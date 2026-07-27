import math

import pytest

from learning_lab.errors import LabError
from learning_lab.ml.preprocess import MNIST_MEAN, MNIST_STD, pixels_to_tensor


def test_pixels_are_normalized_to_canonical_tensor() -> None:
    pixels = [0.0] * 784
    pixels[0] = 1.0

    tensor = pixels_to_tensor(pixels)

    assert list(tensor.shape) == [1, 1, 28, 28]
    assert tensor[0, 0, 0, 0].item() == pytest.approx((1.0 - MNIST_MEAN) / MNIST_STD)
    assert tensor[0, 0, 0, 1].item() == pytest.approx(
        (0.0 - MNIST_MEAN) / MNIST_STD
    )


@pytest.mark.parametrize(
    "pixels",
    (
        [0.0] * 783,
        [0.0] * 785,
        [0.0] * 783 + [-0.1],
        [0.0] * 783 + [1.1],
        [0.0] * 783 + [math.nan],
    ),
)
def test_invalid_pixels_fail_explicitly(pixels: list[float]) -> None:
    with pytest.raises(LabError) as caught:
        pixels_to_tensor(pixels)

    assert caught.value.stage == "input_validation"
