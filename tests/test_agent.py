from app.agents.agent import ThanosAgent


class FakeTool:

    def __init__(
        self,
        name: str,
    ):
        self._name = name

    @property
    def name(self):

        return self._name

    @property
    def description(self):

        return f"{self._name} tool"

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


class FakeToolRegistry:

    def __init__(self):

        self.tools = {
            "weather": FakeTool("weather"),
            "github": FakeTool("github"),
            "news": FakeTool("news"),
            "calculator": FakeTool("calculator"),
        }

    def get(self, name):

        return self.tools.get(name)

    def definitions(self):

        return [
            tool.definition()
            for tool in self.tools.values()
        ]


class FakeAIRegistry:

    def has(self, name):

        return name == "openrouter"

    def get(self, name):

        return None


def test_agent_selects_weather_tool():

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "What's the weather forecast?"
    )

    tools = agent._select_tools(
        request=request,
        use_tools=True,
        use_research=False,
    )

    assert len(tools) == 1

    assert (
        tools[0]["function"]["name"]
        == "weather"
    )


def test_agent_selects_multiple_relevant_tools():

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    tools = agent.tool_selector.select(
        "Calculate something and check the latest news"
    )

    names = {
        tool["function"]["name"]
        for tool in tools
    }

    assert names == {
        "calculator",
        "news",
    }


def test_agent_returns_no_tools_when_tools_disabled():

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "What's the weather?"
    )

    tools = agent._select_tools(
        request=request,
        use_tools=False,
        use_research=False,
    )

    assert tools == []