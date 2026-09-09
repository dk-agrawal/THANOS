from app.tools.result import ToolResult


class ToolVerifier:

    def verify(self, result: ToolResult) -> ToolResult:

        if not isinstance(result, ToolResult):
            return ToolResult(
                success=False,
                error="Invalid tool result object.",
            )

        if not result.success:
            return result

        if result.data is None:
            return ToolResult(
                success=False,
                error="Tool reported success but returned no data.",
            )

        return result