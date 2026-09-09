import asyncio

from app.tools.executor import ToolExecutor
from app.agents.query import ResearchQueryAnalyzer
from app.agents.scoring import SourceScorer
from app.agents.result_scoring import ResearchResultScorer
from app.agents.quality import ResearchQualityGate


class ResearchEngine:

    def __init__(
        self,
        executor: ToolExecutor,
    ):
        self.executor = executor
        self.query_analyzer = ResearchQueryAnalyzer()
        self.source_scorer = SourceScorer()
        self.result_scorer = ResearchResultScorer()
        self.quality_gate = ResearchQualityGate()

    async def search_news(
        self,
        query: str,
        freshness_required: bool = False,
    ) -> dict:

        arguments = {
            "query": query,
        }

        if freshness_required:
            arguments["from_date"] = (
                self._recent_news_date()
            )

        result = await self.executor.execute(
            tool_name="news_search",
            arguments=arguments,
        )

        return result.to_dict()

    async def search_github(
        self,
        query: str,
    ) -> dict:

        result = await self.executor.execute(
            tool_name="github_search",
            arguments={
                "query": query,
            },
        )

        return result.to_dict()

    @staticmethod
    def _recent_news_date(
        days: int = 7,
    ) -> str:

        from app.api.news import NewsProvider

        return NewsProvider.recent_date(
            days
        )

    async def research_and_synthesize(
        self,
        query: str,
        synthesizer,
    ) -> str:

        research_data = await self.research(
            query
        )

        quality = research_data.get(
            "quality",
            {},
        )

        if not quality.get("passed", False):

            return (
                "THANOS could not find enough "
                "reliable research data to provide "
                "a confident answer. "
                f"Reason: {quality.get('reason', 'Unknown')}"
            )

        return await synthesizer.synthesize(
            query=query,
            research_data=research_data,
        )

    def _score_news_results(
        self,
        source_result: dict,
        freshness_required: bool = False,
    ) -> list[dict]:

        articles = (
            source_result
            .get("data", {})
            .get("articles", [])
        )

        scored = []

        for article in articles:

            score = self.result_scorer.score_news_article(
                article,
                freshness_required=freshness_required,
            )

            scored.append({
                "result": article,
                "score": {
                    "value": score.score,
                    "reason": score.reason,
                },
            })

        return scored

    def _score_github_results(
        self,
        source_result: dict,
    ) -> list[dict]:

        repositories = (
            source_result
            .get("data", {})
            .get("repositories", [])
        )

        scored = []

        for repository in repositories:

            score = self.result_scorer.score_github_repository(
                repository
            )

            scored.append({
                "result": repository,
                "score": {
                    "value": score.score,
                    "reason": score.reason,
                },
            })

        return scored

    def _rank_items(
        self,
        items: list[dict],
        limit: int = 5,
    ) -> list[dict]:

        return sorted(
            items,
            key=lambda item: item.get(
                "score",
                {},
            ).get(
                "value",
                0,
            ),
            reverse=True,
        )[:limit]

    async def research(
        self,
        query: str,
    ) -> dict:

        research_query = self.query_analyzer.analyze(
            query
        )

        tasks = {}

        if "news" in research_query.sources:

            tasks["news"] = self.search_news(
                research_query.cleaned,
                freshness_required=(
                    research_query.freshness
                ),
            )

        if "github" in research_query.sources:

            tasks["github"] = self.search_github(
                research_query.cleaned
            )

        results = {}

        if tasks:

            completed = await asyncio.gather(
                *tasks.values(),
                return_exceptions=True,
            )

            for source, result in zip(
                tasks.keys(),
                completed,
            ):

                if isinstance(
                    result,
                    Exception,
                ):

                    source_result = {
                        "success": False,
                        "error": str(result),
                    }

                else:

                    source_result = result

                source_score = self.source_scorer.score(
                    source,
                    source_result,
                )

                results[source] = {
                    "result": source_result,
                    "score": {
                        "value": source_score.score,
                        "reason": source_score.reason,
                    },
                }

                if (
                    source == "news"
                    and source_result.get("success")
                ):

                    items = self._score_news_results(
                        source_result,
                        freshness_required=(
                            research_query.freshness
                        ),
                    )

                    results[source]["items"] = (
                        self._rank_items(
                            items
                        )
                    )

                elif (
                    source == "github"
                    and source_result.get("success")
                ):

                    items = self._score_github_results(
                        source_result
                    )

                    results[source]["items"] = (
                        self._rank_items(
                            items
                        )
                    )

        research_data = {
            "query": research_query.original,
            "cleaned_query": research_query.cleaned,
            "freshness_required": research_query.freshness,
            "sources_requested": research_query.sources,
            "sources": results,
        }

        quality = self.quality_gate.validate(
            research_data
        )

        research_data["quality"] = quality

        return research_data
