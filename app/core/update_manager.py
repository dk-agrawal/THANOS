from pathlib import Path

from app.core.self_update import SelfUpdateService
from app.core.update_info import UpdateInfo


class UpdateManager:

    def __init__(
        self,
        self_update: SelfUpdateService | None = None,
    ):
        self.self_update = (
            self_update
            or SelfUpdateService()
        )

    async def check_for_update(
        self,
        owner: str,
        repo: str,
    ) -> dict:

        return await self.self_update.check(
            owner=owner,
            repo=repo,
        )

    async def update(
        self,
        owner: str,
        repo: str,
        project_root: str | Path,
        dry_run: bool = True,
    ) -> dict:

        return await self.self_update.update(
            owner=owner,
            repo=repo,
            project_root=project_root,
            dry_run=dry_run,
        )

    async def get_update_info(
        self,
        owner: str,
        repo: str,
    ) -> UpdateInfo:

        result = await self.self_update.check(
            owner=owner,
            repo=repo,
        )

        update_data = result.get(
            "update"
        )

        if not update_data:
            raise RuntimeError(
                "Update information is unavailable."
            )

        return UpdateInfo(
            current_version=(
                update_data[
                    "current_version"
                ]
            ),
            latest_version=(
                update_data[
                    "latest_version"
                ]
            ),
            update_available=(
                update_data[
                    "update_available"
                ]
            ),
            release_name=(
                update_data.get(
                    "release_name"
                )
            ),
            release_url=(
                update_data.get(
                    "release_url"
                )
            ),
            published_at=(
                update_data.get(
                    "published_at"
                )
            ),
            update_asset=(
                update_data.get(
                    "update_asset"
                )
            ),
        )