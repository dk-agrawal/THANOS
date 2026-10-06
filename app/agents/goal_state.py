from dataclasses import dataclass, field
from enum import Enum


class GoalStateAction(str, Enum):
    ACHIEVED = "achieved"
    PARTIAL = "partial"
    NOT_ACHIEVED = "not_achieved"


@dataclass(frozen=True)
class GoalResult:
    tool_name: str
    action: GoalStateAction
    reason: str


@dataclass
class GoalState:
    goal: str
    results: list[GoalResult] = field(default_factory=list)

    def add_result(
        self,
        tool_name: str,
        action: GoalStateAction,
        reason: str,
    ) -> None:

        if not tool_name.strip():
            raise ValueError(
                "Tool name cannot be empty."
            )

        if not reason.strip():
            raise ValueError(
                "Reason cannot be empty."
            )

        self.results.append(
            GoalResult(
                tool_name=tool_name,
                action=action,
                reason=reason,
            )
        )

    @property
    def action(self) -> GoalStateAction:

        if not self.results:
            return GoalStateAction.NOT_ACHIEVED

        actions = {
            result.action
            for result in self.results
        }

        if actions == {
            GoalStateAction.ACHIEVED
        }:
            return GoalStateAction.ACHIEVED

        if GoalStateAction.PARTIAL in actions:
            return GoalStateAction.PARTIAL

        if GoalStateAction.NOT_ACHIEVED in actions:
            if (
                GoalStateAction.ACHIEVED in actions
            ):
                return GoalStateAction.PARTIAL

            return GoalStateAction.NOT_ACHIEVED

        return GoalStateAction.PARTIAL

    @property
    def is_complete(self) -> bool:
        return self.action == GoalStateAction.ACHIEVED

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "action": self.action.value,
            "is_complete": self.is_complete,
            "results": [
                {
                    "tool_name": result.tool_name,
                    "action": result.action.value,
                    "reason": result.reason,
                }
                for result in self.results
            ],
        }