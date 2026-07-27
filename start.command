#!/bin/sh

set -u

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_ROOT" || exit 1

find_compatible_python() {
    for candidate in python3.11 python3.12 python3; do
        if command -v "$candidate" >/dev/null 2>&1 &&
            "$candidate" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 13) else 1)' >/dev/null 2>&1; then
            command -v "$candidate"
            return 0
        fi
    done
    return 1
}

if [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
    PROJECT_PYTHON="$PROJECT_ROOT/.venv/bin/python"
else
    PROJECT_PYTHON=$(find_compatible_python) || {
        echo "启动失败：请先安装 Python 3.11 或 3.12。" >&2
        EXIT_CODE=1
        PROJECT_PYTHON=
    }
fi

if [ -n "$PROJECT_PYTHON" ]; then
    "$PROJECT_PYTHON" "$PROJECT_ROOT/scripts/launch.py" "$@"
    EXIT_CODE=$?
fi

if [ "$EXIT_CODE" -ne 0 ] && [ "$EXIT_CODE" -ne 130 ]; then
    echo
    echo "学习实验室未能启动（exit code: ${EXIT_CODE}）。" >&2
    if [ -t 0 ]; then
        printf "按 Enter 键关闭窗口……"
        read -r close_window
    fi
fi

exit "$EXIT_CODE"
