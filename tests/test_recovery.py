from app.agents.recovery import (
    RecoveryAction,
    RecoveryEngine,
)
from app.tools.result import ToolResult


def test_success_returns_continue():
    engine = RecoveryEngine()

    decision = engine.decide(
        tool_name="weather",
        result=ToolResult(
            success=True,
            data={"temperature": 25},
        ),
    )

    assert decision.action == RecoveryAction.CONTINUE
    assert decision.tool_name == "weather"


def test_failure_with_retry_budget_returns_retry():
    engine = RecoveryEngine()

    decision = engine.decide(
        tool_name="weather",
        result=ToolResult(
            success=False,
            error="Temporary timeout",
        ),
        retry_count=0,
        max_retries=2,
    )

    assert decision.action == RecoveryAction.RETRY


def test_failure_after_retry_budget_returns_replan():
    engine = RecoveryEngine()

    decision = engine.decide(
        tool_name="weather",
        result=ToolResult(
            success=False,
            error="API unavailable",
        ),
        retry_count=2,
        max_retries=2,
    )

    assert decision.action == RecoveryAction.REPLAN


def test_repeated_failure_after_replan_returns_abort():
    engine = RecoveryEngine()

    decision = engine.decide(
        tool_name="weather",
        result=ToolResult(
            success=False,
            error="API unavailable",
        ),
        retry_count=2,
        max_retries=2,
        previous_replans=1,
    )

    assert decision.action == RecoveryAction.ABORT
    assert decision.tool_name == "weather"
    assert "execution loop" in decision.reason


def test_multiple_previous_replans_return_abort():
    engine = RecoveryEngine()

    decision = engine.decide(
        tool_name="github",
        result=ToolResult(
            success=False,
            error="rate limited",
        ),
        retry_count=2,
        max_retries=2,
        previous_replans=3,
    )

    assert decision.action == RecoveryAction.ABORT


def test_negative_retry_count_rejected():
    engine = RecoveryEngine()

    try:
        engine.decide(
            tool_name="weather",
            result=ToolResult(
                success=False,
                error="timeout",
            ),
            retry_count=-1,
        )
        assert False
    except ValueError as error:
        assert "negative" in str(error)


def test_negative_replan_count_rejected():
    engine = RecoveryEngine()

    try:
        engine.decide(
            tool_name="weather",
            result=ToolResult(
                success=False,
                error="timeout",
            ),
            previous_replans=-1,
        )
        assert False
    except ValueError as error:
        assert "negative" in str(error)


def test_recover_preserves_success():
    engine = RecoveryEngine()

    result = ToolResult(
        success=True,
        data={"value": 42},
    )

    recovered = engine.recover(
        tool_name="calculator",
        result=result,
    )

    assert recovered is result


def test_recover_wraps_failure():
    engine = RecoveryEngine()

    result = ToolResult(
        success=False,
        error="Calculation failed",
    )

    recovered = engine.recover(
        tool_name="calculator",
        result=result,
    )

    assert recovered.success is False
    assert "calculator" in recovered.error
    assert "Calculation failed" in recovered.error


def test_decision_to_dict():
    engine = RecoveryEngine()

    decision = engine.decide(
        tool_name="github",
        result=ToolResult(
            success=False,
            error="Rate limited",
        ),
        retry_count=0,
        max_retries=1,
    )

    data = decision.to_dict()

    assert data["action"] == "retry"
    assert data["tool_name"] == "github"
    assert "Rate limited" in data["reason"]


from app.agents.execution_history import ExecutionHistory

def test_history_controls_replan_decision():
    engine = RecoveryEngine()
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    decision = engine.decide(
        tool_name="weather",
        result=ToolResult(
            success=False,
            error="API unavailable",
        ),
        retry_count=2,
        max_retries=2,
        history=history,
    )

    assert decision.action == RecoveryAction.ABORT


def test_history_without_replan_allows_replan():
    engine = RecoveryEngine()
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="retry",
    )

    decision = engine.decide(
        tool_name="weather",
        result=ToolResult(
            success=False,
            error="API unavailable",
        ),
        retry_count=2,
        max_retries=2,
        history=history,
    )

    assert decision.action == RecoveryAction.REPLAN


def test_no_history_preserves_replan_behavior():
    engine = RecoveryEngine()

    decision = engine.decide(
        tool_name="weather",
        result=ToolResult(
            success=False,
            error="API unavailable",
        ),
        retry_count=2,
        max_retries=2,
    )

    assert decision.action == RecoveryAction.REPLAN