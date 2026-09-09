from app.ai.registry import AIProviderRegistry
from app.ai.provider import AIProvider


class AIRouter:

    def __init__(
        self,
        registry: AIProviderRegistry,
        default_provider: str = "openrouter",
    ):
        self.registry = registry
        self.default_provider = default_provider

        if not self.registry.has(
            self.default_provider
        ):
            raise ValueError(
                f"Default AI provider is not registered: "
                f"{self.default_provider}"
            )

    def get_provider(
        self,
        provider_name: str | None = None,
    ) -> AIProvider:

        name = (
            provider_name
            or self.default_provider
        )

        return self.registry.get(name)

    def provider_names(self) -> list[str]:

        return self.registry.names()

    async def generate(
        self,
        prompt: str,
        provider_name: str | None = None,
    ) -> str:

        provider = self.get_provider(
            provider_name
        )

        return await provider.generate(
            prompt
        )

    async def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        provider_name: str | None = None,
    ) -> dict:

        provider = self.get_provider(
            provider_name
        )

        return await provider.generate_with_tools(
            messages=messages,
            tools=tools,
        )