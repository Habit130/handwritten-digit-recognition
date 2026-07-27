import json
from pathlib import Path

import pytest
import torch

from learning_lab.errors import LabError
from learning_lab.ml.model import DigitCNN
from learning_lab.ml.trace import build_trace, load_reference_trace


def _reference_trace() -> dict[str, object]:
    model = DigitCNN().eval()
    with torch.inference_mode():
        _, activations = model.forward_with_activations(
            torch.zeros((1, 1, 28, 28), dtype=torch.float32)
        )
    return build_trace(
        activations=activations,
        input_pixels=[0.0] * 784,
        source="reference",
        model_route="reference",
    )


def test_reference_trace_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "reference.json"
    trace = _reference_trace()
    path.write_text(json.dumps(trace), encoding="utf-8")

    loaded = load_reference_trace(path)

    assert loaded == trace
    assert loaded["source"] == "reference"


def test_reference_trace_rejects_architecture_drift(tmp_path: Path) -> None:
    path = tmp_path / "reference.json"
    trace = _reference_trace()
    trace["architecture_version"] = "other-network"
    path.write_text(json.dumps(trace), encoding="utf-8")

    with pytest.raises(LabError) as caught:
        load_reference_trace(path)

    assert caught.value.stage == "asset_validation"
