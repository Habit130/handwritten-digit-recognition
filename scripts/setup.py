import subprocess
import sys
import venv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = REPO_ROOT / ".venv"


def main() -> None:
    if not ((3, 11) <= sys.version_info[:2] < (3, 13)):
        raise RuntimeError(
            "请使用 Python 3.11 或 3.12 运行本脚本；"
            f"当前版本是 {sys.version_info.major}.{sys.version_info.minor}。"
        )

    if not VENV_DIR.exists():
        print(f"创建项目环境：{VENV_DIR}")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)

    if sys.platform == "win32":
        python = VENV_DIR / "Scripts" / "python.exe"
    else:
        python = VENV_DIR / "bin" / "python"

    print("安装锁定的项目依赖……")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=REPO_ROOT,
        check=True,
    )
    subprocess.run(
        [str(python), "-m", "pip", "install", "-e", "."],
        cwd=REPO_ROOT,
        check=True,
    )
    print("\n项目环境配置完成。")


if __name__ == "__main__":
    main()
