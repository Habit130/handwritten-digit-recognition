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
- `python -m learning_lab` 是环境配置完成后的统一启动命令。
- 项目使用一个 `.venv`；安装脚本只负责创建该环境并安装项目锁定的 Python 依赖。

## 后果

学习者的运行路径只有 Python；维护者需要维护 Web 源码、lockfile 和已构建资产的一致性。任何缺失的 Web 构建资产都会显式阻止启动，不允许运行时从 CDN 获取替代资产。
