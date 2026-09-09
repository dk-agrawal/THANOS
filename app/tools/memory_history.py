from app.memory.service import MemoryService
from app.tools.base import Tool
from app.tools.result import ToolResult


class MemoryHistoryTool(Tool):

    def __init__(
        self,
        memory_service: MemoryService,
    ):
        self.memory_service = memory_service

    @property
    def name(self) -> str:
        return "get_memory_history"

    @property
    def description(self) -> str:
        return (
            "Returns the change history of a "
            "specific long-term memory."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": (
                        "The key of the memory whose "
                        "history should be retrieved."
                    ),
                }
            },
            "required": [
                "key"
            ],
        }

    async def execute(
        self,
        key: str,
        **kwargs,
    ) -> ToolResult:

        history = (
            self.memory_service.get_history(
                key
            )
        )

        return ToolResult(
            success=True,
            data={
                "key": key,
                "count": len(history),
                "history": history,
            },
        )