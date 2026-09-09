import asyncio
import hashlib

import pytest

from app.core.update_downloader import (
    UpdateDownloader,
)


class FakeResponse:

    content = b"THANOS UPDATE PACKAGE"

    def raise_for_status(self):
        pass


class FakeAsyncClient:

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        pass

    async def get(
        self,
        url,
    ):
        return FakeResponse()


def test_sha256(
    tmp_path,
):

    file_path = (
        tmp_path
        / "test.zip"
    )

    content = b"THANOS"

    file_path.write_bytes(
        content
    )

    expected = hashlib.sha256(
        content
    ).hexdigest()

    downloader = UpdateDownloader(
        download_root=tmp_path
    )

    assert (
        downloader.calculate_sha256(
            file_path
        )
        == expected
    )


def test_download(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.core.update_downloader.httpx.AsyncClient",
        FakeAsyncClient,
    )

    downloader = UpdateDownloader(
        download_root=tmp_path
    )

    result = asyncio.run(
        downloader.download(
            "https://example.com/thanos.zip"
        )
    )

    assert result.exists()
    assert result.name == "thanos.zip"

    assert (
        result.read_bytes()
        == b"THANOS UPDATE PACKAGE"
    )


def test_download_with_valid_sha256(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.core.update_downloader.httpx.AsyncClient",
        FakeAsyncClient,
    )

    content = b"THANOS UPDATE PACKAGE"

    expected = hashlib.sha256(
        content
    ).hexdigest()

    downloader = UpdateDownloader(
        download_root=tmp_path
    )

    result = asyncio.run(
        downloader.download(
            "https://example.com/thanos.zip",
            expected_sha256=expected,
        )
    )

    assert result.exists()


def test_invalid_sha256_is_rejected(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        "app.core.update_downloader.httpx.AsyncClient",
        FakeAsyncClient,
    )

    downloader = UpdateDownloader(
        download_root=tmp_path
    )

    with pytest.raises(
        ValueError,
        match="SHA-256 verification",
    ):

        asyncio.run(
            downloader.download(
                "https://example.com/thanos.zip",
                expected_sha256="invalid",
            )
        )

    assert not (
        tmp_path
        / "thanos.zip"
    ).exists()


def test_empty_url_is_rejected(
    tmp_path,
):

    downloader = UpdateDownloader(
        download_root=tmp_path
    )

    with pytest.raises(
        ValueError,
        match="Download URL",
    ):

        asyncio.run(
            downloader.download("")
        )


def test_cleanup(
    tmp_path,
):

    file_path = (
        tmp_path
        / "update.zip"
    )

    file_path.write_bytes(
        b"THANOS"
    )

    downloader = UpdateDownloader(
        download_root=tmp_path
    )

    downloader.cleanup(
        file_path
    )

    assert not file_path.exists()