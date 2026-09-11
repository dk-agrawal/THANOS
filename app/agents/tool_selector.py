from app.tools.registry import ToolRegistry


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
    ):
        self.tool_registry = tool_registry

    def select(
        self,
        user_input: str,
    ) -> list[dict]:

        text = user_input.strip().lower()

        if not text:
            return []

        selected_names = []

        for tool_name, keywords in (
            self.TOOL_KEYWORDS.items()
        ):

            if self._matches(
                text,
                keywords,
            ):
                selected_names.append(
                    tool_name
                )

        tools = []

        for tool_name in selected_names:

            tool = self.tool_registry.get(
                tool_name
            )

            if tool is not None:
                tools.append(
                    tool.definition()
                )

        return tools

    @staticmethod
    def _matches(
        text: str,
        keywords: set[str],
    ) -> bool:

        return any(
            IntelligentToolSelector._keyword_matches(
                text,
                keyword,
            )
            for keyword in keywords
        )

    @staticmethod
    def _keyword_matches(
        text: str,
        keyword: str,
    ) -> bool:

        return keyword in text