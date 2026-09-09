import platform

from app.tools.base import Tool
from app.tools.result import ToolResult


class SystemInfoTool(Tool):

    @property
    def name(self) -> str:
        return "system_info"

    @property
    def description(self) -> str:
        return (
            "Returns basic information about "
            "the current computer."
        )

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:

        return ToolResult(
            success=True,
            data={
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
        )