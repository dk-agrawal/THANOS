from pathlib import Path

from app.core.update_runner import UpdateRunner


class FakeBackupManager:

    def __init__(self):
        self.backup_created = False
        self.rollback_performed = False

    def create_backup(
        self,
        source_root,
    ) -> Path:

        self.backup_created = True

        backup = (
            Path(source_root).parent
            / "backup"
        )

        backup.mkdir(
            parents=True,
            exist_ok=True,
        )

        return backup

    def restore_backup(
        self,
        backup_path,
        source_root,
    ) -> Path:

        self.rollback_performed = True

        return Path(
            source_root
        )


class FakeUpdateApplier:

    def apply(
        self,
        package_directory,
        project_root,
    ) -> dict:

        return {
            "success": True,
            "changed_files": [
                "run.py"
            ],
            "changed_file_count": 1,
        }


class SuccessfulUpdateRunner(
    UpdateRunner
):

    def _run_tests(
        self,
        project_root,
    ) -> dict:

        return {
            "success": True,
            "return_code": 0,
            "stdout": "34 passed",
            "stderr": "",
        }


class FailedUpdateRunner(
    UpdateRunner
):

    def _run_tests(
        self,
        project_root,
    ) -> dict:

        return {
            "success": False,
            "return_code": 1,
            "stdout": "1 failed",
            "stderr": "Test failure",
        }


def test_successful_update_keeps_changes(
    tmp_path,
):

    project = (
        tmp_path
        / "project"
    )

    package = (
        tmp_path
        / "package"
    )

    project.mkdir()
    package.mkdir()

    backup_manager = (
        FakeBackupManager()
    )

    runner = SuccessfulUpdateRunner(
        backup_manager=backup_manager,
        update_applier=(
            FakeUpdateApplier()
        ),
    )

    result = runner.run(
        package_directory=package,
        project_root=project,
    )

    assert result["success"] is True
    assert result["rolled_back"] is False

    assert (
        backup_manager.backup_created
        is True
    )

    assert (
        backup_manager.rollback_performed
        is False
    )


def test_failed_update_rolls_back(
    tmp_path,
):

    project = (
        tmp_path
        / "project"
    )

    package = (
        tmp_path
        / "package"
    )

    project.mkdir()
    package.mkdir()

    backup_manager = (
        FakeBackupManager()
    )

    runner = FailedUpdateRunner(
        backup_manager=backup_manager,
        update_applier=(
            FakeUpdateApplier()
        ),
    )

    result = runner.run(
        package_directory=package,
        project_root=project,
    )

    assert result["success"] is False
    assert result["rolled_back"] is True

    assert (
        backup_manager.backup_created
        is True
    )

    assert (
        backup_manager.rollback_performed
        is True
    )

    assert (
        result["tests"]["success"]
        is False
    )


def test_update_result_contains_test_output(
    tmp_path,
):

    project = (
        tmp_path
        / "project"
    )

    package = (
        tmp_path
        / "package"
    )

    project.mkdir()
    package.mkdir()

    runner = SuccessfulUpdateRunner(
        backup_manager=(
            FakeBackupManager()
        ),
        update_applier=(
            FakeUpdateApplier()
        ),
    )

    result = runner.run(
        package_directory=package,
        project_root=project,
    )

    assert (
        result["tests"]["return_code"]
        == 0
    )

    assert (
        result["tests"]["stdout"]
        == "34 passed"
    )


def test_missing_project_is_rejected(
    tmp_path,
):

    package = (
        tmp_path
        / "package"
    )

    package.mkdir()

    runner = SuccessfulUpdateRunner(
        backup_manager=(
            FakeBackupManager()
        ),
        update_applier=(
            FakeUpdateApplier()
        ),
    )

    try:

        runner.run(
            package_directory=package,
            project_root=(
                tmp_path
                / "missing"
            ),
        )

        assert False

    except ValueError as error:

        assert (
            "Project directory"
            in str(error)
        )