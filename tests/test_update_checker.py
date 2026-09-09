import asyncio

from app.core.update_checker import UpdateChecker
from app.core.update_info import UpdateInfo


class FakeAPIClient:

    async def get(
        self,
        url: str,
        *,
        params=None,
        headers=None,
    ) -> dict:

        return {
            "tag_name": "v0.2.0",
            "name": "THANOS 0.2.0",
            "html_url": (
                "https://github.com/example/thanos"
            ),
            "published_at": (
                "2026-09-05T00:00:00Z"
            ),
            "assets": [
                {
                    "name": "THANOS-0.2.0.zip",
                    "browser_download_url": (
                        "https://example.com/"
                        "THANOS-0.2.0.zip"
                    ),
                    "size": 12345,
                },
                {
                    "name": (
                        "THANOS-0.2.0.zip.sha256"
                    ),
                    "sha256": (
                        "abcdef123456"
                    ),
                },
            ],
        }


class FakeCurrentReleaseClient:

    async def get(
        self,
        url: str,
        *,
        params=None,
        headers=None,
    ) -> dict:

        return {
            "tag_name": "v0.1.0",
            "name": "THANOS 0.1.0",
            "html_url": (
                "https://github.com/example/thanos"
            ),
            "published_at": (
                "2026-09-01T00:00:00Z"
            ),
            "assets": [],
        }


def test_update_checker_creation():

    checker = UpdateChecker(
        client=FakeAPIClient()
    )

    assert checker is not None


def test_update_available():

    checker = UpdateChecker(
        client=FakeAPIClient()
    )

    result = asyncio.run(
        checker.check(
            owner="example",
            repo="thanos",
        )
    )

    assert isinstance(
        result,
        UpdateInfo,
    )

    assert result.current_version == (
        "0.1.0"
    )

    assert result.latest_version == (
        "0.2.0"
    )

    assert result.update_available is True

    assert result.release_name == (
        "THANOS 0.2.0"
    )

    assert result.release_url == (
        "https://github.com/example/thanos"
    )

    assert result.is_latest is False

    assert result.is_newer_version is True


def test_update_asset_is_resolved():

    checker = UpdateChecker(
        client=FakeAPIClient()
    )

    result = asyncio.run(
        checker.check(
            owner="example",
            repo="thanos",
        )
    )

    assert result.update_asset is not None

    assert result.download_url == (
        "https://example.com/"
        "THANOS-0.2.0.zip"
    )

    assert result.sha256 == (
        "abcdef123456"
    )


def test_current_version_does_not_resolve_asset():

    checker = UpdateChecker(
        client=FakeCurrentReleaseClient()
    )

    result = asyncio.run(
        checker.check(
            owner="example",
            repo="thanos",
        )
    )

    assert result.update_available is False
    assert result.update_asset is None
    assert result.download_url is None
    assert result.sha256 is None


def test_update_info_to_dict():

    info = UpdateInfo(
        current_version="0.1.0",
        latest_version="0.2.0",
        update_available=True,
        release_name="THANOS 0.2.0",
        update_asset={
            "name": "THANOS-0.2.0.zip",
            "download_url": (
                "https://example.com/update.zip"
            ),
            "sha256": "abcdef",
        },
    )

    data = info.to_dict()

    assert data["current_version"] == (
        "0.1.0"
    )

    assert data["latest_version"] == (
        "0.2.0"
    )

    assert data["update_available"] is True

    assert data["update_asset"]["name"] == (
        "THANOS-0.2.0.zip"
    )

    assert data["update_asset"]["sha256"] == (
        "abcdef"
    )