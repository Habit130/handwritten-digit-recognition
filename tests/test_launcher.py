import subprocess
from pathlib import Path

import pytest

from scripts import launch


def test_virtualenv_python_is_platform_specific(tmp_path: Path) -> None:
    assert launch.virtualenv_python(tmp_path, "darwin") == (
        tmp_path / ".venv" / "bin" / "python"
    )
    assert launch.virtualenv_python(tmp_path, "win32") == (
        tmp_path / ".venv" / "Scripts" / "python.exe"
    )


def test_existing_project_environment_is_reused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    environment_python = launch.virtualenv_python(tmp_path, "darwin")
    environment_python.parent.mkdir(parents=True)
    environment_python.touch()

    def unexpected_run(*args: object, **kwargs: object) -> None:
        raise AssertionError("不应重新配置已有环境")

    monkeypatch.setattr(subprocess, "run", unexpected_run)

    result = launch.ensure_project_environment(
        tmp_path,
        bootstrap_python="/usr/bin/python3.11",
        python_version=(3, 11),
        platform="darwin",
    )

    assert result == environment_python


def test_first_launch_creates_project_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    setup_script = tmp_path / "scripts" / "setup.py"
    setup_script.parent.mkdir()
    setup_script.touch()
    environment_python = launch.virtualenv_python(tmp_path, "darwin")
    commands: list[list[str]] = []

    def fake_run(
        command: list[str], *, cwd: Path, check: bool
    ) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        assert cwd == tmp_path
        assert check is True
        environment_python.parent.mkdir(parents=True)
        environment_python.touch()
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = launch.ensure_project_environment(
        tmp_path,
        bootstrap_python="/usr/bin/python3.12",
        python_version=(3, 12),
        platform="darwin",
    )

    assert result == environment_python
    assert commands == [["/usr/bin/python3.12", str(setup_script)]]


def test_incomplete_project_environment_fails_without_repair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".venv").mkdir()

    def unexpected_run(*args: object, **kwargs: object) -> None:
        raise AssertionError("不应覆盖不完整环境")

    monkeypatch.setattr(subprocess, "run", unexpected_run)

    with pytest.raises(RuntimeError, match="项目环境不完整"):
        launch.ensure_project_environment(
            tmp_path,
            bootstrap_python="/usr/bin/python3.11",
            python_version=(3, 11),
            platform="darwin",
        )


def test_first_launch_rejects_unsupported_python(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="Python 3.11 或 3.12"):
        launch.ensure_project_environment(
            tmp_path,
            bootstrap_python="/usr/bin/python3.13",
            python_version=(3, 13),
            platform="darwin",
        )


def test_keyboard_interrupt_exits_without_traceback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def interrupt() -> int:
        raise KeyboardInterrupt

    monkeypatch.setattr(launch, "run", interrupt)

    assert launch.main() == 130


def test_launcher_check_does_not_prepare_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_prepare(*args: object, **kwargs: object) -> None:
        raise AssertionError("启动器自检不应准备环境")

    monkeypatch.setattr(launch, "ensure_project_environment", unexpected_prepare)

    assert launch.run([launch.LAUNCHER_CHECK_FLAG]) == 0
