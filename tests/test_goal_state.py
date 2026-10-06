from app.agents.goal_state import (
    GoalState,
    GoalStateAction,
)


def test_empty_goal_state_is_not_achieved():

    state = GoalState(
        goal="Get weather and news",
    )

    assert (
        state.action
        == GoalStateAction.NOT_ACHIEVED
    )

    assert state.is_complete is False


def test_all_results_achieved():

    state = GoalState(
        goal="Get weather and news",
    )

    state.add_result(
        tool_name="weather",
        action=GoalStateAction.ACHIEVED,
        reason="Weather information retrieved.",
    )

    state.add_result(
        tool_name="news",
        action=GoalStateAction.ACHIEVED,
        reason="News information retrieved.",
    )

    assert (
        state.action
        == GoalStateAction.ACHIEVED
    )

    assert state.is_complete is True


def test_achieved_and_failed_is_partial():

    state = GoalState(
        goal="Get weather and news",
    )

    state.add_result(
        tool_name="weather",
        action=GoalStateAction.ACHIEVED,
        reason="Weather information retrieved.",
    )

    state.add_result(
        tool_name="news",
        action=GoalStateAction.NOT_ACHIEVED,
        reason="News tool failed.",
    )

    assert (
        state.action
        == GoalStateAction.PARTIAL
    )

    assert state.is_complete is False


def test_all_results_failed():

    state = GoalState(
        goal="Get weather and news",
    )

    state.add_result(
        tool_name="weather",
        action=GoalStateAction.NOT_ACHIEVED,
        reason="Weather tool failed.",
    )

    state.add_result(
        tool_name="news",
        action=GoalStateAction.NOT_ACHIEVED,
        reason="News tool failed.",
    )

    assert (
        state.action
        == GoalStateAction.NOT_ACHIEVED
    )

    assert state.is_complete is False


def test_partial_result_makes_goal_partial():

    state = GoalState(
        goal="Get complete weather information",
    )

    state.add_result(
        tool_name="weather",
        action=GoalStateAction.PARTIAL,
        reason="Humidity information is missing.",
    )

    assert (
        state.action
        == GoalStateAction.PARTIAL
    )


def test_partial_with_achieved_remains_partial():

    state = GoalState(
        goal="Get weather and news",
    )

    state.add_result(
        tool_name="weather",
        action=GoalStateAction.ACHIEVED,
        reason="Weather retrieved.",
    )

    state.add_result(
        tool_name="news",
        action=GoalStateAction.PARTIAL,
        reason="Only some news results retrieved.",
    )

    assert (
        state.action
        == GoalStateAction.PARTIAL
    )


def test_empty_tool_name_is_rejected():

    state = GoalState(
        goal="Get weather",
    )

    try:
        state.add_result(
            tool_name="",
            action=GoalStateAction.ACHIEVED,
            reason="Weather retrieved.",
        )
    except ValueError as error:
        assert str(error) == "Tool name cannot be empty."
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_empty_reason_is_rejected():

    state = GoalState(
        goal="Get weather",
    )

    try:
        state.add_result(
            tool_name="weather",
            action=GoalStateAction.ACHIEVED,
            reason="",
        )
    except ValueError as error:
        assert str(error) == "Reason cannot be empty."
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_goal_state_can_be_serialized():

    state = GoalState(
        goal="Get weather",
    )

    state.add_result(
        tool_name="weather",
        action=GoalStateAction.ACHIEVED,
        reason="Weather retrieved.",
    )

    payload = state.to_dict()

    assert payload == {
        "goal": "Get weather",
        "action": "achieved",
        "is_complete": True,
        "results": [
            {
                "tool_name": "weather",
                "action": "achieved",
                "reason": "Weather retrieved.",
            }
        ],
    }