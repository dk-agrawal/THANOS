from abc import ABC, abstractmethod

from app.tools.result import ToolResult


class Tool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
        }

    @abstractmethod
    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        pass

    def definition(self) -> dict:

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }