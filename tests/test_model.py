from collections import OrderedDict

import torch

from learning_lab.ml.contract import ARCHITECTURE_VERSION, LAYERS, build_contract
from learning_lab.ml.model import DigitCNN


def test_canonical_model_matches_presentation_contract() -> None:
    model = DigitCNN().eval()
    inputs = torch.zeros((1, 1, 28, 28), dtype=torch.float32)

    with torch.inference_mode():
        logits, activations = model.forward_with_activations(inputs)

    assert isinstance(activations, OrderedDict)
    assert list(activations) == [layer["id"] for layer in LAYERS]
    assert [list(tensor.shape) for tensor in activations.values()] == [
        layer["output_shape"] for layer in LAYERS
    ]
    assert tuple(logits.shape) == (1, 10)
    assert torch.allclose(
        activations["probabilities"].sum(dim=1),
        torch.ones(1),
    )


def test_contract_has_one_frozen_architecture() -> None:
    contract = build_contract()

    assert contract["architecture_version"] == ARCHITECTURE_VERSION
    assert contract["classes"] == [str(value) for value in range(10)]
    assert len(contract["layers"]) == 12
