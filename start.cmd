@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PROJECT_PYTHON=.venv\Scripts\python.exe"
    set "PYTHON_ARGS="
    goto run
)

py -3.11 -c "import sys; raise SystemExit(0 if sys.version_info[:2] in ((3, 11), (3, 12)) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "PROJECT_PYTHON=py"
    set "PYTHON_ARGS=-3.11"
    goto run
)

py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2] in ((3, 11), (3, 12)) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "PROJECT_PYTHON=py"
    set "PYTHON_ARGS=-3.12"
    goto run
)

python -c "import sys; raise SystemExit(0 if sys.version_info[:2] in ((3, 11), (3, 12)) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "PROJECT_PYTHON=python"
    set "PYTHON_ARGS="
    goto run
)

echo 启动失败：请先安装 Python 3.11 或 3.12。 1>&2
pause
exit /b 1

:run
"%PROJECT_PYTHON%" %PYTHON_ARGS% scripts\launch.py %*
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    if not "%EXIT_CODE%"=="130" (
        echo.
        echo 学习实验室未能启动（exit code: %EXIT_CODE%）。 1>&2
        pause
    )
)

exit /b %EXIT_CODE%
