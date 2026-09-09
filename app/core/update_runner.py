import subprocess
import sys
from pathlib import Path

from app.core.backup import BackupManager
from app.core.update_applier import UpdateApplier


class UpdateRunner:

    def __init__(
        self,
        backup_manager: BackupManager | None = None,
        update_applier: UpdateApplier | None = None,
    ):
        self.backup_manager = (
            backup_manager
            or BackupManager()
        )

        self.update_applier = (
            update_applier
            or UpdateApplier()
        )

    def run(
        self,
        package_directory: str | Path,
        project_root: str | Path,
    ) -> dict:

        project = Path(
            project_root
        ).resolve()

        package = Path(
            package_directory
        ).resolve()

        if not project.exists():
            raise ValueError(
                "Project directory does not exist."
            )

        if not package.exists():
            raise ValueError(
                "Update package directory does not exist."
            )

        backup_path = (
            self.backup_manager.create_backup(
                project
            )
        )

        try:

            apply_result = (
                self.update_applier.apply(
                    package_directory=package,
                    project_root=project,
                )
            )

            test_result = (
                self._run_tests(
                    project
                )
            )

            if test_result["success"]:

                return {
                    "success": True,
                    "rolled_back": False,
                    "backup": str(
                        backup_path
                    ),
                    "update": apply_result,
                    "tests": test_result,
                }

            rollback_path = (
                self.backup_manager.restore_backup(
                    backup_path=backup_path,
                    source_root=project,
                )
            )

            return {
                "success": False,
                "rolled_back": True,
                "backup": str(
                    backup_path
                ),
                "rollback": str(
                    rollback_path
                ),
                "update": apply_result,
                "tests": test_result,
            }

        except Exception as error:

            try:

                rollback_path = (
                    self.backup_manager.restore_backup(
                        backup_path=backup_path,
                        source_root=project,
                    )
                )

                return {
                    "success": False,
                    "rolled_back": True,
                    "backup": str(
                        backup_path
                    ),
                    "rollback": str(
                        rollback_path
                    ),
                    "error": str(error),
                }

            except Exception as rollback_error:

                raise RuntimeError(
                    "Update failed and automatic "
                    "rollback also failed: "
                    f"{rollback_error}"
                ) from error

    def _run_tests(
        self,
        project_root: Path,
    ) -> dict:

        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
        ]

        process = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        return {
            "success": (
                process.returncode == 0
            ),
            "return_code": (
                process.returncode
            ),
            "stdout": process.stdout,
            "stderr": process.stderr,
        }