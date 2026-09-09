from app.api.weather import WeatherProvider
from app.tools.base import Tool
from app.tools.result import ToolResult
from app.api.registry import APIRegistry

class WeatherTool(Tool):

    def __init__(self, api_registry:APIRegistry):
        self.provider = api_registry.get("weather")

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return (
            "Gets current weather conditions "
            "for a specified location."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": (
                        "City or location name, "
                        "for example Bhopal."
                    ),
                }
            },
            "required": ["location"],
        }

    async def execute(
        self,
        location: str,
    ) -> ToolResult:

        try:
            result = await self.provider.current_weather(
                location
            )

            return ToolResult(
                success=True,
                data=result,
            )

        except Exception as error:
            return ToolResult(
                success=False,
                error=f"Weather lookup failed: {error}",
            )