from pathlib import Path

from app.core.update_checker import UpdateChecker
from app.core.update_downloader import UpdateDownloader
from app.core.update_installer import UpdateInstaller
from app.core.update_runner import UpdateRunner


class SelfUpdateService:

    def __init__(
        self,
        update_checker: UpdateChecker | None = None,
        downloader: UpdateDownloader | None = None,
        installer: UpdateInstaller | None = None,
        runner: UpdateRunner | None = None,
    ):
        self.update_checker = (
            update_checker
            or UpdateChecker()
        )

        self.downloader = (
            downloader
            or UpdateDownloader()
        )

        self.installer = (
            installer
            or UpdateInstaller()
        )

        self.runner = (
            runner
            or UpdateRunner()
        )

    async def check(
        self,
        owner: str,
        repo: str,
    ) -> dict:

        update_info = (
            await self.update_checker.check(
                owner=owner,
                repo=repo,
            )
        )

        return {
            "success": True,
            "update_available": (
                update_info.update_available
            ),
            "update": update_info.to_dict(),
        }

    async def update(
        self,
        owner: str,
        repo: str,
        project_root: str | Path,
        dry_run: bool = True,
    ) -> dict:

        project = Path(
            project_root
        ).resolve()

        if not project.exists():
            raise ValueError(
                "Project directory does not exist."
            )

        update_info = (
            await self.update_checker.check(
                owner=owner,
                repo=repo,
            )
        )

        if not update_info.update_available:

            return {
                "success": True,
                "updated": False,
                "message": (
                    "THANOS is already up to date."
                ),
                "update": update_info.to_dict(),
            }

        if not update_info.download_url:

            raise RuntimeError(
                "Update is available but no "
                "download URL was found."
            )

        if dry_run:

            return {
                "success": True,
                "updated": False,
                "dry_run": True,
                "message": (
                    "Update detected. "
                    "Dry-run prevented "
                    "project modification."
                ),
                "update": update_info.to_dict(),
            }

        package_path = None
        package_directory = None

        try:

            package_path = (
                await self.downloader.download(
                    url=update_info.download_url,
                    expected_sha256=(
                        update_info.sha256
                    ),
                )
            )

            package_directory = (
                self.installer.prepare_package(
                    package_path
                )
            )

            result = self.runner.run(
                package_directory=(
                    package_directory
                ),
                project_root=project,
            )

            return {
                "success": result["success"],
                "updated": result["success"],
                "dry_run": False,
                "message": self._message(
                    result
                ),
                "update": update_info.to_dict(),
                "result": result,
            }

        finally:

            if package_directory is not None:

                self.installer.cleanup(
                    package_directory
                )

            if package_path is not None:

                self.downloader.cleanup(
                    package_path
                )

    @staticmethod
    def _message(
        result: dict,
    ) -> str:

        if result.get("success"):

            return (
                "THANOS update completed "
                "successfully."
            )

        if result.get("rolled_back"):

            return (
                "Update failed. "
                "THANOS was automatically "
                "rolled back."
            )

        return (
            "THANOS update failed."
        )