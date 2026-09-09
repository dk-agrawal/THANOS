class APIProviderRegistry:

    def __init__(self):
        self._providers = {}

    def register(
        self,
        name: str,
        provider,
    ) -> None:

        if not name:
            raise ValueError(
                "Provider name cannot be empty."
            )

        if provider is None:
            raise ValueError(
                "Provider cannot be None."
            )

        self._providers[name] = provider

    def get(self, name: str):

        provider = self._providers.get(name)

        if provider is None:
            raise KeyError(
                f"Provider not registered: {name}"
            )

        return provider

    def has(self, name: str) -> bool:

        return name in self._providers

    def remove(self, name: str) -> None:

        self._providers.pop(name, None)

    def names(self) -> list[str]:

        return list(self._providers.keys())

    def clear(self) -> None:

        self._providers.clear()