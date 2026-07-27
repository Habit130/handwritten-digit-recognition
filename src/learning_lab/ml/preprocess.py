import math
from collections.abc import Sequence

import torch
from torch import Tensor

from learning_lab.errors import LabError


MNIST_MEAN = 0.1307
MNIST_STD = 0.3081
PIXEL_COUNT = 28 * 28


def pixels_to_tensor(pixels: Sequence[float]) -> Tensor:
    if len(pixels) != PIXEL_COUNT:
        raise LabError(
            stage="input_validation",
            message="手写输入必须包含 784 个像素。",
            detail=f"received {len(pixels)} pixels; expected {PIXEL_COUNT}",
            status_code=422,
        )

    values = [float(value) for value in pixels]
    invalid_index = next(
        (
            index
            for index, value in enumerate(values)
            if not math.isfinite(value) or value < 0.0 or value > 1.0
        ),
        None,
    )
    if invalid_index is not None:
        raise LabError(
            stage="input_validation",
            message="每个像素都必须是 0 到 1 之间的有限数值。",
            detail=f"pixels[{invalid_index}]={values[invalid_index]!r}",
            status_code=422,
        )

    tensor = torch.tensor(values, dtype=torch.float32).reshape(1, 1, 28, 28)
    return (tensor - MNIST_MEAN) / MNIST_STD
