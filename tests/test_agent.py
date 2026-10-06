from app.agents.agent import ThanosAgent
from app.ai.request import RequestType


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
            "research": FakeTool("research"),
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


def test_agent_ignores_unregistered_matching_tool():

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    agent.tool_selector.tool_keywords = {
        "weather": {
            "weather",
        },
        "nonexistent": {
            "secret",
        },
    }

    tools = agent.tool_selector.select(
        "Check the weather and secret information"
    )

    names = {
        tool["function"]["name"]
        for tool in tools
    }

    assert names == {
        "weather",
    }


def test_agent_routes_multi_intent_request():

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "Calculate 25 * 8 and check the latest news"
    )

    decision = agent.ai_router.decide(
        request_type=request.request_type,
        provider=request.provider,
        request_types=request.request_types,
    )

    assert request.request_type == (
        RequestType.RESEARCH
    )

    assert set(request.request_types) == {
        RequestType.CALCULATION,
        RequestType.RESEARCH,
    }

    assert decision.use_tools is True
    assert decision.use_research is True


def test_agent_selects_tools_for_multiple_intents():

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "Calculate 25 * 8 and check the latest news"
    )

    decision = agent.ai_router.decide(
        request_type=request.request_type,
        provider=request.provider,
        request_types=request.request_types,
    )

    tools = agent._select_tools(
        request=request,
        use_tools=decision.use_tools,
        use_research=decision.use_research,
    )

    names = {
        tool["function"]["name"]
        for tool in tools
    }

    assert names == {
        "calculator",
        "research",
    }


def test_agent_preserves_planner_execution_layers():

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "Calculate 25 * 8 and check the latest news"
    )

    plan = agent.planner.create_plan(
        request.user_input,
        request.request_types,
    )

    agent.last_plan = plan

    assert agent.last_plan.execution_layers == (
        ("calculator",),
        ("research",),
    )


def test_execution_layers_run_in_dependency_order():

    from app.agents.planner import (
        ExecutionPlan,
        PlanStep,
    )

    plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="calculator",
                reason="Calculate first",
            ),
            PlanStep(
                tool_name="research",
                reason="Research after calculation",
                depends_on=("calculator",),
            ),
        )
    )

    execution_order = []

    async def execute_layer(layer):

        for tool_name in layer:
            execution_order.append(tool_name)

    async def run():

        for layer in plan.execution_layers:
            await execute_layer(layer)

    import asyncio

    asyncio.run(run())

    assert execution_order == [
        "calculator",
        "research",
    ]

def test_same_execution_layer_can_run_in_parallel():

    import asyncio

    from app.agents.planner import (
        ExecutionPlan,
        PlanStep,
    )

    plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="weather",
                reason="Weather",
            ),
            PlanStep(
                tool_name="news",
                reason="News",
            ),
            PlanStep(
                tool_name="research",
                reason="Research after both",
                depends_on=(
                    "weather",
                    "news",
                ),
            ),
        )
    )

    started = []
    completed = []

    async def execute_tool(tool_name):

        started.append(tool_name)

        await asyncio.sleep(0.01)

        completed.append(tool_name)

    async def run():

        for layer in plan.execution_layers:

            await asyncio.gather(
                *(
                    execute_tool(tool_name)
                    for tool_name in layer
                )
            )

    asyncio.run(run())

    assert plan.execution_layers == (
        ("weather", "news"),
        ("research",),
    )

    assert set(started[:2]) == {
        "weather",
        "news",
    }

    assert completed[:2] in (
        ["weather", "news"],
        ["news", "weather"],
    )

    assert completed[-1] == "research"

def test_agent_executes_tool_calls_by_planner_layers():


    import asyncio

    from app.agents.planner import (
        ExecutionPlan,
        PlanStep,
    )

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    agent.last_plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="weather",
                reason="Weather",
            ),
            PlanStep(
                tool_name="news",
                reason="News",
            ),
            PlanStep(
                tool_name="research",
                reason="Research after weather and news",
                depends_on=(
                    "weather",
                    "news",
                ),
            ),
        )
    )

    execution_order = []

    async def fake_execute_tool_call(tool_call):

        tool_name = (
            tool_call["function"]["name"]
        )

        execution_order.append(
            f"start:{tool_name}"
        )

        await asyncio.sleep(0.01)

        execution_order.append(
            f"end:{tool_name}"
        )

        return {
            "tool_call_id": tool_call["id"],
            "content": tool_name,
        }

    agent._execute_tool_call = (
        fake_execute_tool_call
    )

    tool_calls = [
        {
            "id": "weather-1",
            "function": {
                "name": "weather",
                "arguments": "{}",
            },
        },
        {
            "id": "news-1",
            "function": {
                "name": "news",
                "arguments": "{}",
            },
        },
        {
            "id": "research-1",
            "function": {
                "name": "research",
                "arguments": "{}",
            },
        },
    ]

    results = asyncio.run(
        agent._execute_tool_calls_by_plan(
            tool_calls
        )
    )

    assert execution_order[:2] in (
        [
            "start:weather",
            "start:news",
        ],
        [
            "start:news",
            "start:weather",
        ],
    )

    assert execution_order.index(
        "end:weather"
    ) < execution_order.index(
        "start:research"
    )

    assert execution_order.index(
        "end:news"
    ) < execution_order.index(
        "start:research"
    )

    assert execution_order[-2:] == [
        "start:research",
        "end:research",
    ]

    assert len(results) == 3

def test_dynamic_plan_step_maps_actual_tool_calls_to_same_layer():

    import asyncio

    from app.agents.planner import (
        ExecutionPlan,
        PlanStep,
    )

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    agent.last_plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="dynamic",
                reason="External tools",
            ),
            PlanStep(
                tool_name="research",
                reason="Research after external tools",
                depends_on=("dynamic",),
            ),
        )
    )

    execution_order = []

    async def fake_execute_tool_call(tool_call):

        tool_name = (
            tool_call["function"]["name"]
        )

        execution_order.append(
            f"start:{tool_name}"
        )

        await asyncio.sleep(0.01)

        execution_order.append(
            f"end:{tool_name}"
        )

        return {
            "tool_call_id": tool_call["id"],
            "content": tool_name,
        }

    agent._execute_tool_call = (
        fake_execute_tool_call
    )

    tool_calls = [
        {
            "id": "weather-1",
            "function": {
                "name": "weather",
                "arguments": "{}",
            },
        },
        {
            "id": "github-1",
            "function": {
                "name": "github",
                "arguments": "{}",
            },
        },
        {
            "id": "research-1",
            "function": {
                "name": "research",
                "arguments": "{}",
            },
        },
    ]

    results = asyncio.run(
        agent._execute_tool_calls_by_plan(
            tool_calls
        )
    )

    assert execution_order[:2] in (
        [
            "start:weather",
            "start:github",
        ],
        [
            "start:github",
            "start:weather",
        ],
    )

    assert execution_order.index(
        "end:weather"
    ) < execution_order.index(
        "start:research"
    )

    assert execution_order.index(
        "end:github"
    ) < execution_order.index(
        "start:research"
    )

    assert execution_order[-2:] == [
        "start:research",
        "end:research",
    ]

    assert len(results) == 3


def test_agent_replans_after_tool_failure():
    from app.agents.planner import ExecutionPlan, PlanStep

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "Calculate 25 * 8 and check the latest news"
    )

    agent.last_request = request
    agent.last_plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="calculator",
                reason="Calculate first",
            ),
            PlanStep(
                tool_name="research",
                reason="Research after calculation",
                depends_on=("calculator",),
            ),
        )
    )
    agent.last_execution_state = agent._create_execution_state(
        agent.last_plan
    )

    tools = agent.tool_selector.select(
        request.user_input
    )

    replanned_tools = agent._replan_after_failure(
        user_input=request.user_input,
        tools=tools,
        failed_tool="calculator",
    )

    assert agent.last_plan is not None
    assert all(
        step.tool_name != "calculator"
        for step in agent.last_plan.steps
    )

    assert agent.last_execution_state is not None
    assert agent.last_execution_state.tools

    assert all(
        tool["function"]["name"] != "calculator"
        for tool in replanned_tools
    )


def test_agent_replan_preserves_execution_history():
    from app.agents.execution_history import ExecutionHistory
    from app.agents.planner import ExecutionPlan, PlanStep

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "Calculate 25 * 8 and check the latest news"
    )

    agent.last_request = request
    agent.last_plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="calculator",
                reason="Calculate first",
            ),
            PlanStep(
                tool_name="research",
                reason="Research after calculation",
                depends_on=("calculator",),
            ),
        )
    )

    history = ExecutionHistory()
    history.record(
        tool_name="calculator",
        layer_index=0,
        status="failed",
        recovery_action="replan",
        error="Calculator failed.",
    )

    agent.last_execution_history = history

    agent._replan_after_failure(
        user_input=request.user_input,
        tools=agent.tool_selector.select(
            request.user_input
        ),
        failed_tool="calculator",
    )

    assert agent.last_execution_history is history
    assert agent.last_execution_history.replan_count == 1
    assert agent.last_execution_history.tool_replan_count(
        "calculator"
    ) == 1


def test_agent_replan_removes_failed_dependency():
    from app.agents.planner import ExecutionPlan, PlanStep

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "Calculate 25 * 8 and check the latest news"
    )

    agent.last_request = request
    agent.last_plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="calculator",
                reason="Calculate first",
            ),
            PlanStep(
                tool_name="research",
                reason="Research after calculation",
                depends_on=("calculator",),
            ),
        )
    )

    agent._replan_after_failure(
        user_input=request.user_input,
        tools=agent.tool_selector.select(
            request.user_input
        ),
        failed_tool="calculator",
    )

    assert agent.last_plan is not None

    for step in agent.last_plan.steps:
        assert "calculator" not in step.depends_on

from app.agents.agent import ThanosAgent
from app.agents.execution_history import ExecutionHistory


class FakeTool:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": f"{self.name} tool",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        }


class FakeToolRegistry:
    def __init__(self):
        self.tools = {
            "weather": FakeTool("weather"),
            "github": FakeTool("github"),
            "news": FakeTool("news"),
            "calculator": FakeTool("calculator"),
            "research": FakeTool("research"),
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


class CapturingPlanner:
    def __init__(self):
        self.planning_context = None

    def replan(
        self,
        user_input,
        request_types,
        failed_tool,
        planning_context=None,
    ):
        self.planning_context = planning_context
        from app.agents.planner import ExecutionPlan
        return ExecutionPlan(steps=())


def test_agent_passes_result_context_to_replanner():
    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    request = agent.request_classifier.classify(
        "Calculate 25 * 8 and check the latest news"
    )
    agent.last_request = request

    history = ExecutionHistory()
    history.record(
        tool_name="calculator",
        layer_index=0,
        status="success",
        result={"value": 200},
    )
    agent.last_execution_history = history

    planner = CapturingPlanner()
    agent.planner = planner

    agent._replan_after_failure(
        user_input=request.user_input,
        tools=[],
        failed_tool="calculator",
    )

    assert planner.planning_context is not None
    assert planner.planning_context["results"]["calculator"] == {
        "status": "success",
        "result": {"value": 200},
        "error": None,
        "layer_index": 0,
    }
