import zipfile

import pytest

from app.core.update_installer import UpdateInstaller


def create_test_zip(
    zip_path,
):

    with zipfile.ZipFile(
        zip_path,
        "w",
    ) as archive:

        archive.writestr(
            "app/test.py",
            "print('THANOS')",
        )

        archive.writestr(
            "run.py",
            "print('RUN')",
        )


def test_prepare_package(
    tmp_path,
):

    package = (
        tmp_path
        / "thanos_update.zip"
    )

    create_test_zip(
        package
    )

    installer = UpdateInstaller(
        temp_root=tmp_path / "temp"
    )

    extracted = installer.prepare_package(
        package
    )

    assert extracted.exists()
    assert extracted.is_dir()

    assert (
        extracted
        / "app"
        / "test.py"
    ).exists()

    assert (
        extracted
        / "run.py"
    ).exists()


def test_validate_package(
    tmp_path,
):

    package = (
        tmp_path
        / "thanos_update.zip"
    )

    create_test_zip(
        package
    )

    installer = UpdateInstaller(
        temp_root=tmp_path / "temp"
    )

    extracted = installer.prepare_package(
        package
    )

    assert installer.validate_package(
        extracted
    ) is True


def test_cleanup(
    tmp_path,
):

    package = (
        tmp_path
        / "thanos_update.zip"
    )

    create_test_zip(
        package
    )

    installer = UpdateInstaller(
        temp_root=tmp_path / "temp"
    )

    extracted = installer.prepare_package(
        package
    )

    assert extracted.exists()

    installer.cleanup(
        extracted
    )

    assert not extracted.exists()


def test_invalid_package(
    tmp_path,
):

    package = (
        tmp_path
        / "invalid.zip"
    )

    package.write_text(
        "not a zip"
    )

    installer = UpdateInstaller(
        temp_root=tmp_path / "temp"
    )

    with pytest.raises(
        ValueError,
        match="valid ZIP",
    ):

        installer.prepare_package(
            package
        )


def test_path_traversal_is_blocked(
    tmp_path,
):

    package = (
        tmp_path
        / "malicious.zip"
    )

    with zipfile.ZipFile(
        package,
        "w",
    ) as archive:

        archive.writestr(
            "../../evil.py",
            "malicious",
        )

        archive.writestr(
            "run.py",
            "print('RUN')",
        )

    installer = UpdateInstaller(
        temp_root=tmp_path / "temp"
    )

    with pytest.raises(
        ValueError,
        match="path traversal",
    ):

        installer.prepare_package(
            package
        )


def test_blocked_env_is_rejected(
    tmp_path,
):

    package = (
        tmp_path
        / "blocked.zip"
    )

    with zipfile.ZipFile(
        package,
        "w",
    ) as archive:

        archive.writestr(
            ".env",
            "SECRET=value",
        )

        archive.writestr(
            "run.py",
            "print('RUN')",
        )

    installer = UpdateInstaller(
        temp_root=tmp_path / "temp"
    )

    with pytest.raises(
        ValueError,
        match="blocked path",
    ):

        installer.prepare_package(
            package
        )


def test_missing_required_file_is_rejected(
    tmp_path,
):

    package = (
        tmp_path
        / "incomplete.zip"
    )

    with zipfile.ZipFile(
        package,
        "w",
    ) as archive:

        archive.writestr(
            "app/test.py",
            "print('TEST')",
        )

    installer = UpdateInstaller(
        temp_root=tmp_path / "temp"
    )

    with pytest.raises(
        ValueError,
        match="structure is invalid",
    ):

        installer.prepare_package(
            package
        )