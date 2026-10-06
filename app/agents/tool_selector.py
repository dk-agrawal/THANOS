import re

from app.tools.registry import ToolRegistry
from app.agents.tool_scoring import ToolRelevanceScorer


class IntelligentToolSelector:

    TOOL_KEYWORDS = {
        "weather": {
            "weather",
            "temperature",
            "forecast",
            "rain",
            "raining",
            "rainfall",
            "climate",
            "hot",
            "cold",
            "humidity",
            "wind",
        },
        "github": {
            "github",
            "repository",
            "repo",
            "commit",
            "pull request",
            "pull requests",
            "pr",
            "issue",
            "issues",
            "branch",
            "branches",
        },
        "news": {
            "news",
            "headlines",
            "breaking news",
            "latest news",
            "current events",
            "happening",
        },
        "calculator": {
            "calculate",
            "calculation",
            "compute",
            "solve",
            "math",
            "equation",
        },
        "remember": {
            "remember",
            "memorize",
            "save this",
            "store this",
        },
        "recall": {
            "recall",
            "what do you remember",
            "remember what",
        },
        "forget": {
            "forget",
            "remove memory",
            "delete memory",
        },
        "system_info": {
            "system info",
            "system information",
            "computer information",
            "pc information",
            "computer specs",
            "pc specs",
        },
    }

    def __init__(
        self,
        tool_registry: ToolRegistry,
        scorer: ToolRelevanceScorer | None = None,
        tool_keywords: dict[str, set[str]] | None = None,
    ):
        self.tool_registry = tool_registry

        self.scorer = scorer or ToolRelevanceScorer()

        self.tool_keywords = (
            tool_keywords
            or {
                name: set(keywords)
                for name, keywords in self.TOOL_KEYWORDS.items()
            }
        )

    @staticmethod
    def _keyword_matches(
        text: str,
        keyword: str,
    ) -> bool:
        keyword = keyword.strip().lower()

        if not keyword:
            return False

        # Multi-word keywords are matched as phrases.
        if " " in keyword:
            return keyword in text

        # Single-word keywords must match complete words.
        return re.search(
            rf"\b{re.escape(keyword)}\b",
            text,
        ) is not None

    def _direct_matches(
        self,
        text: str,
    ) -> list[str]:
        matches = []

        for tool_name, keywords in self.tool_keywords.items():

            for keyword in keywords:

                if self._keyword_matches(
                    text,
                    keyword,
                ):
                    matches.append(tool_name)
                    break

        return matches

    def select(
        self,
        user_input: str,
    ) -> list[dict]:

        text = user_input.strip().lower()

        if not text:
            return []

        selected_names = []

        # First use deterministic keyword matching.
        #
        # This guarantees that an obvious request such as
        # "weather forecast" selects weather directly,
        # without depending on the scoring implementation.
        direct_matches = self._direct_matches(text)

        for tool_name in direct_matches:

            if tool_name not in selected_names:
                selected_names.append(tool_name)

        # Then use the relevance scorer as an additional
        # intelligence layer.
        #
        # Scoring is allowed to discover additional tools,
        # but it must never remove a deterministic match.
        try:
            relevant_tools = self.scorer.relevant(
                user_input=text,
                tool_keywords=self.tool_keywords,
                minimum_score=1,
            )
        except Exception:
            relevant_tools = []

        for result in relevant_tools:

            tool_name = result.tool_name

            if tool_name not in selected_names:
                selected_names.append(tool_name)

        tools = []

        for tool_name in selected_names:

            tool = self.tool_registry.get(
                tool_name
            )

            # Never return a tool that is not actually
            # registered in the active ToolRegistry.
            if tool is not None:
                tools.append(
                    tool.definition()
                )

        return tools