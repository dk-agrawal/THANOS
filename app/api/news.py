from datetime import datetime, timedelta, timezone

from app.api.client import APIClient
from app.core.config import settings


class NewsProvider:

    def __init__(
        self,
        client: APIClient | None = None,
    ):
        self.client = client or APIClient()

    async def search(
        self,
        query: str,
        language: str = "en",
        page_size: int = 5,
        from_date: str | None = None,
    ) -> dict:

        if not settings.NEWS_API_KEY:
            raise RuntimeError(
                "NEWS_API_KEY is not configured"
            )

        headers = {
            "X-Api-Key": settings.NEWS_API_KEY,
        }

        params = {
            "q": query,
            "language": language,
            "sortBy": "publishedAt",
            "pageSize": page_size,
        }

        if from_date:
            params["from"] = from_date

        return await self.client.get(
            f"{settings.NEWS_API_BASE_URL}/everything",
            params=params,
            headers=headers,
        )

    async def top_headlines(
        self,
        country: str = "in",
        category: str | None = None,
        page_size: int = 5,
    ) -> dict:

        if not settings.NEWS_API_KEY:
            raise RuntimeError(
                "NEWS_API_KEY is not configured"
            )

        headers = {
            "X-Api-Key": settings.NEWS_API_KEY,
        }

        params = {
            "country": country,
            "pageSize": page_size,
        }

        if category:
            params["category"] = category

        return await self.client.get(
            f"{settings.NEWS_API_BASE_URL}/top-headlines",
            params=params,
            headers=headers,
        )

    @staticmethod
    def recent_date(
        days: int = 7,
    ) -> str:

        date = (
            datetime.now(timezone.utc)
            - timedelta(days=days)
        )

        return date.strftime(
            "%Y-%m-%d"
        )