import asyncio

from pathlib import Path

from app.core.update_info import UpdateInfo
from app.core.update_manager import UpdateManager


class FakeSelfUpdateService:

    async def check(
        self,
        owner,
        repo,
    ):

        return {
            "success": True,
            "update_available": True,
            "update": {
                "current_version": "0.1.0",
                "latest_version": "0.2.0",
                "update_available": True,
                "release_name": "THANOS 0.2.0",
                "release_url": (
                    "https://github.com/example/thanos"
                ),
                "published_at": (
                    "2026-09-05T00:00:00Z"
                ),
                "update_asset": {
                    "name": "THANOS-0.2.0.zip",
                    "download_url": (
                        "https://example.com/update.zip"
                    ),
                    "sha256": "abcdef",
                },
            },
        }

    async def update(
        self,
        owner,
        repo,
        project_root,
        dry_run=True,
    ):

        return {
            "success": True,
            "updated": False,
            "dry_run": dry_run,
            "message": "Update detected.",
        }


def create_manager():

    return UpdateManager(
        self_update=(
            FakeSelfUpdateService()
        )
    )


def test_check_for_update():

    manager = create_manager()

    result = asyncio.run(
        manager.check_for_update(
            owner="example",
            repo="thanos",
        )
    )

    assert result["success"] is True

    assert (
        result["update_available"]
        is True
    )


def test_update():

    manager = create_manager()

    result = asyncio.run(
        manager.update(
            owner="example",
            repo="thanos",
            project_root="project",
            dry_run=True,
        )
    )

    assert result["success"] is True
    assert result["updated"] is False
    assert result["dry_run"] is True


def test_get_update_info():

    manager = create_manager()

    result = asyncio.run(
        manager.get_update_info(
            owner="example",
            repo="thanos",
        )
    )

    assert isinstance(
        result,
        UpdateInfo,
    )

    assert (
        result.current_version
        == "0.1.0"
    )

    assert (
        result.latest_version
        == "0.2.0"
    )

    assert (
        result.update_available
        is True
    )

    assert (
        result.download_url
        == "https://example.com/update.zip"
    )

    assert (
        result.sha256
        == "abcdef"
    )


def test_update_info_contains_release():

    manager = create_manager()

    result = asyncio.run(
        manager.get_update_info(
            owner="example",
            repo="thanos",
        )
    )

    assert (
        result.release_name
        == "THANOS 0.2.0"
    )

    assert (
        result.release_url
        == (
            "https://github.com/example/thanos"
        )
    )