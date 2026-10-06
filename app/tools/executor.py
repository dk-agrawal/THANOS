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

    async def execute_once(
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
            return ToolResult(
                success=False,
                error=(
                    f"Tool '{tool_name}' timed out "
                    f"after {self.timeout} seconds."
                ),
            )

        except Exception as error:
            return ToolResult(
                success=False,
                error=f"{type(error).__name__}: {error}",
            )

    async def execute(
        self,
        tool_name: str,
        arguments: dict,
    ) -> ToolResult:

        last_error = None

        for _ in range(self.max_retries + 1):
            result = await self.execute_once(
                tool_name=tool_name,
                arguments=arguments,
            )

            if result.success:
                return result

            last_error = result.error

        return ToolResult(
            success=False,
            error=(
                f"Tool '{tool_name}' failed after "
                f"{self.max_retries + 1} attempts. "
                f"Last error: {last_error}"
            ),
        )
