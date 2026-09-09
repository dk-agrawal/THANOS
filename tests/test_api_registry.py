from app.api.registry import APIRegistry


def test_api_registry():

    registry = APIRegistry()

    assert registry.names()

    expected_providers = {
        "geocoding",
        "weather",
        "news",
        "github",
    }

    assert expected_providers.issubset(
        set(registry.names())
    )

    for name in expected_providers:

        assert registry.has(name)

        provider = registry.get(name)

        assert provider is not None