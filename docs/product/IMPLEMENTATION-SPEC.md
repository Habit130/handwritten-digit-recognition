# 首个版本实现规格

## 状态与权威

本文把 [`GLOBAL-STRATEGY.md`](GLOBAL-STRATEGY.md) 的全局边界落实为首个可运行版本。产品边界冲突时以全局策略为准；代码、API、测试和教学资产必须符合本文。

关联决策：[ADR-0031](../adr/0031-python-fastapi-react-delivery-stack.md)、[ADR-0032](../adr/0032-canonical-cnn-and-trace-schema.md)、[ADR-0033](../adr/0033-three-guided-challenge-routes.md)。

## 运行边界

```text
browser
  └── http://127.0.0.1:8000
      ├── prebuilt React application
      └── /api/*
          └── Python learning_lab package
              ├── canonical PyTorch model
              ├── fixed model allowlist
              ├── reference trace
              └── learner workspace
```

- Python：`>=3.11,<3.13`
- 机器学习：PyTorch `2.13.0`、torchvision `0.28.0`
- 本地 API：FastAPI `0.140.0`、Uvicorn `0.51.0`
- Web：React `19.2.8`、TypeScript `7.0.2`、Vite `8.1.5`
- 运行地址：`127.0.0.1:8000`
- 正式启动：`python -m learning_lab`
- Web 运行资产：`web/dist/`，不得使用 CDN

## 精确网络与输入

架构版本为 `mnist-lenet-v1`：

| layer ID | PyTorch 操作 | 输出 shape |
| --- | --- | --- |
| `input` | normalized input | `[1, 1, 28, 28]` |
| `conv1` | `Conv2d(1, 8, 5)` | `[1, 8, 24, 24]` |
| `relu1` | `ReLU` | `[1, 8, 24, 24]` |
| `pool1` | `MaxPool2d(2)` | `[1, 8, 12, 12]` |
| `conv2` | `Conv2d(8, 16, 5)` | `[1, 16, 8, 8]` |
| `relu2` | `ReLU` | `[1, 16, 8, 8]` |
| `pool2` | `MaxPool2d(2)` | `[1, 16, 4, 4]` |
| `flatten` | `Flatten` | `[1, 256]` |
| `fc1` | `Linear(256, 64)` | `[1, 64]` |
| `relu3` | `ReLU` | `[1, 64]` |
| `logits` | `Linear(64, 10)` | `[1, 10]` |
| `probabilities` | `Softmax(dim=1)` | `[1, 10]` |

输入 API 接收按行排列的 784 个 `[0, 1]` 灰度值。后端执行 `(pixel - 0.1307) / 0.3081`。浏览器画板负责：

1. 读取非空像素边界；
2. 保持比例缩放，使最长边为 20；
3. 按灰度质量中心平移到 `28×28` 中心；
4. 向后端发送 784 个像素。

## 模型产物

- 只接受 raw `state_dict` 字典。
- 参数名称和 shape 必须与 `mnist-lenet-v1` 完全一致。
- 使用 `torch.load(..., map_location="cpu", weights_only=True)`。
- 加载后立即使用固定全零输入做一次推理，验证输出为 `[1, 10]` 且数值有限。
- 不兼容、损坏或缺失时立即返回结构化错误；不得自动换用预训练模型。
- 学习者模型只需兼容并可运行，不设置准确率门槛。

## 网络展示契约与轨迹

契约由 Python 生成，Web 不复制网络拓扑。契约包含：

- `schema_version = "1.0"`
- `architecture_version = "mnist-lenet-v1"`
- 输入规范、类别列表
- 每层稳定 ID、中文名称、英文术语、操作类型、输出 shape、教学解释和代码锚点

轨迹 schema：

```json
{
  "schema_version": "1.0",
  "architecture_version": "mnist-lenet-v1",
  "source": "reference | live",
  "model_route": "reference | direct | practical | challenge",
  "predicted_digit": 7,
  "probabilities": [0.0],
  "input_pixels": [0.0],
  "layers": [
    {
      "id": "input",
      "shape": [1, 1, 28, 28],
      "values": [0.0],
      "min": 0.0,
      "max": 1.0,
      "summary": "..."
    }
  ]
}
```

所有 tensor 值按五位小数写入 JSON。`reference` 轨迹必须由固定预训练模型针对固定 MNIST 样例真实生成；`live` 轨迹只能由当前已加载模型和当前输入生成。

## 固定 API

API 只能提供以下能力：

| method | path | 作用 |
| --- | --- | --- |
| `GET` | `/api/health` | 运行状态和已加载路线 |
| `GET` | `/api/contract` | 网络展示契约 |
| `GET` | `/api/reference-trace` | 固定真实参考轨迹 |
| `GET` | `/api/routes` | 三档挑战说明和固定命令 |
| `GET` | `/api/code/{route}` | 读取 allowlist 中的教学代码 |
| `POST` | `/api/models/{route}/load` | 加载固定路线对应的 `.pth` |
| `GET` | `/api/models/status` | 当前模型状态 |
| `POST` | `/api/infer` | 对 784 个像素执行真实推理并返回实时轨迹 |

`route` 只允许 `direct`、`practical`、`challenge`。API 不接收文件路径、Python 代码或 shell command。Web 与 API 同源，不开启跨域访问。

错误返回：

```json
{
  "error": {
    "stage": "model_load",
    "message": "无法加载模型文件。",
    "detail": "original exception text"
  }
}
```

## 三档挑战

| route | 学习者责任 | 固定模型位置 |
| --- | --- | --- |
| `direct` / 直接运行 | 配置环境、确认预训练模型、加载并实验 | `assets/models/mnist_cnn.pth` |
| `practical` / 跟随训练 | 下载 MNIST、运行完整训练代码、保存并实验 | `workspace/practical/model.pth` |
| `challenge` / 核心挑战 | 在受控骨架完成三个核心 TODO、下载、训练、保存并实验 | `workspace/challenge/model.pth` |

训练在 terminal/IDE 中进行。Web 只展示真实源文件、任务、命令和产物验证结果，不执行训练、不记录进度。

## Web 信息架构

Web 只有三个一级工作区：

1. **教学推演**：自动重放固定 reference trace，支持暂停、前进、回退、重播、调速和 layer inspection。
2. **挑战路线**：切换三档责任说明，显示真实文件、只读代码和明确命令。
3. **真实实验**：选择路线、显式加载模型、鼠标手写、执行推理、展示 live trace。

教学推演与真实实验必须复用同一个网络舞台和 layer inspector。页面是桌面产品，最低内容宽度 `1100px`；窄窗口明确提示使用桌面宽度，不提供移动布局。

## 显式失败

以下情况必须阻止当前动作并保留原始错误：

- Python 版本不兼容；
- `web/dist/` 或固定资产缺失；
- route 不在 allowlist；
- 模型文件缺失、不是 raw `state_dict`、参数不兼容或推理失败；
- 输入不是 784 个有限的 `[0, 1]` 数值；
- reference trace 与当前 schema 或架构版本不一致。

不得静默回退到其他模型、模拟 trace、远程资源或默认输入。

## 验证门槛

- Python：模型 shape、预处理、兼容性、reference/live trace、API allowlist、错误语义。
- Web：TypeScript typecheck、单元测试、production build。
- 集成：启动后 API、静态资产、加载预训练模型和一次真实推理。
- 安全：仅 loopback、无 CORS、无任意路径/命令 API、运行时无 CDN/后台请求。
- 视觉：桌面浏览器中三个工作区、动画控制、layer inspection、画板和错误状态均完成截图检查。
- 跨平台：只有对应系统 CPU 路径产生真实 CI 或实机证据后才标记通过。
