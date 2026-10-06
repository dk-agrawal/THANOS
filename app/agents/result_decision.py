from dataclasses import dataclass
from enum import Enum


class ResultDecisionAction(str, Enum):
    CONTINUE = "continue"
    RECOVER = "recover"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class ResultDecision:
    action: ResultDecisionAction
    tool_name: str
    reason: str


class ResultDecisionEngine:

    def decide(
        self,
        tool_name: str,
        success: bool,
        result: object | None = None,
        error: str | None = None,
    ) -> ResultDecision:

        if not tool_name.strip():
            raise ValueError(
                "Tool name cannot be empty."
            )

        if success and result is not None:
            return ResultDecision(
                action=ResultDecisionAction.CONTINUE,
                tool_name=tool_name,
                reason="Tool produced a usable result.",
            )

        if success:
            return ResultDecision(
                action=ResultDecisionAction.INSUFFICIENT,
                tool_name=tool_name,
                reason=(
                    "Tool succeeded but produced "
                    "no usable result."
                ),
            )

        return ResultDecision(
            action=ResultDecisionAction.RECOVER,
            tool_name=tool_name,
            reason="Tool did not produce a usable result.",
        )
