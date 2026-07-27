import argparse
import sys
import threading
import webbrowser

import uvicorn

from learning_lab.api.app import create_app, validate_runtime_assets
from learning_lab.config import build_paths


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动手写数字识别学习实验室")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="启动服务但不自动打开浏览器",
    )
    return parser.parse_args()


def main() -> None:
    if not ((3, 11) <= sys.version_info[:2] < (3, 13)):
        raise RuntimeError(
            "Python 版本不兼容："
            f"当前是 {sys.version_info.major}.{sys.version_info.minor}，"
            "项目要求 Python 3.11 或 3.12。"
        )

    args = _parse_args()
    paths = build_paths()
    validate_runtime_assets(paths)
    app = create_app(paths=paths)
    url = "http://127.0.0.1:8000"
    print(f"学习实验室已准备：{url}")
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
