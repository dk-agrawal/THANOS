from app.api.providers import APIProviderRegistry


def test_api_provider_registry():

    registry = APIProviderRegistry()

    assert registry.names() == []

    provider_one = object()
    provider_two = object()

    registry.register(
        "provider_one",
        provider_one,
    )

    registry.register(
        "provider_two",
        provider_two,
    )

    assert registry.has("provider_one")
    assert registry.has("provider_two")

    assert (
        registry.get("provider_one")
        is provider_one
    )

    assert (
        registry.get("provider_two")
        is provider_two
    )

    assert set(registry.names()) == {
        "provider_one",
        "provider_two",
    }

    registry.remove("provider_one")

    assert not registry.has(
        "provider_one"
    )

    assert registry.has(
        "provider_two"
    )

    registry.clear()

    assert registry.names() == []


def test_api_provider_registry_invalid_registration():

    registry = APIProviderRegistry()

    try:
        registry.register(
            "",
            object(),
        )
        assert False
    except ValueError as error:
        assert str(error) == (
            "Provider name cannot be empty."
        )

    try:
        registry.register(
            "provider",
            None,
        )
        assert False
    except ValueError as error:
        assert str(error) == (
            "Provider cannot be None."
        )


def test_api_provider_registry_missing_provider():

    registry = APIProviderRegistry()

    try:
        registry.get(
            "missing"
        )
        assert False
    except KeyError as error:
        assert str(error) == (
            "'Provider not registered: missing'"
        )