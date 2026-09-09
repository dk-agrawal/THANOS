from app.agents.research_tools import (
    ResearchToolSelector,
)


class FakeResearchTool:

    @property
    def name(self):

        return "research"

    @property
    def description(self):

        return "Research information."

    @property
    def parameters(self):

        return {
            "type": "object",
            "properties": {},
        }

    def definition(self):

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class FakeRegistry:

    def __init__(self):

        self.tools = {
            "research": FakeResearchTool()
        }

    def get(self, name):

        return self.tools.get(name)


def test_selects_research_tool():

    registry = FakeRegistry()

    selector = ResearchToolSelector(
        registry
    )

    tools = selector.select()

    assert len(tools) == 1

    assert (
        tools[0]["function"]["name"]
        == "research"
    )


def test_missing_research_tool_is_rejected():

    class EmptyRegistry:

        def get(self, name):

            return None

    selector = ResearchToolSelector(
        EmptyRegistry()
    )

    try:

        selector.select()

        assert False

    except RuntimeError as error:

        assert str(error) == (
            "Research tool is not registered"
        )