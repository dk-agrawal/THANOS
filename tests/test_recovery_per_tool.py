from app.agents.execution_history import ExecutionHistory
from app.agents.recovery import RecoveryAction, RecoveryEngine
from app.tools.result import ToolResult


def test_recovery_uses_replan_count_for_specific_tool():
    engine = RecoveryEngine()
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    result = ToolResult(
        success=False,
        error="Weather failed again.",
    )

    decision = engine.decide(
        tool_name="weather",
        result=result,
        retry_count=2,
        max_retries=2,
        history=history,
    )

    assert decision.action == RecoveryAction.ABORT


def test_recovery_does_not_block_unrelated_tool():
    engine = RecoveryEngine()
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    result = ToolResult(
        success=False,
        error="GitHub failed.",
    )

    decision = engine.decide(
        tool_name="github",
        result=result,
        retry_count=2,
        max_retries=2,
        history=history,
    )

    assert decision.action == RecoveryAction.REPLAN


def test_recovery_allows_first_replan_for_tool():
    engine = RecoveryEngine()
    history = ExecutionHistory()

    result = ToolResult(
        success=False,
        error="News failed.",
    )

    decision = engine.decide(
        tool_name="news",
        result=result,
        retry_count=2,
        max_retries=2,
        history=history,
    )

    assert decision.action == RecoveryAction.REPLAN


def test_recovery_aborts_only_repeatedly_replanned_tool():
    engine = RecoveryEngine()
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    weather_result = ToolResult(
        success=False,
        error="Weather failed again.",
    )

    github_result = ToolResult(
        success=False,
        error="GitHub failed again.",
    )

    weather_decision = engine.decide(
        tool_name="weather",
        result=weather_result,
        retry_count=2,
        max_retries=2,
        history=history,
    )

    github_decision = engine.decide(
        tool_name="github",
        result=github_result,
        retry_count=2,
        max_retries=2,
        history=history,
    )

    assert weather_decision.action == RecoveryAction.ABORT
    assert github_decision.action == RecoveryAction.ABORT


def test_legacy_previous_replans_still_works_without_history():
    engine = RecoveryEngine()

    result = ToolResult(
        success=False,
        error="Tool failed.",
    )

    decision = engine.decide(
        tool_name="weather",
        result=result,
        retry_count=2,
        max_retries=2,
        previous_replans=1,
    )

    assert decision.action == RecoveryAction.ABORT