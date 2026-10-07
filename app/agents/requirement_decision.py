from dataclasses import dataclass
from enum import Enum

from app.agents.goal_requirements import (
    GoalRequirements,
)


class RequirementDecisionAction(str, Enum):
    COMPLETE = "complete"
    CONTINUE = "continue"
    REPLAN = "replan"


@dataclass(frozen=True)
class RequirementDecision:
    action: RequirementDecisionAction
    reason: str

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "reason": self.reason,
        }


class RequirementDecisionEngine:

    def decide(
        self,
        requirements: GoalRequirements,
    ) -> RequirementDecision:

        if not isinstance(
            requirements,
            GoalRequirements,
        ):
            raise ValueError(
                "Invalid goal requirements."
            )

        if requirements.is_complete:
            return RequirementDecision(
                action=RequirementDecisionAction.COMPLETE,
                reason=(
                    "All goal requirements have "
                    "been completed."
                ),
            )

        if requirements.failed:
            return RequirementDecision(
                action=RequirementDecisionAction.REPLAN,
                reason=(
                    "One or more goal requirements "
                    "failed and require a different "
                    "execution strategy."
                ),
            )

        return RequirementDecision(
            action=RequirementDecisionAction.CONTINUE,
            reason=(
                "Some goal requirements are still "
                "pending and execution should continue."
            ),
        )