import pytest

from app.core.update_release import (
    GitHubReleaseResolver,
    UpdateAsset,
)


def test_resolve_thanos_zip():

    release = {
        "tag_name": "v0.2.0",
        "assets": [
            {
                "name": "THANOS-0.2.0.zip",
                "browser_download_url": (
                    "https://github.com/example/"
                    "thanos/releases/download/"
                    "v0.2.0/THANOS-0.2.0.zip"
                ),
                "size": 12345,
            }
        ],
    }

    resolver = GitHubReleaseResolver()

    result = resolver.resolve(
        release
    )

    assert isinstance(
        result,
        UpdateAsset,
    )

    assert (
        result.name
        == "THANOS-0.2.0.zip"
    )

    assert (
        result.download_url
        == (
            "https://github.com/example/"
            "thanos/releases/download/"
            "v0.2.0/THANOS-0.2.0.zip"
        )
    )

    assert result.size == 12345
    assert result.sha256 is None


def test_resolve_with_sha256():

    release = {
        "tag_name": "v0.2.0",
        "assets": [
            {
                "name": "THANOS-0.2.0.zip",
                "browser_download_url": (
                    "https://example.com/"
                    "THANOS-0.2.0.zip"
                ),
                "size": 100,
            },
            {
                "name": "THANOS-0.2.0.zip.sha256",
                "sha256": (
                    "abcdef123456"
                ),
            },
        ],
    }

    resolver = GitHubReleaseResolver()

    result = resolver.resolve(
        release
    )

    assert result.sha256 == (
        "abcdef123456"
    )


def test_non_zip_assets_are_ignored():

    release = {
        "assets": [
            {
                "name": "THANOS-0.2.0.exe",
                "browser_download_url": (
                    "https://example.com/"
                    "THANOS.exe"
                ),
            },
            {
                "name": "release-notes.txt",
                "browser_download_url": (
                    "https://example.com/"
                    "notes.txt"
                ),
            },
        ],
    }

    resolver = GitHubReleaseResolver()

    with pytest.raises(
        ValueError,
        match="No ZIP update asset",
    ):

        resolver.resolve(
            release
        )


def test_empty_assets_are_rejected():

    resolver = GitHubReleaseResolver()

    with pytest.raises(
        ValueError,
        match="No ZIP update asset",
    ):

        resolver.resolve(
            {
                "assets": []
            }
        )


def test_invalid_assets_type():

    resolver = GitHubReleaseResolver()

    with pytest.raises(
        ValueError,
        match="assets must be a list",
    ):

        resolver.resolve(
            {
                "assets": "invalid"
            }
        )


def test_thanos_asset_gets_priority():

    release = {
        "assets": [
            {
                "name": "update.zip",
                "browser_download_url": (
                    "https://example.com/update.zip"
                ),
            },
            {
                "name": "THANOS-0.2.0.zip",
                "browser_download_url": (
                    "https://example.com/thanos.zip"
                ),
            },
        ],
    }

    resolver = GitHubReleaseResolver()

    result = resolver.resolve(
        release
    )

    assert result.name == (
        "THANOS-0.2.0.zip"
    )