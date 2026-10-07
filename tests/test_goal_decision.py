from app.agents.goal_decision import (
    GoalDecisionAction,
    GoalDecisionEngine,
)
from app.agents.goal_state import GoalStateAction


def test_achieved_goal_means_complete():

    engine = GoalDecisionEngine()

    decision = engine.decide(
        GoalStateAction.ACHIEVED
    )

    assert (
        decision.action
        == GoalDecisionAction.COMPLETE
    )

    assert (
        decision.reason
        == "The overall goal has been achieved."
    )


def test_partial_goal_means_continue():

    engine = GoalDecisionEngine()

    decision = engine.decide(
        GoalStateAction.PARTIAL
    )

    assert (
        decision.action
        == GoalDecisionAction.CONTINUE
    )

    assert (
        "continue execution"
        in decision.reason
    )


def test_unachieved_goal_means_replan():

    engine = GoalDecisionEngine()

    decision = engine.decide(
        GoalStateAction.NOT_ACHIEVED
    )

    assert (
        decision.action
        == GoalDecisionAction.REPLAN
    )

    assert (
        "reconsider"
        in decision.reason
    )


def test_invalid_goal_action_is_rejected():

    engine = GoalDecisionEngine()

    try:
        engine.decide("invalid")
    except ValueError as error:
        assert str(error) == (
            "Invalid goal state action."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_complete_decision_can_be_serialized():

    engine = GoalDecisionEngine()

    decision = engine.decide(
        GoalStateAction.ACHIEVED
    )

    payload = decision.to_dict()

    assert payload == {
        "action": "complete",
        "reason": (
            "The overall goal has been "
            "achieved."
        ),
    }


def test_continue_decision_can_be_serialized():

    engine = GoalDecisionEngine()

    decision = engine.decide(
        GoalStateAction.PARTIAL
    )

    payload = decision.to_dict()

    assert payload == {
        "action": "continue",
        "reason": (
            "The goal is partially satisfied. "
            "THANOS should continue execution "
            "to satisfy the remaining requirements."
        ),
    }


def test_replan_decision_can_be_serialized():

    engine = GoalDecisionEngine()

    decision = engine.decide(
        GoalStateAction.NOT_ACHIEVED
    )

    payload = decision.to_dict()

    assert payload == {
        "action": "replan",
        "reason": (
            "The goal has not been achieved. "
            "THANOS should reconsider the current "
            "execution strategy."
        ),
    }