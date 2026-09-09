import shutil
import tempfile
import zipfile
from pathlib import Path


class UpdateInstaller:

    REQUIRED_FILES = {
        "run.py",
    }

    BLOCKED_NAMES = {
        ".env",
        ".git",
        ".venv",
        "__pycache__",
    }

    def __init__(
        self,
        temp_root: str | Path | None = None,
    ):
        if temp_root is None:
            self.temp_root = (
                Path(tempfile.gettempdir())
                / "thanos_updates"
            )
        else:
            self.temp_root = Path(temp_root)

        self.temp_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def prepare_package(
        self,
        package_path: str | Path,
    ) -> Path:

        package = Path(
            package_path
        ).resolve()

        if not package.exists():
            raise ValueError(
                "Update package does not exist."
            )

        if not package.is_file():
            raise ValueError(
                "Update package must be a file."
            )

        if not zipfile.is_zipfile(package):
            raise ValueError(
                "Update package must be a valid ZIP file."
            )

        self._validate_zip(
            package
        )

        extraction_dir = Path(
            tempfile.mkdtemp(
                prefix="update_",
                dir=self.temp_root,
            )
        )

        try:

            with zipfile.ZipFile(
                package,
                "r",
            ) as archive:

                archive.extractall(
                    extraction_dir
                )

            if not self.validate_package(
                extraction_dir
            ):
                raise ValueError(
                    "Update package structure is invalid."
                )

        except Exception:

            shutil.rmtree(
                extraction_dir,
                ignore_errors=True,
            )

            raise

        return extraction_dir

    def validate_package(
        self,
        package_directory: str | Path,
    ) -> bool:

        directory = Path(
            package_directory
        ).resolve()

        if not directory.exists():
            return False

        if not directory.is_dir():
            return False

        for required_file in self.REQUIRED_FILES:

            if not (
                directory / required_file
            ).is_file():

                return False

        return True

    def cleanup(
        self,
        package_directory: str | Path,
    ) -> None:

        directory = Path(
            package_directory
        ).resolve()

        if not directory.exists():
            return

        shutil.rmtree(
            directory,
            ignore_errors=True,
        )

    def _validate_zip(
        self,
        package: Path,
    ) -> None:

        with zipfile.ZipFile(
            package,
            "r",
        ) as archive:

            for entry in archive.infolist():

                name = entry.filename

                if not name:
                    continue

                entry_path = Path(name)

                if entry_path.is_absolute():
                    raise ValueError(
                        "Update package contains "
                        "an absolute path."
                    )

                if ".." in entry_path.parts:
                    raise ValueError(
                        "Update package contains "
                        "path traversal."
                    )

                parts = {
                    part.lower()
                    for part in entry_path.parts
                }

                blocked = {
                    name.lower()
                    for name in self.BLOCKED_NAMES
                }

                if parts.intersection(
                    blocked
                ):
                    raise ValueError(
                        "Update package contains "
                        "a blocked path."
                    )