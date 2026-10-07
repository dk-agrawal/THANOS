from app.agents.goal_coordinator import (
    GoalCoordinator,
    GoalCoordinatorAction,
)
from app.agents.goal_state import GoalStateAction
from app.agents.recovery import RecoveryAction


def test_achieved_goal_completes():

    coordinator = GoalCoordinator()

    decision = coordinator.coordinate(
        goal_action=GoalStateAction.ACHIEVED,
    )

    assert (
        decision.action
        == GoalCoordinatorAction.COMPLETE
    )


def test_partial_goal_continues():

    coordinator = GoalCoordinator()

    decision = coordinator.coordinate(
        goal_action=GoalStateAction.PARTIAL,
    )

    assert (
        decision.action
        == GoalCoordinatorAction.CONTINUE
    )


def test_unachieved_goal_replans():

    coordinator = GoalCoordinator()

    decision = coordinator.coordinate(
        goal_action=GoalStateAction.NOT_ACHIEVED,
    )

    assert (
        decision.action
        == GoalCoordinatorAction.REPLAN
    )


def test_abort_has_priority():

    coordinator = GoalCoordinator()

    decision = coordinator.coordinate(
        goal_action=GoalStateAction.PARTIAL,
        recovery_action=RecoveryAction.ABORT,
    )

    assert (
        decision.action
        == GoalCoordinatorAction.ABORT
    )


def test_retry_has_priority():

    coordinator = GoalCoordinator()

    decision = coordinator.coordinate(
        goal_action=GoalStateAction.NOT_ACHIEVED,
        recovery_action=RecoveryAction.RETRY,
    )

    assert (
        decision.action
        == GoalCoordinatorAction.RETRY
    )


def test_replan_recovery_has_priority():

    coordinator = GoalCoordinator()

    decision = coordinator.coordinate(
        goal_action=GoalStateAction.ACHIEVED,
        recovery_action=RecoveryAction.REPLAN,
    )

    assert (
        decision.action
        == GoalCoordinatorAction.REPLAN
    )


def test_invalid_goal_action_is_rejected():

    coordinator = GoalCoordinator()

    try:
        coordinator.coordinate(
            goal_action="invalid",
        )
    except ValueError as error:
        assert str(error) == (
            "Invalid goal state action."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_invalid_recovery_action_is_rejected():

    coordinator = GoalCoordinator()

    try:
        coordinator.coordinate(
            goal_action=GoalStateAction.PARTIAL,
            recovery_action="invalid",
        )
    except ValueError as error:
        assert str(error) == (
            "Invalid recovery action."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_decision_can_be_serialized():

    coordinator = GoalCoordinator()

    decision = coordinator.coordinate(
        goal_action=GoalStateAction.ACHIEVED,
    )

    payload = decision.to_dict()

    assert payload == {
        "action": "complete",
        "reason": (
            "The overall goal has been achieved."
        ),
    }