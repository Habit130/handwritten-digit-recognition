import subprocess
import sys
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_PYTHON = {(3, 11), (3, 12)}
LAUNCHER_CHECK_FLAG = "--launcher-check"


def virtualenv_python(repo_root: Path, platform: str) -> Path:
    if platform == "win32":
        return repo_root / ".venv" / "Scripts" / "python.exe"
    return repo_root / ".venv" / "bin" / "python"


def ensure_project_environment(
    repo_root: Path,
    *,
    bootstrap_python: str,
    python_version: tuple[int, int],
    platform: str,
) -> Path:
    environment_dir = repo_root / ".venv"
    environment_python = virtualenv_python(repo_root, platform)

    if environment_python.is_file():
        return environment_python

    if environment_dir.exists():
        raise RuntimeError(
            f"项目环境不完整：{environment_python} 不存在。"
            "请删除损坏的 .venv 后重新启动。"
        )

    if python_version not in SUPPORTED_PYTHON:
        version = ".".join(str(part) for part in python_version)
        raise RuntimeError(
            f"首次启动需要 Python 3.11 或 3.12，当前版本是 {version}。"
        )

    print("首次启动：正在创建项目专用环境并安装依赖……", flush=True)
    subprocess.run(
        [bootstrap_python, str(repo_root / "scripts" / "setup.py")],
        cwd=repo_root,
        check=True,
    )

    if not environment_python.is_file():
        raise RuntimeError(
            f"环境配置命令已结束，但未生成预期解释器：{environment_python}"
        )
    return environment_python


def run(argv: Sequence[str] | None = None) -> int:
    arguments = list(argv if argv is not None else sys.argv[1:])
    if arguments == [LAUNCHER_CHECK_FLAG]:
        print("project launcher check passed")
        return 0

    environment_python = ensure_project_environment(
        REPO_ROOT,
        bootstrap_python=sys.executable,
        python_version=sys.version_info[:2],
        platform=sys.platform,
    )
    completed = subprocess.run(
        [str(environment_python), "-m", "learning_lab", *arguments],
        cwd=REPO_ROOT,
        check=False,
    )
    return completed.returncode


def main() -> int:
    try:
        return run()
    except KeyboardInterrupt:
        return 130
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"\n启动失败：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
