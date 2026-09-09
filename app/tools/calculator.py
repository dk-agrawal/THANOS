from app.tools.base import Tool
from app.tools.result import ToolResult


class CalculatorTool(Tool):

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Performs basic arithmetic calculations."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Arithmetic operation.",
                    "enum": [
                        "add",
                        "subtract",
                        "multiply",
                        "divide",
                    ],
                },
                "a": {
                    "type": "number",
                    "description": "First number.",
                },
                "b": {
                    "type": "number",
                    "description": "Second number.",
                },
            },
            "required": ["operation", "a", "b"],
        }

    async def execute(
        self,
        operation: str,
        a: float,
        b: float,
    ) -> ToolResult:

        if operation == "add":
            return ToolResult(
                success=True,
                data={"result": a + b},
            )

        if operation == "subtract":
            return ToolResult(
                success=True,
                data={"result": a - b},
            )

        if operation == "multiply":
            return ToolResult(
                success=True,
                data={"result": a * b},
            )

        if operation == "divide":

            if b == 0:
                return ToolResult(
                    success=False,
                    error="Cannot divide by zero.",
                )

            return ToolResult(
                success=True,
                data={"result": a / b},
            )

        return ToolResult(
            success=False,
            error=f"Unknown operation: {operation}",
        )