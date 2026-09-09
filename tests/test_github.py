import asyncio

import pytest

from app.api.github import GitHubProvider
from app.core.config import settings


def test_github():

    provider = GitHubProvider()

    if not settings.GITHUB_TOKEN:
        pytest.skip(
            "GITHUB_TOKEN is not configured"
        )

    result = asyncio.run(
        provider.search_repositories(
            query="python",
            per_page=5,
        )
    )

    assert result

    assert "items" in result
    assert isinstance(
        result["items"],
        list,
    )

    assert len(result["items"]) > 0

    repository = result["items"][0]

    assert repository.get("name")
    assert repository.get("full_name")
    assert repository.get("html_url")