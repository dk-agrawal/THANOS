from app.api.client import APIClient
from app.core.update_info import UpdateInfo
from app.core.update_release import (
    GitHubReleaseResolver,
)
from app.core.version import VersionManager


class UpdateChecker:

    def __init__(
        self,
        client: APIClient | None = None,
        resolver: GitHubReleaseResolver | None = None,
    ):
        self.client = (
            client or APIClient()
        )

        self.resolver = (
            resolver
            or GitHubReleaseResolver()
        )

    async def check(
        self,
        owner: str,
        repo: str,
    ) -> UpdateInfo:

        if not owner:
            raise ValueError(
                "GitHub owner cannot be empty."
            )

        if not repo:
            raise ValueError(
                "GitHub repository cannot be empty."
            )

        url = (
            f"https://api.github.com/"
            f"repos/{owner}/{repo}/releases/latest"
        )

        data = await self.client.get(
            url,
            headers={
                "Accept": (
                    "application/vnd.github+json"
                ),
                "X-GitHub-Api-Version": (
                    "2026-03-10"
                ),
            },
        )

        tag_name = data.get(
            "tag_name"
        )

        if not tag_name:
            raise RuntimeError(
                "GitHub release does not contain "
                "a tag_name."
            )

        latest_version = (
            VersionManager.parse(
                tag_name
            )
        )

        current_version = (
            VersionManager.current_version()
        )

        update_available = (
            current_version
            < latest_version
        )

        update_asset = None

        if update_available:

            asset = self.resolver.resolve(
                data
            )

            update_asset = (
                asset.to_dict()
            )

        return UpdateInfo(
            current_version=str(
                current_version
            ),
            latest_version=str(
                latest_version
            ),
            update_available=(
                update_available
            ),
            release_name=data.get(
                "name"
            ),
            release_url=data.get(
                "html_url"
            ),
            published_at=data.get(
                "published_at"
            ),
            update_asset=update_asset,
        )