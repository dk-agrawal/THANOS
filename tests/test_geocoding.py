import asyncio

from app.api.geocoding import GeocodingProvider


def test_geocoding():

    provider = GeocodingProvider()

    result = asyncio.run(
        provider.search("Bhopal")
    )

    assert result

    assert result["name"]

    assert result["latitude"] is not None
    assert result["longitude"] is not None

    assert result["country"]
    assert result["country_code"]
    assert result["timezone"]