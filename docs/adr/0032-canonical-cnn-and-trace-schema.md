# ADR-0032：冻结精确 CNN、预处理和轨迹 schema

## 状态

已接受

## 背景

网络结构、模型参数、网页节点、代码对照、参考轨迹和实时轨迹必须逐项一致。仅有“LeNet-style”不足以形成可验证的实现契约。

## 决策

首个架构版本命名为 `mnist-lenet-v1`，输入与网络固定如下：

1. 输入：`1×28×28`
2. `Conv2d(1, 8, kernel_size=5)`：`8×24×24`
3. `ReLU`
4. `MaxPool2d(2)`：`8×12×12`
5. `Conv2d(8, 16, kernel_size=5)`：`16×8×8`
6. `ReLU`
7. `MaxPool2d(2)`：`16×4×4`
8. `Flatten`：`256`
9. `Linear(256, 64)`
10. `ReLU`
11. `Linear(64, 10)`：十个 logits
12. `Softmax(dim=1)`：十类概率，仅用于解释和展示

标准输入使用 MNIST 的灰度语义，缩放到 `[0, 1]` 后以 `mean=0.1307`、`std=0.3081` 归一化。浏览器手写内容先按非空边界裁剪，保持比例缩放到 `20×20`，再按质量中心放入 `28×28` 画布。

网络展示契约使用稳定 ID：

`input`、`conv1`、`relu1`、`pool1`、`conv2`、`relu2`、`pool2`、`flatten`、`fc1`、`relu3`、`logits`、`probabilities`。

参考轨迹和实时轨迹使用同一个 JSON schema，至少包含：

- `schema_version`
- `architecture_version`
- `source`
- 输入、预测类别和十类概率
- 按稳定 ID 排列的层数据：名称、类型、shape、数值、最小值、最大值和教学摘要

模型产物只保存该结构的 raw `state_dict`。

## 后果

任何会改变 shape、参数名称、预处理或 layer ID 的修改都是架构代际变更。训练、推理、参考轨迹和网页不能分别演化。
