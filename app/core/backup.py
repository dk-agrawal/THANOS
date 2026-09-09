import shutil
from datetime import datetime, timezone
from pathlib import Path


class BackupManager:

    DEFAULT_BACKUP_DIRECTORY = (
        "data/update_backups"
    )

    EXCLUDED_NAMES = {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "data",
    }

    EXCLUDED_FILES = {
        ".env",
    }

    def __init__(
        self,
        backup_root: str | Path | None = None,
    ):
        self.backup_root = Path(
            backup_root
            or self.DEFAULT_BACKUP_DIRECTORY
        )

        self.backup_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_backup(
        self,
        source_root: str | Path,
    ) -> Path:

        source = Path(
            source_root
        ).resolve()

        if not source.exists():
            raise ValueError(
                "Source project directory does not exist."
            )

        if not source.is_dir():
            raise ValueError(
                "Source project path must be a directory."
            )

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )

        backup_path = (
            self.backup_root.resolve()
            / f"backup_{timestamp}"
        )

        backup_path.mkdir(
            parents=True,
            exist_ok=False,
        )

        for item in source.iterdir():

            if self._should_exclude(item):
                continue

            destination = (
                backup_path
                / item.name
            )

            if item.is_dir():

                shutil.copytree(
                    item,
                    destination,
                )

            else:

                shutil.copy2(
                    item,
                    destination,
                )

        return backup_path

    def restore_backup(
        self,
        backup_path: str | Path,
        source_root: str | Path,
    ) -> Path:

        backup = Path(
            backup_path
        ).resolve()

        source = Path(
            source_root
        ).resolve()

        if not backup.exists():
            raise ValueError(
                "Backup directory does not exist."
            )

        if not backup.is_dir():
            raise ValueError(
                "Backup path must be a directory."
            )

        if not source.exists():
            raise ValueError(
                "Source project directory does not exist."
            )

        if not source.is_dir():
            raise ValueError(
                "Source project path must be a directory."
            )

        backup_root = (
            self.backup_root.resolve()
        )

        if not self._is_within(
            backup,
            backup_root,
        ):
            raise ValueError(
                "Backup path is outside the "
                "configured backup directory."
            )

        for item in source.iterdir():

            if self._should_exclude(item):
                continue

            if item.is_dir():

                shutil.rmtree(item)

            else:

                item.unlink()

        for item in backup.iterdir():

            destination = (
                source
                / item.name
            )

            if item.is_dir():

                shutil.copytree(
                    item,
                    destination,
                )

            else:

                shutil.copy2(
                    item,
                    destination,
                )

        return source

    def list_backups(self) -> list[Path]:

        if not self.backup_root.exists():
            return []

        backups = [
            item
            for item in self.backup_root.iterdir()
            if item.is_dir()
        ]

        backups.sort(
            key=lambda item: item.name,
            reverse=True,
        )

        return backups

    def _should_exclude(
        self,
        path: Path,
    ) -> bool:

        if path.name in self.EXCLUDED_NAMES:
            return True

        if (
            path.is_file()
            and path.name in self.EXCLUDED_FILES
        ):
            return True

        return False

    @staticmethod
    def _is_within(
        path: Path,
        parent: Path,
    ) -> bool:

        try:

            path.relative_to(parent)

            return True

        except ValueError:

            return False