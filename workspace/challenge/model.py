"""核心挑战 1：完成与展示契约完全一致的 DigitCNN。"""

import torch
from torch import Tensor, nn


class DigitCNN(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        # TODO 1: 定义 conv1、conv2、fc1、fc2。
        # 精确结构见 docs/product/IMPLEMENTATION-SPEC.md。
        raise NotImplementedError("TODO 1：请完成标准网络的四个可学习层")

    def forward(self, inputs: Tensor) -> Tensor:
        # TODO 2: 按“卷积 → ReLU → 池化”两次，再 Flatten 和全连接。
        # 训练和推理必须共享这个 forward()。
        raise NotImplementedError("TODO 2：请完成标准网络的 forward()")
