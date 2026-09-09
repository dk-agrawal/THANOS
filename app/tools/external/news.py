from app.api.news import NewsProvider
from app.tools.base import Tool
from app.tools.result import ToolResult


class NewsTool(Tool):

    def __init__(self, api_registry):
        self.provider = api_registry.get("news")

    @property
    def name(self) -> str:
        return "news_search"

    @property
    def description(self) -> str:
        return (
            "Searches news articles for a given topic "
            "or keyword."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Topic or keyword to search "
                        "in news articles."
                    ),
                }
            },
            "required": ["query"],
        }

    async def execute(
        self,
        query: str,
    ) -> ToolResult:

        try:
            result = await self.provider.search(
                query=query,
                page_size=5,
            )

            articles = result.get(
                "articles",
                [],
            )

            simplified_articles = []

            for article in articles:
                simplified_articles.append(
                    {
                        "source": article.get(
                            "source",
                            {},
                        ).get("name"),
                        "title": article.get("title"),
                        "description": article.get(
                            "description"
                        ),
                        "url": article.get("url"),
                        "published_at": article.get(
                            "publishedAt"
                        ),
                    }
                )

            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "total_results": result.get(
                        "totalResults",
                        0,
                    ),
                    "articles": simplified_articles,
                },
            )

        except Exception as error:

            return ToolResult(
                success=False,
                error=f"News search failed: {error}",
            )