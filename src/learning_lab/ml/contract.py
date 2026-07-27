from typing import TypedDict


SCHEMA_VERSION = "1.0"
ARCHITECTURE_VERSION = "mnist-lenet-v1"
CLASS_LABELS = tuple(str(value) for value in range(10))


class LayerContract(TypedDict):
    id: str
    name: str
    term: str
    operation: str
    output_shape: list[int]
    summary: str
    code_anchor: str


LAYERS: tuple[LayerContract, ...] = (
    {
        "id": "input",
        "name": "标准输入",
        "term": "Input",
        "operation": "normalize",
        "output_shape": [1, 1, 28, 28],
        "summary": "28×28 的灰度像素先转换为模型熟悉的数值范围。",
        "code_anchor": "layer:input",
    },
    {
        "id": "conv1",
        "name": "第一层卷积",
        "term": "Convolution 1",
        "operation": "Conv2d(1, 8, 5)",
        "output_shape": [1, 8, 24, 24],
        "summary": "8 个卷积核寻找笔画边缘和局部方向。",
        "code_anchor": "layer:conv1",
    },
    {
        "id": "relu1",
        "name": "第一次激活",
        "term": "ReLU 1",
        "operation": "ReLU",
        "output_shape": [1, 8, 24, 24],
        "summary": "保留正响应，让明显的局部特征继续传播。",
        "code_anchor": "layer:relu1",
    },
    {
        "id": "pool1",
        "name": "第一次池化",
        "term": "Max Pooling 1",
        "operation": "MaxPool2d(2)",
        "output_shape": [1, 8, 12, 12],
        "summary": "压缩空间尺寸，同时保留每个小区域最强的特征。",
        "code_anchor": "layer:pool1",
    },
    {
        "id": "conv2",
        "name": "第二层卷积",
        "term": "Convolution 2",
        "operation": "Conv2d(8, 16, 5)",
        "output_shape": [1, 16, 8, 8],
        "summary": "组合基础笔画，形成更完整的数字局部结构。",
        "code_anchor": "layer:conv2",
    },
    {
        "id": "relu2",
        "name": "第二次激活",
        "term": "ReLU 2",
        "operation": "ReLU",
        "output_shape": [1, 16, 8, 8],
        "summary": "强调第二组卷积发现的有效组合特征。",
        "code_anchor": "layer:relu2",
    },
    {
        "id": "pool2",
        "name": "第二次池化",
        "term": "Max Pooling 2",
        "operation": "MaxPool2d(2)",
        "output_shape": [1, 16, 4, 4],
        "summary": "把每张特征图收缩到 4×4，留下最关键的响应。",
        "code_anchor": "layer:pool2",
    },
    {
        "id": "flatten",
        "name": "展平",
        "term": "Flatten",
        "operation": "Flatten",
        "output_shape": [1, 256],
        "summary": "把 16 张 4×4 特征图排列成长度为 256 的向量。",
        "code_anchor": "layer:flatten",
    },
    {
        "id": "fc1",
        "name": "特征组合",
        "term": "Fully Connected 1",
        "operation": "Linear(256, 64)",
        "output_shape": [1, 64],
        "summary": "把局部特征组合为 64 个用于分类的高层证据。",
        "code_anchor": "layer:fc1",
    },
    {
        "id": "relu3",
        "name": "分类前激活",
        "term": "ReLU 3",
        "operation": "ReLU",
        "output_shape": [1, 64],
        "summary": "保留支持某些数字类别的正向证据。",
        "code_anchor": "layer:relu3",
    },
    {
        "id": "logits",
        "name": "类别分数",
        "term": "Logits",
        "operation": "Linear(64, 10)",
        "output_shape": [1, 10],
        "summary": "为数字 0 到 9 分别计算一个尚未归一化的分数。",
        "code_anchor": "layer:logits",
    },
    {
        "id": "probabilities",
        "name": "预测概率",
        "term": "Probabilities",
        "operation": "Softmax(dim=1)",
        "output_shape": [1, 10],
        "summary": "把十个分数转换为总和为 1 的概率分布。",
        "code_anchor": "layer:probabilities",
    },
)


def build_contract() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "architecture_version": ARCHITECTURE_VERSION,
        "input": {
            "shape": [1, 1, 28, 28],
            "pixel_range": [0.0, 1.0],
            "normalization": {"mean": 0.1307, "std": 0.3081},
        },
        "classes": list(CLASS_LABELS),
        "layers": list(LAYERS),
    }
