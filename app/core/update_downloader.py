import hashlib
import tempfile
from pathlib import Path

import httpx


class UpdateDownloader:

    def __init__(
        self,
        download_root: str | Path | None = None,
        timeout: float = 60.0,
    ):
        if download_root is None:
            self.download_root = (
                Path(tempfile.gettempdir())
                / "thanos_downloads"
            )
        else:
            self.download_root = Path(
                download_root
            )

        self.download_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.timeout = timeout

    async def download(
        self,
        url: str,
        expected_sha256: str | None = None,
    ) -> Path:

        if not url:
            raise ValueError(
                "Download URL cannot be empty."
            )

        filename = self._filename_from_url(
            url
        )

        destination = (
            self.download_root
            / filename
        )

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                url
            )

            response.raise_for_status()

            with open(
                destination,
                "wb",
            ) as file:

                file.write(
                    response.content
                )

        if expected_sha256:

            actual_sha256 = (
                self.calculate_sha256(
                    destination
                )
            )

            if (
                actual_sha256.lower()
                != expected_sha256.lower()
            ):

                destination.unlink(
                    missing_ok=True
                )

                raise ValueError(
                    "Downloaded update failed "
                    "SHA-256 verification."
                )

        return destination

    def calculate_sha256(
        self,
        file_path: str | Path,
    ) -> str:

        path = Path(
            file_path
        )

        if not path.exists():
            raise ValueError(
                "File does not exist."
            )

        if not path.is_file():
            raise ValueError(
                "SHA-256 can only be calculated "
                "for files."
            )

        digest = hashlib.sha256()

        with open(
            path,
            "rb",
        ) as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                digest.update(
                    chunk
                )

        return digest.hexdigest()

    def cleanup(
        self,
        file_path: str | Path,
    ) -> None:

        path = Path(
            file_path
        )

        if path.exists():
            path.unlink()

    @staticmethod
    def _filename_from_url(
        url: str,
    ) -> str:

        filename = (
            url.split("?")[0]
            .rstrip("/")
            .split("/")[-1]
        )

        if not filename:
            filename = "thanos_update.zip"

        return filename