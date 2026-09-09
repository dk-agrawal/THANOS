import pytest

from app.ai.router import AIRouter


class FakeAIProvider:

    async def generate(
        self,
        prompt: str,
    ) -> str:

        return f"generated: {prompt}"

    async def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> dict:

        return {
            "provider": "fake",
            "messages": messages,
            "tools": tools,
        }


class FakeRegistry:

    def __init__(self):

        self.providers = {
            "fake": FakeAIProvider(),
        }

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self.providers

    def get(
        self,
        name: str,
    ):

        if name not in self.providers:
            raise KeyError(
                f"AI provider not registered: {name}"
            )

        return self.providers[name]

    def names(self) -> list[str]:

        return list(self.providers.keys())


@pytest.mark.asyncio
async def test_router_uses_default_provider():

    registry = FakeRegistry()

    router = AIRouter(
        registry=registry,
        default_provider="fake",
    )

    provider = router.get_provider()

    assert isinstance(
        provider,
        FakeAIProvider,
    )


@pytest.mark.asyncio
async def test_router_can_select_provider():

    registry = FakeRegistry()

    router = AIRouter(
        registry=registry,
        default_provider="fake",
    )

    provider = router.get_provider(
        "fake"
    )

    assert isinstance(
        provider,
        FakeAIProvider,
    )


@pytest.mark.asyncio
async def test_router_generate():

    registry = FakeRegistry()

    router = AIRouter(
        registry=registry,
        default_provider="fake",
    )

    result = await router.generate(
        "Hello THANOS"
    )

    assert result == (
        "generated: Hello THANOS"
    )


@pytest.mark.asyncio
async def test_router_generate_with_tools():

    registry = FakeRegistry()

    router = AIRouter(
        registry=registry,
        default_provider="fake",
    )

    messages = [
        {
            "role": "user",
            "content": "Calculate 2 + 2",
        }
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
            },
        }
    ]

    result = (
        await router.generate_with_tools(
            messages=messages,
            tools=tools,
        )
    )

    assert result["provider"] == "fake"
    assert result["messages"] == messages
    assert result["tools"] == tools


def test_router_rejects_missing_default_provider():

    registry = FakeRegistry()

    with pytest.raises(
        ValueError,
        match="Default AI provider is not registered",
    ):

        AIRouter(
            registry=registry,
            default_provider="openrouter",
        )


def test_router_lists_providers():

    registry = FakeRegistry()

    router = AIRouter(
        registry=registry,
        default_provider="fake",
    )

    assert router.provider_names() == [
        "fake"
    ]