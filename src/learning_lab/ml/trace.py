import json
import math
from collections import OrderedDict
from pathlib import Path
from typing import Literal

import torch
from torch import Tensor

from learning_lab.errors import LabError
from learning_lab.ml.contract import (
    ARCHITECTURE_VERSION,
    LAYERS,
    SCHEMA_VERSION,
)


TraceSource = Literal["reference", "live"]


def _rounded_values(tensor: Tensor) -> list[float]:
    return [
        round(float(value), 5)
        for value in tensor.detach().cpu().contiguous().flatten().tolist()
    ]


def build_trace(
    *,
    activations: OrderedDict[str, Tensor],
    input_pixels: list[float],
    source: TraceSource,
    model_route: str,
) -> dict[str, object]:
    expected_ids = [layer["id"] for layer in LAYERS]
    actual_ids = list(activations.keys())
    if actual_ids != expected_ids:
        raise LabError(
            stage="trace_generation",
            message="模型层与网络展示契约不一致。",
            detail=f"expected {expected_ids}; received {actual_ids}",
            status_code=500,
        )

    probabilities_tensor = activations["probabilities"]
    if tuple(probabilities_tensor.shape) != (1, 10):
        raise LabError(
            stage="trace_generation",
            message="模型输出 shape 与十分类契约不一致。",
            detail=f"received {list(probabilities_tensor.shape)}; expected [1, 10]",
            status_code=500,
        )

    probabilities = _rounded_values(probabilities_tensor)
    layers: list[dict[str, object]] = []
    for contract_layer, (layer_id, tensor) in zip(LAYERS, activations.items()):
        values = _rounded_values(tensor)
        if not values or not all(math.isfinite(value) for value in values):
            raise LabError(
                stage="trace_generation",
                message="模型产生了无法展示的中间数值。",
                detail=f"layer {layer_id} contains empty or non-finite values",
                status_code=500,
            )
        layers.append(
            {
                "id": layer_id,
                "shape": list(tensor.shape),
                "values": values,
                "min": min(values),
                "max": max(values),
                "summary": contract_layer["summary"],
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "architecture_version": ARCHITECTURE_VERSION,
        "source": source,
        "model_route": model_route,
        "predicted_digit": int(torch.argmax(probabilities_tensor, dim=1).item()),
        "probabilities": probabilities,
        "input_pixels": [round(float(value), 5) for value in input_pixels],
        "layers": layers,
    }


def load_reference_trace(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise LabError(
            stage="asset_load",
            message="固定参考轨迹不存在。",
            detail=f"missing file: {path}",
            status_code=500,
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LabError(
            stage="asset_load",
            message="固定参考轨迹无法读取。",
            detail=f"{type(error).__name__}: {error}",
            status_code=500,
        ) from error

    if payload.get("schema_version") != SCHEMA_VERSION:
        raise LabError(
            stage="asset_validation",
            message="固定参考轨迹的 schema 版本不兼容。",
            detail=(
                f"received {payload.get('schema_version')!r}; "
                f"expected {SCHEMA_VERSION!r}"
            ),
            status_code=500,
        )
    if payload.get("architecture_version") != ARCHITECTURE_VERSION:
        raise LabError(
            stage="asset_validation",
            message="固定参考轨迹的网络架构版本不兼容。",
            detail=(
                f"received {payload.get('architecture_version')!r}; "
                f"expected {ARCHITECTURE_VERSION!r}"
            ),
            status_code=500,
        )
    if payload.get("source") != "reference":
        raise LabError(
            stage="asset_validation",
            message="教学推演只能读取 reference 轨迹。",
            detail=f"received source={payload.get('source')!r}",
            status_code=500,
        )
    return payload
