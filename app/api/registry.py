from app.api.github import GitHubProvider
from app.api.geocoding import GeocodingProvider
from app.api.news import NewsProvider
from app.api.providers import APIProviderRegistry
from app.api.weather import WeatherProvider


class APIRegistry:

    def __init__(self):

        self.providers = APIProviderRegistry()

        self._register_defaults()

    def _register_defaults(self):

        geocoding = GeocodingProvider()

        self.providers.register(
            "geocoding",
            geocoding,
        )

        self.providers.register(
            "weather",
            WeatherProvider(
                geocoder=geocoding,
            ),
        )

        self.providers.register(
            "news",
            NewsProvider(),
        )

        self.providers.register(
            "github",
            GitHubProvider(),
        )

    def get(self, name: str):

        return self.providers.get(name)

    def has(self, name: str) -> bool:

        return self.providers.has(name)

    def names(self) -> list[str]:

        return self.providers.names()