import asyncio

from app.api.geocoding import GeocodingProvider
from app.api.weather import WeatherProvider


def test_weather():

    geocoder = GeocodingProvider()

    provider = WeatherProvider(
        geocoder=geocoder
    )

    result = asyncio.run(
        provider.current_weather(
            "Bhopal"
        )
    )

    assert result

    assert "location" in result
    assert "current" in result
    assert "units" in result

    location = result["location"]
    current = result["current"]

    assert location["name"]
    assert location["latitude"] is not None
    assert location["longitude"] is not None

    assert "temperature_2m" in current
    assert "relative_humidity_2m" in current
    assert "apparent_temperature" in current
    assert "weather_code" in current
    assert "wind_speed_10m" in current