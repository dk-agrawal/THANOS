from app.api.client import APIClient


class GeocodingProvider:

    BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self, client: APIClient | None = None):
        self.client = client or APIClient()

    async def search(self, location: str) -> dict:

        data = await self.client.get(
            self.BASE_URL,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )

        results = data.get("results", [])

        if not results:
            raise ValueError(
                f"Location not found: {location}"
            )

        result = results[0]

        return {
            "name": result.get("name"),
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "country": result.get("country"),
            "country_code": result.get("country_code"),
            "timezone": result.get("timezone"),
        }