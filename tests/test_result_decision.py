from app.agents.result_decision import (
    ResultDecision,
    ResultDecisionAction,
    ResultDecisionEngine,
)


def test_successful_result_should_continue():
    engine = ResultDecisionEngine()

    decision = engine.decide(
        tool_name="weather",
        success=True,
        result={"temperature": 25},
    )

    assert decision == ResultDecision(
        action=ResultDecisionAction.CONTINUE,
        tool_name="weather",
        reason="Tool produced a usable result.",
    )


def test_failed_result_should_recover():
    engine = ResultDecisionEngine()

    decision = engine.decide(
        tool_name="weather",
        success=False,
        result=None,
        error="Timeout",
    )

    assert decision == ResultDecision(
        action=ResultDecisionAction.RECOVER,
        tool_name="weather",
        reason="Tool did not produce a usable result.",
    )


def test_missing_result_should_not_continue():
    engine = ResultDecisionEngine()

    decision = engine.decide(
        tool_name="weather",
        success=True,
        result=None,
    )

    assert decision == ResultDecision(
        action=ResultDecisionAction.INSUFFICIENT,
        tool_name="weather",
        reason="Tool succeeded but produced no usable result.",
    )


def test_empty_tool_name_is_rejected():
    engine = ResultDecisionEngine()

    try:
        engine.decide(
            tool_name="",
            success=True,
            result={"temperature": 25},
        )
    except ValueError as exc:
        assert str(exc) == "Tool name cannot be empty."
    else:
        raise AssertionError(
            "Expected ValueError for empty tool name."
        )

def test_result_decision_uses_actual_tool_result():
    engine = ResultDecisionEngine()

    tool_result = {
        "temperature": 28,
        "condition": "clear",
    }

    decision = engine.decide(
        tool_name="weather",
        success=True,
        result=tool_result,
    )

    assert decision.action == ResultDecisionAction.CONTINUE
    assert decision.tool_name == "weather"


def test_result_decision_recovers_from_actual_tool_failure():
    engine = ResultDecisionEngine()

    decision = engine.decide(
        tool_name="github",
        success=False,
        result=None,
        error="GitHub API timeout",
    )

    assert decision.action == ResultDecisionAction.RECOVER
    assert decision.tool_name == "github"

def test_result_decision_can_classify_tool_execution_payload():
    engine = ResultDecisionEngine()

    payload = {
        "success": True,
        "data": {
            "temperature": 28,
            "condition": "clear",
        },
        "error": None,
    }

    decision = engine.decide(
        tool_name="weather",
        success=payload["success"],
        result=payload["data"],
        error=payload["error"],
    )

    assert decision.action == ResultDecisionAction.CONTINUE
    assert decision.tool_name == "weather"
    assert decision.reason == "Tool produced a usable result."

def test_agent_result_decision_classifies_tool_result():
    from app.agents.agent import ThanosAgent
    from app.agents.result_decision import (
        ResultDecisionAction,
    )
    from tests.test_agent import (
        FakeAIRegistry,
        FakeToolRegistry,
    )

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    decision = agent.result_decision_engine.decide(
        tool_name="weather",
        success=True,
        result={
            "temperature": 28,
            "condition": "clear",
        },
    )

    assert decision.action == ResultDecisionAction.CONTINUE
    assert decision.tool_name == "weather"

def test_agent_tool_execution_uses_result_decision_engine():
    import asyncio

    from app.agents.agent import ThanosAgent
    from app.agents.result_decision import (
        ResultDecisionAction,
    )
    from app.tools.result import ToolResult
    from tests.test_agent import (
        FakeAIRegistry,
        FakeToolRegistry,
    )

    agent = ThanosAgent(
        ai_registry=FakeAIRegistry(),
        tool_registry=FakeToolRegistry(),
    )

    calls = []

    original_decide = (
        agent.result_decision_engine.decide
    )

    def tracking_decide(
        tool_name,
        success,
        result=None,
        error=None,
    ):
        calls.append(
            {
                "tool_name": tool_name,
                "success": success,
                "result": result,
                "error": error,
            }
        )

        return original_decide(
            tool_name=tool_name,
            success=success,
            result=result,
            error=error,
        )

    agent.result_decision_engine.decide = (
        tracking_decide
    )

    async def fake_execute_once(
        tool_name,
        arguments,
    ):
        return ToolResult(
            success=True,
            data={
                "temperature": 28,
            },
        )

    agent.tool_executor.execute_once = (
        fake_execute_once
    )

    tool_call = {
        "id": "weather-1",
        "function": {
            "name": "weather",
            "arguments": "{}",
        },
    }

    asyncio.run(
        agent._execute_tool_call(
            tool_call
        )
    )

    assert calls == [
        {
            "tool_name": "weather",
            "success": True,
            "result": {
                "temperature": 28,
            },
            "error": None,
        }
    ]

    decision = original_decide(
        tool_name=calls[0]["tool_name"],
        success=calls[0]["success"],
        result=calls[0]["result"],
        error=calls[0]["error"],
    )

    assert decision.action == (
        ResultDecisionAction.CONTINUE
    )