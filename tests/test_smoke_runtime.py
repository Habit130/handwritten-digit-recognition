import pytest

from scripts.smoke_runtime import (
    ABS_TOLERANCE,
    assert_numeric_sequence_close,
)


def test_numeric_trace_comparison_accepts_cross_kernel_rounding_delta() -> None:
    max_delta = assert_numeric_sequence_close(
        label="layer conv1 values",
        expected=[-1.25, 0.0, 4.5],
        actual=[-1.24991, 0.00001, 4.49995],
    )

    assert max_delta == pytest.approx(0.00009)


def test_numeric_trace_comparison_rejects_material_delta() -> None:
    with pytest.raises(RuntimeError, match="delta="):
        assert_numeric_sequence_close(
            label="probabilities",
            expected=[0.1, 0.9],
            actual=[0.1 + ABS_TOLERANCE + 0.00001, 0.9],
        )
