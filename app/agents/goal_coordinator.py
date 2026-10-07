from dataclasses import dataclass
from enum import Enum

from app.agents.goal_requirements import (
    GoalRequirements,
)
from app.agents.goal_state import GoalStateAction
from app.agents.recovery import RecoveryAction
from app.agents.requirement_decision import (
    RequirementDecisionAction,
    RequirementDecisionEngine,
)


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

    def __init__(
        self,
        requirement_decision_engine=None,
    ):
        self.requirement_decision_engine = (
            requirement_decision_engine
            or RequirementDecisionEngine()
        )

    def coordinate(
        self,
        goal_action: GoalStateAction,
        recovery_action: RecoveryAction | None = None,
        requirements: GoalRequirements | None = None,
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

        if requirements is not None and not isinstance(
            requirements,
            GoalRequirements,
        ):
            raise ValueError(
                "Invalid goal requirements."
            )

        # RecoveryEngine always has priority.
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

        # Requirement-level reasoning takes priority
        # over the broader goal state when available.
        if requirements is not None:
            requirement_decision = (
                self.requirement_decision_engine.decide(
                    requirements
                )
            )

            if (
                requirement_decision.action
                == RequirementDecisionAction.COMPLETE
            ):
                return GoalCoordinatorDecision(
                    action=GoalCoordinatorAction.COMPLETE,
                    reason=(
                        "All goal requirements have "
                        "been completed."
                    ),
                )

            if (
                requirement_decision.action
                == RequirementDecisionAction.REPLAN
            ):
                return GoalCoordinatorDecision(
                    action=GoalCoordinatorAction.REPLAN,
                    reason=(
                        "One or more goal requirements "
                        "failed and require replanning."
                    ),
                )

            return GoalCoordinatorDecision(
                action=GoalCoordinatorAction.CONTINUE,
                reason=(
                    "Some goal requirements are still "
                    "pending and execution should continue."
                ),
            )

        # Fallback to broader GoalState reasoning
        # when no explicit requirements are available.
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