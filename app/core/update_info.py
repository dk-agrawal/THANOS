from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateInfo:

    current_version: str
    latest_version: str
    update_available: bool
    release_name: str | None = None
    release_url: str | None = None
    published_at: str | None = None
    update_asset: dict | None = None

    def to_dict(self) -> dict:

        return {
            "current_version": (
                self.current_version
            ),
            "latest_version": (
                self.latest_version
            ),
            "update_available": (
                self.update_available
            ),
            "release_name": (
                self.release_name
            ),
            "release_url": (
                self.release_url
            ),
            "published_at": (
                self.published_at
            ),
            "update_asset": (
                self.update_asset
            ),
        }

    @property
    def is_latest(self) -> bool:
        return not self.update_available

    @property
    def is_newer_version(self) -> bool:
        return self.update_available

    @property
    def download_url(self) -> str | None:

        if not self.update_asset:
            return None

        return self.update_asset.get(
            "download_url"
        )

    @property
    def sha256(self) -> str | None:

        if not self.update_asset:
            return None

        return self.update_asset.get(
            "sha256"
        )