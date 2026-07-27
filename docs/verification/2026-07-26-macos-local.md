# 2026-07-26 macOS 本地验证

## 结论

首个版本在当前 macOS arm64 主机上的 CPU 路径完成本地实现验证。该记录不替代 Windows 或 Linux 证据。

## 环境

- macOS 27.0（Build 26A5388g），arm64
- Python 3.11.15
- PyTorch 2.13.0
- Node.js 24.14.1
- npm 11.11.0
- 当前执行环境 `torch.backends.mps.is_available() == False`，因此本记录只覆盖 CPU baseline

## 自动验证

| 命令 | 结果 |
| --- | --- |
| `python -m pytest` | 25 passed |
| `npm run typecheck` | passed |
| `npm run test` | 2 passed |
| `npm run build` | passed，production assets 成功生成 |
| `python -m compileall -q src scripts workspace tests` | passed |
| `python scripts/smoke_runtime.py` | prediction 7；12 layers；本机 max absolute numeric delta `0.0` |
| `./start.command --no-browser` + `GET /api/health` | 根目录启动成功；HTTP 200；`Ctrl+C` 干净停止 |
| `git diff --check` | passed |

Pytest 产生一条 Starlette `TestClient` 关于未来 `httpx2` 的 deprecation warning；它来自测试工具适配层，不影响 runtime。该 warning 未被隐藏。

## GitHub Actions CPU matrix

Commit `3c4b437` 的 [CI run 30229455296](https://github.com/Habit130/handwritten-digit-recognition/actions/runs/30229455296) 全部通过：

- Python 3.11 · macOS：tests 与真实模型 smoke passed
- Python 3.11 · Windows：tests 与真实模型 smoke passed
- Python 3.11 · Linux：tests 与真实模型 smoke passed
- Python 3.12 · Linux：tests 与真实模型 smoke passed
- Web：locked install、typecheck、tests、production rebuild 和 committed asset diff passed

GitHub 对 `actions/checkout@v4`、`actions/setup-python@v5` 和 `actions/setup-node@v4` 发出 Node.js 20 action runtime deprecation annotation，并在 runner 中强制使用 Node.js 24。该 annotation 来自上游 GitHub Action 版本，不是学习实验室 runtime failure。

## 模型与固定资产

- 标准训练脚本运行 3 epochs。
- 每轮结果：
  - epoch 1：loss `0.2111`，test accuracy `97.89%`
  - epoch 2：loss `0.0611`，test accuracy `98.58%`
  - epoch 3：loss `0.0456`，test accuracy `98.72%`
- `assets/models/mnist_cnn.pth` 为 raw `state_dict`，约 84 KB。
- 固定 MNIST 数字 7 被真实识别为 7。
- `assets/traces/reference.json` 由保存后的输入像素、标准模型和真实本地 inference 生成。
- smoke check 使用同一保存输入和同一 `.pth` 重新实时推理。本机 12 层 tensor、概率与预测逐项相同；跨平台 CPU kernel 验证固定 schema、layer ID、shape、summary、输入和预测严格一致，并要求所有数值的 absolute delta 不超过 `1e-4`。

## 浏览器交互与视觉 QA

在本地 production build 上实际检查：

- 教学推演自动逐层播放，暂停、前进、回退、重播、调速和 layer inspection 可用。
- 12 个 Web 节点、shape、说明、真实 tensor 和代码 anchor 与 Python contract 一致。
- 三档挑战均可切换；核心挑战显示真实受控骨架与三个 TODO。
- 加载缺失的 challenge 模型会显式停止并显示原始路径，不回退到预训练模型。
- direct 模型严格加载成功；画板载入固定样例、整理为 `28×28` 后真实预测为 7。
- live trace 使用与教学推演相同的网络舞台，并显示当前模型的 12 层真实数据。
- 浏览器 console 无 error 或 warning。
- 1100px 宽度正常显示桌面产品；1099px 显示明确桌面宽度提示。

## 安全与本地边界

- Uvicorn 仅监听 `127.0.0.1:8000`。
- API 只有实现规格中列出的固定 endpoint。
- route 由 `direct`、`practical`、`challenge` allowlist 管理；API 不接收任意路径、Python 或 shell command。
- Trusted Host 拒绝非 `localhost`、`127.0.0.1` 和测试 host。
- 无 CORS middleware。
- production response 包含：
  - `Content-Security-Policy`，其中 `connect-src 'self'`
  - `Referrer-Policy: no-referrer`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
- 主页与仓库内 favicon 均返回 200；Web 不依赖 CDN。
- 服务停止后端口 8000 不再监听。

## 未覆盖

- Windows 与 Linux 的真实桌面浏览器视觉 QA 和终端人工上手流程尚未执行；CI 只证明这些平台的安装、tests、CPU 模型加载与 inference smoke。
- 当前记录不覆盖 MPS 或 CUDA；它们不是首个版本的必要路径。
