from app.api.client import APIClient
from app.api.geocoding import GeocodingProvider


class WeatherProvider:

    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(
        self,
        client: APIClient | None = None,
        geocoder: GeocodingProvider | None = None,
    ):
        self.client = client or APIClient()
        if geocoder is None:
            raise ValueError(
                "GeocodingProvider is required."
            )
        self.geocoder = geocoder

    async def current_weather(
        self,
        location: str,
    ) -> dict:

        place = await self.geocoder.search(location)

        weather = await self.client.get(
            self.FORECAST_URL,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
        )

        return {
            "location": place,
            "current": weather.get("current", {}),
            "units": weather.get(
                "current_units",
                {},
            ),
        }