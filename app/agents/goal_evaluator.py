from dataclasses import dataclass
from enum import Enum


class GoalEvaluationAction(str, Enum):
    ACHIEVED = "achieved"
    PARTIAL = "partial"
    NOT_ACHIEVED = "not_achieved"


@dataclass(frozen=True)
class GoalEvaluation:
    action: GoalEvaluationAction
    goal: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "goal": self.goal,
            "reason": self.reason,
        }


class GoalEvaluator:

    def evaluate(
        self,
        goal: str,
        result: object | None = None,
        required_fields: set[str] | None = None,
    ) -> GoalEvaluation:

        if not goal.strip():
            raise ValueError(
                "Goal cannot be empty."
            )

        if result is None:
            return GoalEvaluation(
                action=GoalEvaluationAction.NOT_ACHIEVED,
                goal=goal,
                reason=(
                    "No result was produced "
                    "for the requested goal."
                ),
            )

        if required_fields:
            if not isinstance(result, dict):
                return GoalEvaluation(
                    action=GoalEvaluationAction.NOT_ACHIEVED,
                    goal=goal,
                    reason=(
                        "The result is not structured "
                        "data, so the required goal "
                        "requirements cannot be verified."
                    ),
                )

            missing_fields = (
                required_fields
                - set(result.keys())
            )

            if missing_fields:
                return GoalEvaluation(
                    action=GoalEvaluationAction.PARTIAL,
                    goal=goal,
                    reason=(
                        "The result only partially "
                        "satisfies the goal because "
                        f"these requirements are missing: "
                        f"{sorted(missing_fields)}"
                    ),
                )

        if isinstance(result, dict) and not result:
            return GoalEvaluation(
                action=GoalEvaluationAction.NOT_ACHIEVED,
                goal=goal,
                reason=(
                    "The tool returned an empty "
                    "result, so the goal was not achieved."
                ),
            )

        return GoalEvaluation(
            action=GoalEvaluationAction.ACHIEVED,
            goal=goal,
            reason=(
                "The available result satisfies "
                "the known requirements of the goal."
            ),
        )