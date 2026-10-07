from dataclasses import dataclass
from enum import Enum

from app.agents.goal_state import GoalStateAction


class GoalDecisionAction(str, Enum):
    COMPLETE = "complete"
    CONTINUE = "continue"
    REPLAN = "replan"
    ABORT = "abort"


@dataclass(frozen=True)
class GoalDecision:
    action: GoalDecisionAction
    reason: str

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "reason": self.reason,
        }


class GoalDecisionEngine:

    def decide(
        self,
        goal_action: GoalStateAction,
    ) -> GoalDecision:

        if not isinstance(
            goal_action,
            GoalStateAction,
        ):
            raise ValueError(
                "Invalid goal state action."
            )

        if goal_action == GoalStateAction.ACHIEVED:
            return GoalDecision(
                action=GoalDecisionAction.COMPLETE,
                reason=(
                    "The overall goal has been "
                    "achieved."
                ),
            )

        if goal_action == GoalStateAction.PARTIAL:
            return GoalDecision(
                action=GoalDecisionAction.CONTINUE,
                reason=(
                    "The goal is partially satisfied. "
                    "THANOS should continue execution "
                    "to satisfy the remaining requirements."
                ),
            )

        return GoalDecision(
            action=GoalDecisionAction.REPLAN,
            reason=(
                "The goal has not been achieved. "
                "THANOS should reconsider the current "
                "execution strategy."
            ),
        )