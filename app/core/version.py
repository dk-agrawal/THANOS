from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return (
            f"{self.major}."
            f"{self.minor}."
            f"{self.patch}"
        )

    def __lt__(
        self,
        other: "Version",
    ) -> bool:

        return (
            self.major,
            self.minor,
            self.patch,
        ) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            Version,
        ):
            return NotImplemented

        return (
            self.major,
            self.minor,
            self.patch,
        ) == (
            other.major,
            other.minor,
            other.patch,
        )


class VersionManager:

    CURRENT_VERSION = Version(
        major=0,
        minor=1,
        patch=0,
    )

    @classmethod
    def current_version(cls) -> Version:

        return cls.CURRENT_VERSION

    @classmethod
    def current_version_string(cls) -> str:

        return str(
            cls.CURRENT_VERSION
        )

    @classmethod
    def is_update_available(
        cls,
        latest_version: str,
    ) -> bool:

        latest = cls.parse(
            latest_version
        )

        return (
            cls.CURRENT_VERSION < latest
        )

    @staticmethod
    def parse(
        version: str,
    ) -> Version:

        cleaned = (
            version
            .strip()
            .lower()
            .removeprefix("v")
        )

        parts = cleaned.split(".")

        if len(parts) != 3:
            raise ValueError(
                "Version must use "
                "MAJOR.MINOR.PATCH format."
            )

        try:

            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2])

        except ValueError as error:

            raise ValueError(
                "Version must contain "
                "numeric values."
            ) from error

        if (
            major < 0
            or minor < 0
            or patch < 0
        ):

            raise ValueError(
                "Version values cannot "
                "be negative."
            )

        return Version(
            major=major,
            minor=minor,
            patch=patch,
        )