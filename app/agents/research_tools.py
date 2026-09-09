from app.tools.registry import ToolRegistry


class ResearchToolSelector:

    def __init__(
        self,
        tool_registry: ToolRegistry,
    ):
        self.tool_registry = tool_registry

    def select(self) -> list[dict]:

        research_tool = (
            self.tool_registry.get(
                "research"
            )
        )

        if research_tool is None:
            raise RuntimeError(
                "Research tool is not registered"
            )

        return [
            research_tool.definition()
        ]