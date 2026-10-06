from app.agents.execution_history import (
    ExecutionHistory,
)


def test_record_event():
    history = ExecutionHistory()

    event = history.record(
        tool_name="weather",
        layer_index=0,
        status="success",
    )

    assert event.tool_name == "weather"
    assert event.status == "success"


def test_all_events():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="success",
    )

    history.record(
        tool_name="github",
        layer_index=1,
        status="failed",
        error="API error",
    )

    assert len(history.all_events()) == 2


def test_tool_events():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="success",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
    )

    history.record(
        tool_name="weather",
        layer_index=1,
        status="failed",
    )

    events = history.tool_events("weather")

    assert len(events) == 2
    assert all(
        event.tool_name == "weather"
        for event in events
    )


def test_failed_events():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="success",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
        error="timeout",
    )

    assert len(history.failed_events()) == 1
    assert (
        history.failed_events()[0].tool_name
        == "github"
    )


def test_successful_events():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="success",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
    )

    assert len(history.successful_events()) == 1


def test_to_dict():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        retry_count=2,
        recovery_action="replan",
        error="timeout",
    )

    data = history.to_dict()

    assert data["total_events"] == 1
    assert data["successful"] == 0
    assert data["failed"] == 1

    event = data["events"][0]

    assert event["tool_name"] == "weather"
    assert event["retry_count"] == 2
    assert event["recovery_action"] == "replan"
    assert event["error"] == "timeout"


def test_clear():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="success",
    )

    history.clear()

    assert history.all_events() == ()


def test_recovery_events():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="retry",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    history.record(
        tool_name="news",
        layer_index=0,
        status="failed",
        recovery_action="abort",
    )

    assert len(history.recovery_events()) == 3


def test_replan_count():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    history.record(
        tool_name="github",
        layer_index=1,
        status="failed",
        recovery_action="retry",
    )

    history.record(
        tool_name="news",
        layer_index=2,
        status="failed",
        recovery_action="replan",
    )

    assert history.replan_count == 2


def test_retry_count():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="retry",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
        recovery_action="retry",
    )

    assert history.retry_count == 2


def test_abort_count():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="abort",
    )

    assert history.abort_count == 1


def test_recovery_counts_in_to_dict():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="retry",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    data = history.to_dict()

    assert data["retries"] == 1
    assert data["replans"] == 1
    assert data["aborts"] == 0

def test_tool_recovery_events():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="retry",
    )

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
        recovery_action="retry",
    )

    events = history.tool_recovery_events("weather")

    assert len(events) == 2
    assert all(
        event.tool_name == "weather"
        for event in events
    )


def test_tool_replan_count():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    history.record(
        tool_name="weather",
        layer_index=1,
        status="failed",
        recovery_action="replan",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
        recovery_action="replan",
    )

    assert history.tool_replan_count("weather") == 2
    assert history.tool_replan_count("github") == 1


def test_tool_retry_count():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="retry",
    )

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="retry",
    )

    assert history.tool_retry_count("weather") == 2


def test_tool_abort_count():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="abort",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="failed",
        recovery_action="abort",
    )

    assert history.tool_abort_count("weather") == 1
    assert history.tool_abort_count("github") == 1


def test_tool_recovery_ignores_other_tools():
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

    assert history.tool_replan_count("weather") == 1
    assert history.tool_replan_count("github") == 1

def test_planning_context_summarizes_execution_history():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="retry",
        error="Timeout",
    )

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        recovery_action="replan",
        error="Timeout",
    )

    history.record(
        tool_name="github",
        layer_index=0,
        status="success",
    )

    context = history.planning_context()

    assert context["total_events"] == 3
    assert context["successful"] == 1
    assert context["failed"] == 2
    assert context["retries"] == 1
    assert context["replans"] == 1
    assert context["aborts"] == 0

    assert context["tools"]["weather"] == {
        "attempts": 2,
        "successes": 0,
        "failures": 2,
        "retries": 1,
        "replans": 1,
        "aborts": 0,
        "last_status": "failed",
        "last_recovery_action": "replan",
        "last_error": "Timeout",
    }

    assert context["tools"]["github"] == {
        "attempts": 1,
        "successes": 1,
        "failures": 0,
        "retries": 0,
        "replans": 0,
        "aborts": 0,
        "last_status": "success",
        "last_recovery_action": None,
        "last_error": None,
    }


def test_planning_context_is_empty_for_new_history():
    history = ExecutionHistory()

    context = history.planning_context()

    assert context == {
        "total_events": 0,
        "successful": 0,
        "failed": 0,
        "retries": 0,
        "replans": 0,
        "aborts": 0,
        "tools": {},
    }

from app.agents.execution_history import ExecutionHistory


def test_result_context_exposes_latest_meaningful_tool_result():
    history = ExecutionHistory()

    history.record(
        tool_name="calculator",
        layer_index=0,
        status="success",
        result={"value": 200},
    )

    history.record(
        tool_name="calculator",
        layer_index=0,
        status="failed",
        error="Temporary failure",
    )

    context = history.result_context()

    assert context["calculator"] == {
        "status": "success",
        "result": {"value": 200},
        "error": None,
        "layer_index": 0,
    }


def test_result_context_ignores_tools_without_results():
    history = ExecutionHistory()

    history.record(
        tool_name="weather",
        layer_index=0,
        status="failed",
        error="Timeout",
    )

    assert history.result_context() == {}
