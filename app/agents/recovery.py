from app.tools.result import ToolResult


class RecoveryEngine:

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