from app.tools.registry import ToolRegistry


class ToolRouter:

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def find_tool(self, user_input: str):
        text = user_input.lower().strip()

        if any(
            keyword in text
            for keyword in [
                "system info",
                "system information",
                "computer information",
                "pc information",
            ]
        ):
            return self.registry.get("system_info")

        return None