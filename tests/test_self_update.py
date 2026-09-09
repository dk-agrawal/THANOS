import asyncio

from app.core.self_update import (
    SelfUpdateService,
)
from app.core.update_info import UpdateInfo


class FakeUpdateChecker:

    async def check(
        self,
        owner,
        repo,
    ):

        return UpdateInfo(
            current_version="0.1.0",
            latest_version="0.2.0",
            update_available=True,
            release_name="THANOS 0.2.0",
            release_url=(
                "https://github.com/example/thanos"
            ),
            update_asset={
                "name": "THANOS-0.2.0.zip",
                "download_url": (
                    "https://example.com/update.zip"
                ),
                "sha256": "abcdef",
            },
        )


class FakeDownloader:

    def __init__(self):

        self.downloaded = False
        self.cleaned = False

    async def download(
        self,
        url,
        expected_sha256=None,
    ):

        self.downloaded = True

        return "update.zip"

    def cleanup(
        self,
        file_path,
    ):

        self.cleaned = True


class FakeInstaller:

    def __init__(self):

        self.prepared = False
        self.cleaned = False

    def prepare_package(
        self,
        package_path,
    ):

        self.prepared = True

        return "package_directory"

    def cleanup(
        self,
        package_directory,
    ):

        self.cleaned = True


class FakeRunner:

    def __init__(self):

        self.ran = False

    def run(
        self,
        package_directory,
        project_root,
    ):

        self.ran = True

        return {
            "success": True,
            "rolled_back": False,
            "tests": {
                "success": True,
                "return_code": 0,
            },
        }


def create_service():

    downloader = FakeDownloader()
    installer = FakeInstaller()
    runner = FakeRunner()

    service = SelfUpdateService(
        update_checker=FakeUpdateChecker(),
        downloader=downloader,
        installer=installer,
        runner=runner,
    )

    return (
        service,
        downloader,
        installer,
        runner,
    )


def test_check():

    service, _, _, _ = (
        create_service()
    )

    result = asyncio.run(
        service.check(
            owner="example",
            repo="thanos",
        )
    )

    assert result["success"] is True
    assert result[
        "update_available"
    ] is True


def test_dry_run_does_not_modify_project(
    tmp_path,
):

    service, downloader, installer, runner = (
        create_service()
    )

    project = (
        tmp_path
        / "project"
    )

    project.mkdir()

    result = asyncio.run(
        service.update(
            owner="example",
            repo="thanos",
            project_root=project,
            dry_run=True,
        )
    )

    assert result["success"] is True
    assert result["updated"] is False
    assert result["dry_run"] is True

    assert downloader.downloaded is False
    assert installer.prepared is False
    assert runner.ran is False


def test_real_update_pipeline(
    tmp_path,
):

    service, downloader, installer, runner = (
        create_service()
    )

    project = (
        tmp_path
        / "project"
    )

    project.mkdir()

    result = asyncio.run(
        service.update(
            owner="example",
            repo="thanos",
            project_root=project,
            dry_run=False,
        )
    )

    assert result["success"] is True
    assert result["updated"] is True

    assert downloader.downloaded is True
    assert downloader.cleaned is True

    assert installer.prepared is True
    assert installer.cleaned is True

    assert runner.ran is True


def test_missing_project_is_rejected(
    tmp_path,
):

    service, _, _, _ = (
        create_service()
    )

    missing_project = (
        tmp_path
        / "missing"
    )

    try:

        asyncio.run(
            service.update(
                owner="example",
                repo="thanos",
                project_root=missing_project,
                dry_run=True,
            )
        )

        assert False

    except ValueError as error:

        assert (
            "Project directory"
            in str(error)
        )