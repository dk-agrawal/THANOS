from app.tools.registry import ToolRegistry


class IntelligentToolSelector:

    TOOL_KEYWORDS = {
        "weather": {"weather"},
        "github": {
            "github",
            "repository",
            "repo",
            "commit",
            "pull request",
            "issue",
        },
        "news": {
            "news",
            "headlines",
            "breaking news",
        },
        "calculator": {
            "calculate",
            "calculation",
            "compute",
            "solve",
        },
        "remember": {
            "remember",
            "memorize",
        },
        "recall": {
            "recall",
            "remember what",
        },
        "forget": {
            "forget",
            "remove memory",
        },
        "system_info": {
            "system info",
            "system information",
            "computer information",
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

            if any(
                keyword in text
                for keyword in keywords
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