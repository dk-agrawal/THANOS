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
    ):
        self.tool_registry = tool_registry

        self.scorer = (
            scorer
            or ToolRelevanceScorer()
        )

    def select(
        self,
        user_input: str,
    ) -> list[dict]:

        text = user_input.strip().lower()

        if not text:
            return []

        relevant_tools = self.scorer.relevant(
            user_input=text,
            tool_keywords=self.TOOL_KEYWORDS,
            minimum_score=1,
        )

        tools = []

        for result in relevant_tools:

            tool = self.tool_registry.get(
                result.tool_name
            )

            if tool is not None:
                tools.append(
                    tool.definition()
                )

        return tools