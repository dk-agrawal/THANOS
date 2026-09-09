import asyncio

import pytest

from app.api.news import NewsProvider
from app.core.config import settings


def test_news():

    if not settings.NEWS_API_KEY:
        pytest.skip(
            "NEWS_API_KEY is not configured"
        )

    provider = NewsProvider()

    result = asyncio.run(
        provider.top_headlines(
            country="in",
            page_size=5,
        )
    )

    assert result
    assert result["status"] == "ok"

    assert "articles" in result
    assert isinstance(
        result["articles"],
        list,
    )