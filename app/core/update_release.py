from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateAsset:

    name: str
    download_url: str
    size: int | None = None
    sha256: str | None = None

    def to_dict(self) -> dict:

        return {
            "name": self.name,
            "download_url": self.download_url,
            "size": self.size,
            "sha256": self.sha256,
        }


class GitHubReleaseResolver:

    ZIP_EXTENSIONS = (
        ".zip",
    )

    SHA256_SUFFIXES = (
        ".sha256",
        ".sha256.txt",
    )

    def resolve(
        self,
        release_data: dict,
    ) -> UpdateAsset:

        if not isinstance(
            release_data,
            dict,
        ):
            raise ValueError(
                "Release data must be a dictionary."
            )

        assets = release_data.get(
            "assets",
            [],
        )

        if not isinstance(
            assets,
            list,
        ):
            raise ValueError(
                "Release assets must be a list."
            )

        update_asset = (
            self._find_update_asset(
                assets
            )
        )

        if update_asset is None:
            raise ValueError(
                "No ZIP update asset found "
                "in the GitHub release."
            )

        checksum = (
            self._find_checksum_asset(
                assets
            )
        )

        sha256 = None

        if checksum is not None:

            sha256 = (
                checksum.get(
                    "sha256"
                )
            )

        return UpdateAsset(
            name=update_asset["name"],
            download_url=(
                update_asset["browser_download_url"]
            ),
            size=update_asset.get(
                "size"
            ),
            sha256=sha256,
        )

    def _find_update_asset(
        self,
        assets: list[dict],
    ) -> dict | None:

        candidates = []

        for asset in assets:

            name = asset.get(
                "name"
            )

            download_url = asset.get(
                "browser_download_url"
            )

            if not name or not download_url:
                continue

            if name.lower().endswith(
                self.ZIP_EXTENSIONS
            ):

                candidates.append(
                    asset
                )

        if not candidates:
            return None

        candidates.sort(
            key=lambda asset: (
                self._asset_priority(
                    asset["name"]
                ),
                asset["name"].lower(),
            )
        )

        return candidates[0]

    def _find_checksum_asset(
        self,
        assets: list[dict],
    ) -> dict | None:

        for asset in assets:

            name = asset.get(
                "name",
                "",
            )

            lowered = name.lower()

            if lowered.endswith(
                self.SHA256_SUFFIXES
            ):

                sha256 = asset.get(
                    "sha256"
                )

                if sha256:

                    return {
                        "name": name,
                        "sha256": sha256,
                    }

        return None

    @staticmethod
    def _asset_priority(
        name: str,
    ) -> int:

        lowered = name.lower()

        if (
            "thanos"
            in lowered
            and lowered.endswith(".zip")
        ):
            return 0

        return 1