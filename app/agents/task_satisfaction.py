from dataclasses import dataclass
from enum import Enum


class TaskSatisfactionAction(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNSATISFIED = "unsatisfied"


@dataclass(frozen=True)
class TaskSatisfaction:
    action: TaskSatisfactionAction
    tool_name: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "tool_name": self.tool_name,
            "reason": self.reason,
        }


class TaskSatisfactionEngine:

    def evaluate(
        self,
        tool_name: str,
        result: object | None = None,
        required_fields: set[str] | None = None,
    ) -> TaskSatisfaction:

        if not tool_name.strip():
            raise ValueError(
                "Tool name cannot be empty."
            )

        if result is None:
            return TaskSatisfaction(
                action=TaskSatisfactionAction.UNSATISFIED,
                tool_name=tool_name,
                reason=(
                    "No result was produced for "
                    "the requested operation."
                ),
            )

        if required_fields:
            if not isinstance(result, dict):
                return TaskSatisfaction(
                    action=TaskSatisfactionAction.UNSATISFIED,
                    tool_name=tool_name,
                    reason=(
                        "The result is not structured "
                        "data, so required fields "
                        "cannot be verified."
                    ),
                )

            missing_fields = (
                required_fields
                - set(result.keys())
            )

            if missing_fields:
                return TaskSatisfaction(
                    action=TaskSatisfactionAction.PARTIAL,
                    tool_name=tool_name,
                    reason=(
                        "The result is missing "
                        f"required fields: "
                        f"{sorted(missing_fields)}"
                    ),
                )

        if isinstance(result, dict) and not result:
            return TaskSatisfaction(
                action=TaskSatisfactionAction.UNSATISFIED,
                tool_name=tool_name,
                reason=(
                    "The tool returned an empty "
                    "result."
                ),
            )

        return TaskSatisfaction(
            action=TaskSatisfactionAction.COMPLETE,
            tool_name=tool_name,
            reason=(
                "The tool produced a result "
                "that satisfies the available "
                "requirements."
            ),
        )