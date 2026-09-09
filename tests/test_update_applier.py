from app.core.update_applier import UpdateApplier


def test_apply_update(
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

    old_file = (
        project
        / "run.py"
    )

    old_file.write_text(
        "old code"
    )

    new_file = (
        package
        / "run.py"
    )

    new_file.write_text(
        "new code"
    )

    new_app_file = (
        package
        / "app"
        / "new.py"
    )

    new_app_file.parent.mkdir()

    new_app_file.write_text(
        "new feature"
    )

    applier = UpdateApplier()

    result = applier.apply(
        package_directory=package,
        project_root=project,
    )

    assert result["success"] is True

    assert (
        old_file.read_text()
        == "new code"
    )

    assert (
        project
        / "app"
        / "new.py"
    ).exists()

    assert result[
        "changed_file_count"
    ] == 2


def test_env_is_preserved(
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

    env_file = (
        project
        / ".env"
    )

    env_file.write_text(
        "SECRET=original"
    )

    (
        package
        / ".env"
    ).write_text(
        "SECRET=malicious"
    )

    (
        package
        / "run.py"
    ).write_text(
        "print('new')"
    )

    applier = UpdateApplier()

    applier.apply(
        package_directory=package,
        project_root=project,
    )

    assert (
        env_file.read_text()
        == "SECRET=original"
    )


def test_data_is_preserved(
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

    data_directory = (
        project
        / "data"
    )

    data_directory.mkdir()

    memory_file = (
        data_directory
        / "memory.json"
    )

    memory_file.write_text(
        "user data"
    )

    package_data = (
        package
        / "data"
    )

    package_data.mkdir()

    (
        package_data
        / "memory.json"
    ).write_text(
        "new data"
    )

    (
        package
        / "run.py"
    ).write_text(
        "print('new')"
    )

    applier = UpdateApplier()

    applier.apply(
        package_directory=package,
        project_root=project,
    )

    assert (
        memory_file.read_text()
        == "user data"
    )


def test_venv_is_preserved(
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

    venv = (
        project
        / ".venv"
    )

    venv.mkdir()

    marker = (
        venv
        / "marker.txt"
    )

    marker.write_text(
        "original"
    )

    package_venv = (
        package
        / ".venv"
    )

    package_venv.mkdir()

    (
        package_venv
        / "marker.txt"
    ).write_text(
        "new"
    )

    (
        package
        / "run.py"
    ).write_text(
        "print('new')"
    )

    applier = UpdateApplier()

    applier.apply(
        package_directory=package,
        project_root=project,
    )

    assert (
        marker.read_text()
        == "original"
    )


def test_missing_project_is_rejected(
    tmp_path,
):

    package = (
        tmp_path
        / "package"
    )

    package.mkdir()

    applier = UpdateApplier()

    try:

        applier.apply(
            package_directory=package,
            project_root=(
                tmp_path
                / "missing"
            ),
        )

        assert False

    except ValueError as error:

        assert "Project directory" in str(
            error
        )