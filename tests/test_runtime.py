from pathlib import Path

import pytest
import torch

from learning_lab.config import build_paths
from learning_lab.errors import LabError
from learning_lab.ml.model import DigitCNN
from learning_lab.ml.runtime import ModelRuntime


def _save_direct_model(root: Path) -> Path:
    paths = build_paths(root)
    model_path = paths.route_models["direct"]
    model_path.parent.mkdir(parents=True)
    torch.save(DigitCNN().state_dict(), model_path)
    return model_path


def test_runtime_requires_explicit_load(tmp_path: Path) -> None:
    runtime = ModelRuntime(build_paths(tmp_path))

    with pytest.raises(LabError) as caught:
        runtime.infer([0.0] * 784)

    assert caught.value.status_code == 409
    assert caught.value.stage == "inference"


def test_runtime_loads_strict_state_dict_and_returns_live_trace(
    tmp_path: Path,
) -> None:
    _save_direct_model(tmp_path)
    runtime = ModelRuntime(build_paths(tmp_path))

    status = runtime.load("direct")
    trace = runtime.infer([0.0] * 784)

    assert status["loaded"] is True
    assert status["route"] == "direct"
    assert trace["source"] == "live"
    assert trace["model_route"] == "direct"
    assert len(trace["probabilities"]) == 10
    assert len(trace["layers"]) == 12


def test_runtime_rejects_wrapped_state_dict(tmp_path: Path) -> None:
    model_path = _save_direct_model(tmp_path)
    torch.save({"state_dict": DigitCNN().state_dict()}, model_path)
    runtime = ModelRuntime(build_paths(tmp_path))

    with pytest.raises(LabError) as caught:
        runtime.load("direct")

    assert caught.value.stage == "model_validation"
    assert "raw state_dict" in caught.value.message


def test_runtime_does_not_fall_back_for_missing_route_model(tmp_path: Path) -> None:
    _save_direct_model(tmp_path)
    runtime = ModelRuntime(build_paths(tmp_path))

    with pytest.raises(LabError) as caught:
        runtime.load("practical")

    assert caught.value.status_code == 404
    assert "practical/model.pth" in caught.value.detail
    assert runtime.status()["loaded"] is False
