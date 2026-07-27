# ADR-0031：采用 Python 3.11、FastAPI、React 与预构建 Web 资产

## 状态

已接受

## 背景

全局策略已经确定：学习者只维护一个 Python 环境，通过一个命令启动本地学习实验室；Node.js 只能属于维护者构建环境。实现仍需明确 Python、API、Web 和资产交付方案。

## 决策

- 项目要求 Python `>=3.11,<3.13`。
- 本地应用使用 FastAPI 与 Uvicorn，只监听 `127.0.0.1`。
- Web 使用 React、TypeScript 和 Vite，由维护者构建。
- `web/dist/` 是正式运行资产并提交到仓库；学习者运行产品不需要 Node.js。
- Python 包、固定教学资产、学习者工作区和预构建 Web 资产保持在同一个仓库。
- 根目录的 `start.command`、`start.cmd` 和 `start.sh` 是面向学习者的平台启动入口，共同调用 `scripts/launch.py`。
- 启动器在首次运行时创建唯一的项目 `.venv` 并安装锁定依赖，后续直接复用；已有但不完整的环境必须显式失败。
- `.venv` 中的 `python -m learning_lab` 是启动器使用的内部运行入口。

## 后果

学习者只需操作项目根目录启动入口，实际运行路径仍然只有 Python；维护者需要维护 Web 源码、lockfile 和已构建资产的一致性。任何缺失的 Web 构建资产都会显式阻止启动，不允许运行时从 CDN 获取替代资产。
