from app.agents.execution_state import (
    ExecutionState,
    ExecutionStatus,
)


def test_execution_state_registers_tool():

    state = ExecutionState()

    tool_state = state.register(
        tool_name="weather",
        layer_index=0,
    )

    assert tool_state.tool_name == "weather"
    assert tool_state.layer_index == 0
    assert tool_state.status == ExecutionStatus.PENDING


def test_execution_state_tracks_success():

    state = ExecutionState()

    state.register(
        tool_name="weather",
        layer_index=0,
    )

    state.start("weather")
    state.succeed("weather")

    tool_state = state.get("weather")

    assert tool_state is not None
    assert tool_state.status == ExecutionStatus.SUCCESS
    assert tool_state.error is None


def test_execution_state_tracks_failure():

    state = ExecutionState()

    state.register(
        tool_name="github",
        layer_index=1,
    )

    state.start("github")
    state.fail(
        "github",
        "GitHub API failed",
    )

    tool_state = state.get("github")

    assert tool_state is not None
    assert tool_state.status == ExecutionStatus.FAILED
    assert tool_state.error == "GitHub API failed"


def test_execution_state_tracks_pending_tools():

    state = ExecutionState()

    state.register(
        tool_name="weather",
        layer_index=0,
    )

    state.register(
        tool_name="research",
        layer_index=1,
    )

    state.start("weather")
    state.succeed("weather")

    assert state.completed_tools() == (
        "weather",
    )

    assert state.pending_tools() == (
        "research",
    )

    assert state.failed_tools() == ()


def test_execution_state_is_complete_after_success():

    state = ExecutionState()

    state.register(
        tool_name="weather",
        layer_index=0,
    )

    state.start("weather")
    state.succeed("weather")

    assert state.is_complete() is True


def test_execution_state_is_complete_after_failure():

    state = ExecutionState()

    state.register(
        tool_name="weather",
        layer_index=0,
    )

    state.start("weather")
    state.fail(
        "weather",
        "Network error",
    )

    assert state.is_complete() is True


def test_execution_state_is_not_complete_with_pending_tools():

    state = ExecutionState()

    state.register(
        tool_name="weather",
        layer_index=0,
    )

    state.register(
        tool_name="research",
        layer_index=1,
    )

    state.start("weather")
    state.succeed("weather")

    assert state.is_complete() is False


def test_execution_state_to_dict_contains_execution_summary():

    state = ExecutionState()

    state.register(
        tool_name="weather",
        layer_index=0,
    )

    state.register(
        tool_name="github",
        layer_index=0,
    )

    state.start("weather")
    state.succeed("weather")

    state.start("github")
    state.fail(
        "github",
        "API unavailable",
    )

    result = state.to_dict()

    assert result["complete"] is True

    assert result["completed"] == [
        "weather",
    ]

    assert result["failed"] == [
        "github",
    ]

    assert result["pending"] == []

    assert (
        result["tools"]["weather"]["status"]
        == "success"
    )

    assert (
        result["tools"]["github"]["status"]
        == "failed"
    )

    assert (
        result["tools"]["github"]["error"]
        == "API unavailable"
    )


def test_execution_state_rejects_duplicate_tool():

    state = ExecutionState()

    state.register(
        tool_name="weather",
        layer_index=0,
    )

    try:
        state.register(
            tool_name="weather",
            layer_index=1,
        )
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "already registered" in str(error)


def test_execution_state_rejects_unknown_tool():

    state = ExecutionState()

    try:
        state.start("weather")
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "not registered" in str(error)