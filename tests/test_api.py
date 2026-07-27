import json
from pathlib import Path

import torch
from fastapi.testclient import TestClient

from learning_lab.api.app import create_app
from learning_lab.config import build_paths
from learning_lab.ml.model import DigitCNN
from learning_lab.ml.trace import build_trace


def _prepare_repo(root: Path) -> None:
    paths = build_paths(root)
    paths.route_models["direct"].parent.mkdir(parents=True)
    torch.save(DigitCNN().state_dict(), paths.route_models["direct"])

    for route_files in paths.route_code.values():
        for path in route_files:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# teaching source\n", encoding="utf-8")

    model = DigitCNN().eval()
    with torch.inference_mode():
        _, activations = model.forward_with_activations(
            torch.zeros((1, 1, 28, 28), dtype=torch.float32)
        )
    trace = build_trace(
        activations=activations,
        input_pixels=[0.0] * 784,
        source="reference",
        model_route="reference",
    )
    paths.reference_trace.parent.mkdir(parents=True)
    paths.reference_trace.write_text(json.dumps(trace), encoding="utf-8")


def test_fixed_api_supports_reference_code_load_and_live_inference(
    tmp_path: Path,
) -> None:
    _prepare_repo(tmp_path)
    client = TestClient(create_app(paths=build_paths(tmp_path), mount_static=False))

    health = client.get("/api/health")
    assert health.json()["status"] == "ok"
    assert "connect-src 'self'" in health.headers["content-security-policy"]
    assert health.headers["x-frame-options"] == "DENY"
    assert client.get("/api/contract").json()["architecture_version"] == (
        "mnist-lenet-v1"
    )
    assert client.get("/api/reference-trace").json()["source"] == "reference"
    assert len(client.get("/api/routes").json()) == 3
    assert client.get("/api/code/direct").json()["route"] == "direct"

    blocked = client.post("/api/infer", json={"pixels": [0.0] * 784})
    assert blocked.status_code == 409

    loaded = client.post("/api/models/direct/load")
    assert loaded.status_code == 200
    inferred = client.post("/api/infer", json={"pixels": [0.0] * 784})
    assert inferred.status_code == 200
    assert inferred.json()["source"] == "live"


def test_api_rejects_unknown_routes_invalid_input_and_untrusted_hosts(
    tmp_path: Path,
) -> None:
    _prepare_repo(tmp_path)
    client = TestClient(create_app(paths=build_paths(tmp_path), mount_static=False))

    unknown = client.post("/api/models/unknown/load")
    assert unknown.status_code == 404
    assert unknown.json()["error"]["stage"] == "route_validation"

    invalid = client.post("/api/infer", json={"pixels": [0.0] * 783})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["stage"] == "request_validation"

    untrusted = client.get("/api/health", headers={"host": "outside.example"})
    assert untrusted.status_code == 400
