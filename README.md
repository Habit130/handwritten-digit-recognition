# 手写数字识别学习实验室

一个面向 AI 初学者的 local-first 学习产品：先逐层看懂一次真实 MNIST 推理，再按不同挑战深度准备 `.pth`，最后用鼠标写数字并观察自己本机模型产生的实时内部数据。

产品不是通用训练平台。首个版本固定一套 `mnist-lenet-v1` CNN、MNIST `0–9` 和 `28×28` 灰度输入，让模型代码、训练、推理、动画节点和每层 tensor 始终一一对应。

## 快速开始

需要 Python 3.11 或 3.12。第一次使用先配置一次环境：

### macOS / Linux

```bash
python3.11 scripts/setup.py
source .venv/bin/activate
python -m learning_lab
```

### Windows PowerShell

```powershell
py -3.11 scripts/setup.py
.venv\Scripts\Activate.ps1
python -m learning_lab
```

环境配置完成后，每次只需激活 `.venv` 并运行：

```bash
python -m learning_lab
```

学习实验室只监听 `http://127.0.0.1:8000`，默认自动打开浏览器。需要只启动服务时使用 `python -m learning_lab --no-browser`。

## 三档挑战路线

| 路线 | 你负责什么 | 模型产物 |
| --- | --- | --- |
| 直接运行 | 配置环境、加载项目预训练模型、完成真实实验 | `assets/models/mnist_cnn.pth` |
| 跟随训练 | 下载 MNIST、运行完整训练代码、保存并实验 | `workspace/practical/model.pth` |
| 核心挑战 | 在受控骨架中完成模型、训练循环与保存 | `workspace/challenge/model.pth` |

完整训练路线：

```bash
python workspace/practical/train.py
```

自行训练模型不设置 accuracy 准入门槛。只要它是标准网络的 raw `state_dict`、可以严格加载并产生十分类输出，就可以进入真实实验；效果不好也是有价值的实验结果。

## 真实数据边界

- 教学推演重放 `assets/traces/reference.json`。它由项目预训练模型针对固定 MNIST 样例真实推理后生成。
- 真实实验的 trace 由当前明确加载的本地 `.pth` 和当前画板输入实时产生。
- 两种 trace 使用同一个 Python 网络展示契约和稳定 layer ID，不使用模拟数值。
- API 不接受任意文件路径、Python 代码或 shell command。
- 运行时无账号、无 telemetry、无 CDN、无后台网络请求。

## 项目结构

```text
assets/                 预训练模型、固定样例和真实参考轨迹
src/learning_lab/       PyTorch 模型、trace、runtime 与 loopback API
web/                    React/TypeScript 源码及提交到仓库的 dist
workspace/practical/    完整跟随训练路线
workspace/challenge/    留有三个核心 TODO 的受控骨架
tests/                  模型、输入、artifact、trace、API 与安全测试
docs/                   全局策略、实现规格与 ADR
```

全局产品边界见 [`docs/product/GLOBAL-STRATEGY.md`](docs/product/GLOBAL-STRATEGY.md)，精确实现契约见 [`docs/product/IMPLEMENTATION-SPEC.md`](docs/product/IMPLEMENTATION-SPEC.md)。

## 维护者验证

Python：

```bash
python -m pip install -e '.[dev]'
python -m pytest
python scripts/smoke_runtime.py
```

Web：

```bash
cd web
npm ci
npm run typecheck
npm run test
npm run build
```

Node.js 只用于维护者构建。学习者运行仓库中已经生成的 `web/dist/`，不需要安装 Node.js。

## 当前证据边界

仓库中的预训练模型在生成时经过 3 epochs，MNIST test accuracy 为 `98.72%`。该数值只描述随仓库发布的固定模型，不是学习者模型的门槛。

本地开发与浏览器视觉检查必须记录实际运行平台。macOS、Windows、Linux 的正式支持只在各自 CPU CI 或实机证据通过后成立，不能由单个平台结果推断。
