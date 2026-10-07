from dataclasses import dataclass
from enum import Enum

from app.agents.goal_decision import (
    GoalDecisionAction,
)
from app.agents.goal_state import GoalStateAction
from app.agents.recovery import RecoveryAction


class GoalCoordinatorAction(str, Enum):
    COMPLETE = "complete"
    CONTINUE = "continue"
    RETRY = "retry"
    REPLAN = "replan"
    ABORT = "abort"


@dataclass(frozen=True)
class GoalCoordinatorDecision:
    action: GoalCoordinatorAction
    reason: str

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "reason": self.reason,
        }


class GoalCoordinator:

    def coordinate(
        self,
        goal_action: GoalStateAction,
        recovery_action: RecoveryAction | None = None,
    ) -> GoalCoordinatorDecision:

        if not isinstance(
            goal_action,
            GoalStateAction,
        ):
            raise ValueError(
                "Invalid goal state action."
            )

        if recovery_action is not None and not isinstance(
            recovery_action,
            RecoveryAction,
        ):
            raise ValueError(
                "Invalid recovery action."
            )

        # Safety actions from RecoveryEngine always
        # take priority over goal-level continuation.
        if recovery_action == RecoveryAction.ABORT:
            return GoalCoordinatorDecision(
                action=GoalCoordinatorAction.ABORT,
                reason=(
                    "RecoveryEngine requested an "
                    "immediate safe abort."
                ),
            )

        if recovery_action == RecoveryAction.RETRY:
            return GoalCoordinatorDecision(
                action=GoalCoordinatorAction.RETRY,
                reason=(
                    "RecoveryEngine requested a retry "
                    "before making a goal-level decision."
                ),
            )

        if recovery_action == RecoveryAction.REPLAN:
            return GoalCoordinatorDecision(
                action=GoalCoordinatorAction.REPLAN,
                reason=(
                    "RecoveryEngine requested replanning "
                    "to recover the execution."
                ),
            )

        if goal_action == GoalStateAction.ACHIEVED:
            return GoalCoordinatorDecision(
                action=GoalCoordinatorAction.COMPLETE,
                reason=(
                    "The overall goal has been achieved."
                ),
            )

        if goal_action == GoalStateAction.PARTIAL:
            return GoalCoordinatorDecision(
                action=GoalCoordinatorAction.CONTINUE,
                reason=(
                    "The goal is partially satisfied "
                    "and execution should continue."
                ),
            )

        return GoalCoordinatorDecision(
            action=GoalCoordinatorAction.REPLAN,
            reason=(
                "The goal is not achieved and no "
                "higher-priority recovery action "
                "was requested."
            ),
        )