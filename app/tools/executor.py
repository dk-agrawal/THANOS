import asyncio

from app.tools.registry import ToolRegistry
from app.tools.result import ToolResult
from app.tools.verifier import ToolVerifier

class ToolExecutor:

    def __init__(
        self,
        registry: ToolRegistry,
        timeout: float = 15.0,
        max_retries: int = 2,
    ):
        self.registry = registry
        self.timeout = timeout
        self.max_retries = max_retries
        self.verifier = ToolVerifier()

    async def execute(
        self,
        tool_name: str,
        arguments: dict,
    ) -> ToolResult:

        tool = self.registry.get(tool_name)

        if tool is None:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}",
            )

        last_error = None

        for attempt in range(self.max_retries + 1):

            try:
                result = await asyncio.wait_for(
                    tool.execute(**arguments),
                    timeout=self.timeout,
                )

                if not isinstance(result, ToolResult):
                    return ToolResult(
                        success=False,
                        error=(
                            f"Tool '{tool_name}' returned "
                            "an invalid result."
                        ),
                    )

                return self.verifier.verify(result)

            except asyncio.TimeoutError:
                last_error = (
                    f"Tool '{tool_name}' timed out "
                    f"after {self.timeout} seconds."
                )

            except Exception as error:
                last_error = (
                    f"{type(error).__name__}: {error}"
                )

        return ToolResult(
            success=False,
            error=(
                f"Tool '{tool_name}' failed after "
                f"{self.max_retries + 1} attempts. "
                f"Last error: {last_error}"
            ),
        )