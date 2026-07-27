from collections.abc import Sequence

from learning_lab.api.app import validate_runtime_assets
from learning_lab.config import build_paths
from learning_lab.ml.runtime import ModelRuntime
from learning_lab.ml.trace import load_reference_trace


ABS_TOLERANCE = 1e-4


def require_numeric_sequence(value: object, label: str) -> list[float]:
    if not isinstance(value, list):
        raise RuntimeError(f"{label} must be a list")
    result: list[float] = []
    for index, item in enumerate(value):
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise RuntimeError(f"{label}[{index}] must be numeric")
        result.append(float(item))
    return result


def assert_numeric_sequence_close(
    *,
    label: str,
    expected: Sequence[float],
    actual: Sequence[float],
) -> float:
    if len(expected) != len(actual):
        raise RuntimeError(
            f"{label} length mismatch: {len(expected)} != {len(actual)}"
        )
    deltas = [
        abs(float(expected_value) - float(actual_value))
        for expected_value, actual_value in zip(expected, actual)
    ]
    max_delta = max(deltas, default=0.0)
    if max_delta > ABS_TOLERANCE:
        index = deltas.index(max_delta)
        raise RuntimeError(
            f"{label} differs at index {index}: "
            f"expected={expected[index]}, actual={actual[index]}, "
            f"delta={max_delta:.8f}, tolerance={ABS_TOLERANCE:.8f}"
        )
    return max_delta


def assert_traces_equivalent(
    reference: dict[str, object],
    live: dict[str, object],
) -> float:
    for key in ("schema_version", "architecture_version", "predicted_digit"):
        if reference[key] != live[key]:
            raise RuntimeError(
                f"reference/live {key} mismatch: "
                f"{reference[key]!r} != {live[key]!r}"
            )
    if reference["input_pixels"] != live["input_pixels"]:
        raise RuntimeError("reference/live input_pixels mismatch")

    max_delta = assert_numeric_sequence_close(
        label="probabilities",
        expected=require_numeric_sequence(
            reference["probabilities"], "reference probabilities"
        ),
        actual=require_numeric_sequence(
            live["probabilities"], "live probabilities"
        ),
    )
    reference_layers = reference["layers"]
    live_layers = live["layers"]
    if not isinstance(reference_layers, list) or not isinstance(
        live_layers, list
    ):
        raise RuntimeError("reference/live layers must be lists")
    if len(reference_layers) != len(live_layers):
        raise RuntimeError(
            "reference/live layer count mismatch: "
            f"{len(reference_layers)} != {len(live_layers)}"
        )

    for reference_layer, live_layer in zip(reference_layers, live_layers):
        if not isinstance(reference_layer, dict) or not isinstance(live_layer, dict):
            raise RuntimeError("every trace layer must be an object")
        for key in ("id", "shape", "summary"):
            if reference_layer[key] != live_layer[key]:
                raise RuntimeError(
                    f"layer {reference_layer.get('id')} {key} mismatch: "
                    f"{reference_layer[key]!r} != {live_layer[key]!r}"
                )
        layer_id = str(reference_layer["id"])
        values_delta = assert_numeric_sequence_close(
            label=f"layer {layer_id} values",
            expected=require_numeric_sequence(
                reference_layer["values"], f"reference layer {layer_id} values"
            ),
            actual=require_numeric_sequence(
                live_layer["values"], f"live layer {layer_id} values"
            ),
        )
        extrema_delta = assert_numeric_sequence_close(
            label=f"layer {layer_id} extrema",
            expected=require_numeric_sequence(
                [reference_layer["min"], reference_layer["max"]],
                f"reference layer {layer_id} extrema",
            ),
            actual=require_numeric_sequence(
                [live_layer["min"], live_layer["max"]],
                f"live layer {layer_id} extrema",
            ),
        )
        max_delta = max(max_delta, values_delta, extrema_delta)
    return max_delta


def main() -> None:
    paths = build_paths()
    validate_runtime_assets(paths)
    reference = load_reference_trace(paths.reference_trace)
    pixels = reference["input_pixels"]
    if not isinstance(pixels, list):
        raise RuntimeError("reference input_pixels is not a list")

    runtime = ModelRuntime(paths)
    runtime.load("direct")
    live = runtime.infer(pixels)
    max_delta = assert_traces_equivalent(reference, live)

    print("runtime smoke check passed")
    print(f"prediction: {live['predicted_digit']}")
    print(f"layers: {len(live['layers'])}")
    print(
        "reference/live max absolute numeric delta: "
        f"{max_delta:.8f} (tolerance {ABS_TOLERANCE:.8f})"
    )


if __name__ == "__main__":
    main()
