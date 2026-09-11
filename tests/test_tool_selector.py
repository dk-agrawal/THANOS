from app.agents.tool_selector import (
    IntelligentToolSelector,
)


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


class FakeRegistry:

    def __init__(self):

        self.tools = {
            "weather": FakeTool("weather"),
            "github": FakeTool("github"),
            "news": FakeTool("news"),
            "calculator": FakeTool("calculator"),
        }

    def get(self, name):

        return self.tools.get(name)


def test_selects_weather_tool():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "What's the weather today?"
    )

    assert len(tools) == 1
    assert (
        tools[0]["function"]["name"]
        == "weather"
    )


def test_selects_weather_from_forecast():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "What's the forecast for tomorrow?"
    )

    assert len(tools) == 1
    assert (
        tools[0]["function"]["name"]
        == "weather"
    )


def test_selects_weather_from_rain_request():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "Will it rain today?"
    )

    assert len(tools) == 1
    assert (
        tools[0]["function"]["name"]
        == "weather"
    )


def test_selects_github_tool():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "Check this repository"
    )

    assert len(tools) == 1
    assert (
        tools[0]["function"]["name"]
        == "github"
    )


def test_selects_github_from_pull_request():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "Show me the pull requests"
    )

    assert len(tools) == 1
    assert (
        tools[0]["function"]["name"]
        == "github"
    )


def test_selects_news_tool():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "Show me the latest news"
    )

    assert len(tools) == 1
    assert (
        tools[0]["function"]["name"]
        == "news"
    )


def test_selects_news_from_current_events():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "What's happening in the world?"
    )

    assert len(tools) == 1
    assert (
        tools[0]["function"]["name"]
        == "news"
    )


def test_selects_calculator_tool():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "Solve this equation"
    )

    assert len(tools) == 1
    assert (
        tools[0]["function"]["name"]
        == "calculator"
    )


def test_can_select_multiple_tools():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
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


def test_unknown_request_returns_no_tools():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select(
        "Tell me a funny story"
    )

    assert tools == []


def test_empty_input_returns_no_tools():

    selector = IntelligentToolSelector(
        FakeRegistry()
    )

    tools = selector.select("   ")

    assert tools == []