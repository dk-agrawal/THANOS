from app.memory.service import MemoryService
from app.tools.base import Tool
from app.tools.result import ToolResult


class ListPendingMemoryTool(Tool):

    def __init__(
        self,
        memory_service: MemoryService,
    ):
        self.memory_service = memory_service

    @property
    def name(self) -> str:
        return "list_pending_memories"

    @property
    def description(self) -> str:
        return (
            "Lists memories that are waiting "
            "for confirmation before being saved "
            "as long-term memories."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
        }

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:

        memories = (
            self.memory_service.list_pending()
        )

        return ToolResult(
            success=True,
            data={
                "count": len(memories),
                "memories": memories,
            },
        )


class ConfirmPendingMemoryTool(Tool):

    def __init__(
        self,
        memory_service: MemoryService,
    ):
        self.memory_service = memory_service

    @property
    def name(self) -> str:
        return "confirm_pending_memory"

    @property
    def description(self) -> str:
        return (
            "Confirms a pending memory and saves it "
            "as a permanent long-term memory."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": (
                        "The key of the pending memory "
                        "to confirm."
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

        result = (
            self.memory_service.confirm_pending(
                key
            )
        )

        if result is None:

            return ToolResult(
                success=False,
                error=(
                    f"Pending memory not found: {key}"
                ),
            )

        return ToolResult(
            success=True,
            data={
                "confirmed": True,
                "operation": result.to_dict(),
            },
        )