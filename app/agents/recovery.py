from dataclasses import dataclass
from enum import Enum

from app.agents.execution_history import ExecutionHistory
from app.tools.result import ToolResult


class RecoveryAction(str, Enum):
    CONTINUE = "continue"
    RETRY = "retry"
    REPLAN = "replan"
    ABORT = "abort"


@dataclass(frozen=True)
class RecoveryDecision:
    action: RecoveryAction
    tool_name: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "tool_name": self.tool_name,
            "reason": self.reason,
        }


class RecoveryEngine:

    def decide(
        self,
        tool_name: str,
        result: ToolResult,
        retry_count: int = 0,
        max_retries: int = 2,
        previous_replans: int = 0,
        history: ExecutionHistory | None = None,
    ) -> RecoveryDecision:

        if retry_count < 0:
            raise ValueError("Retry count cannot be negative.")

        if max_retries < 0:
            raise ValueError("Maximum retries cannot be negative.")

        if previous_replans < 0:
            raise ValueError("Previous replans cannot be negative.")

        if result.success:
            return RecoveryDecision(
                action=RecoveryAction.CONTINUE,
                tool_name=tool_name,
                reason="Tool execution succeeded.",
            )

        if history is not None:
            previous_replans = history.tool_replan_count(
                tool_name
            )

        if retry_count < max_retries:
            return RecoveryDecision(
                action=RecoveryAction.RETRY,
                tool_name=tool_name,
                reason=(
                    f"Tool failed and retry budget remains. "
                    f"Reason: {result.error}"
                ),
            )

        if previous_replans > 0:
            return RecoveryDecision(
                action=RecoveryAction.ABORT,
                tool_name=tool_name,
                reason=(
                    f"Tool '{tool_name}' failed after "
                    f"retry budget was exhausted and "
                    f"this tool has already been replanned. "
                    f"Further recovery would risk an "
                    f"execution loop. "
                    f"Reason: {result.error}"
                ),
            )

        return RecoveryDecision(
            action=RecoveryAction.REPLAN,
            tool_name=tool_name,
            reason=(
                f"Tool '{tool_name}' failed after "
                f"{retry_count} retries. "
                f"Replanning is required. "
                f"Reason: {result.error}"
            ),
        )

    def recover(
        self,
        tool_name: str,
        result: ToolResult,
    ) -> ToolResult:

        if result.success:
            return result

        return ToolResult(
            success=False,
            error=(
                f"THANOS could not complete the "
                f"'{tool_name}' operation. "
                f"Reason: {result.error}"
            ),
        )