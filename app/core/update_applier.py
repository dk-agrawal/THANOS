import shutil
from pathlib import Path


class UpdateApplier:

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

    def apply(
        self,
        package_directory: str | Path,
        project_root: str | Path,
    ) -> dict:

        package = Path(
            package_directory
        ).resolve()

        project = Path(
            project_root
        ).resolve()

        if not package.exists():
            raise ValueError(
                "Update package directory does not exist."
            )

        if not package.is_dir():
            raise ValueError(
                "Update package must be a directory."
            )

        if not project.exists():
            raise ValueError(
                "Project directory does not exist."
            )

        if not project.is_dir():
            raise ValueError(
                "Project root must be a directory."
            )

        changed_files = []
        created_directories = []

        for source in package.rglob("*"):

            relative_path = source.relative_to(
                package
            )

            if self._should_exclude(
                relative_path
            ):
                continue

            destination = (
                project
                / relative_path
            )

            if source.is_dir():

                if not destination.exists():

                    destination.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    created_directories.append(
                        str(relative_path)
                    )

                continue

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source,
                destination,
            )

            changed_files.append(
                str(relative_path)
            )

        return {
            "success": True,
            "changed_files": changed_files,
            "created_directories": (
                created_directories
            ),
            "changed_file_count": len(
                changed_files
            ),
        }

    def _should_exclude(
        self,
        relative_path: Path,
    ) -> bool:

        parts = relative_path.parts

        if not parts:
            return True

        if any(
            part in self.EXCLUDED_NAMES
            for part in parts
        ):
            return True

        if (
            relative_path.name
            in self.EXCLUDED_FILES
        ):
            return True

        return False