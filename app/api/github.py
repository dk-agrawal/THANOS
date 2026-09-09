from app.api.client import APIClient
from app.core.config import settings


class GitHubProvider:

    def __init__(
        self,
        client: APIClient | None = None,
    ):
        self.client = client or APIClient()

    def _headers(self) -> dict:

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }

        if settings.GITHUB_TOKEN:
            headers["Authorization"] = (
                f"Bearer {settings.GITHUB_TOKEN}"
            )

        return headers

    async def search_repositories(
        self,
        query: str,
        per_page: int = 5,
    ) -> dict:

        return await self.client.get(
            f"{settings.GITHUB_API_BASE_URL}/search/repositories",
            params={
                "q": query,
                "per_page": per_page,
            },
            headers=self._headers(),
        )

    async def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> dict:

        return await self.client.get(
            f"{settings.GITHUB_API_BASE_URL}/repos/{owner}/{repo}",
            headers=self._headers(),
        )