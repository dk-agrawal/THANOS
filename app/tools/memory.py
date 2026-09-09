from app.memory.service import MemoryService
from app.tools.base import Tool
from app.tools.result import ToolResult


class RememberTool(Tool):

    def __init__(
        self,
        memory_service: MemoryService,
    ):
        self.memory_service = memory_service

    @property
    def name(self) -> str:
        return "remember"

    @property
    def description(self) -> str:
        return (
            "Stores information as a long-term "
            "memory for future conversations."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": (
                        "A unique key identifying "
                        "the memory."
                    ),
                },
                "value": {
                    "type": "string",
                    "description": (
                        "The information to remember."
                    ),
                },
            },
            "required": [
                "key",
                "value",
            ],
        }

    async def execute(
        self,
        key: str,
        value: str,
        **kwargs,
    ) -> ToolResult:

        result = self.memory_service.remember(
            key=key,
            value=value,
        )

        return ToolResult(
            success=True,
            data=result.to_dict(),
        )


class RecallTool(Tool):

    def __init__(
        self,
        memory: MemoryService,
    ):
        self.memory = memory

    @property
    def name(self) -> str:
        return "recall"

    @property
    def description(self) -> str:
        return (
            "Recalls a specific long-term "
            "memory using its key."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": (
                        "The key of the memory "
                        "to recall."
                    ),
                },
            },
            "required": [
                "key",
            ],
        }

    async def execute(
        self,
        key: str,
        **kwargs,
    ) -> ToolResult:

        value = self.memory.recall(key)

        if value is None:

            return ToolResult(
                success=False,
                error=(
                    f"Memory not found: {key}"
                ),
            )

        return ToolResult(
            success=True,
            data={
                "key": key,
                "value": value,
            },
        )


class ForgetTool(Tool):

    def __init__(
        self,
        memory: MemoryService,
    ):
        self.memory = memory

    @property
    def name(self) -> str:
        return "forget"

    @property
    def description(self) -> str:
        return (
            "Deletes a specific long-term "
            "memory and records the deletion "
            "in memory history."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": (
                        "The key of the memory "
                        "to delete."
                    ),
                },
            },
            "required": [
                "key",
            ],
        }

    async def execute(
        self,
        key: str,
        **kwargs,
    ) -> ToolResult:

        result = self.memory.forget(key)

        if result is None:

            return ToolResult(
                success=False,
                error=(
                    f"Memory not found: {key}"
                ),
            )

        return ToolResult(
            success=True,
            data=result.to_dict(),
        )


class ListMemoryTool(Tool):

    def __init__(
        self,
        memory: MemoryService,
    ):
        self.memory = memory

    @property
    def name(self) -> str:
        return "list_memories"

    @property
    def description(self) -> str:
        return (
            "Lists all stored long-term "
            "memories."
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

        memories = self.memory.list_memories()

        return ToolResult(
            success=True,
            data={
                "count": len(memories),
                "memories": memories,
            },
        )