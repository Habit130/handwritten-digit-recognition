from learning_lab.api.app import validate_runtime_assets
from learning_lab.config import build_paths
from learning_lab.ml.runtime import ModelRuntime
from learning_lab.ml.trace import load_reference_trace


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

    if live["predicted_digit"] != reference["predicted_digit"]:
        raise RuntimeError(
            "reference/live prediction mismatch: "
            f"{reference['predicted_digit']} != {live['predicted_digit']}"
        )
    if live["probabilities"] != reference["probabilities"]:
        raise RuntimeError("reference/live probability mismatch")
    if live["layers"] != reference["layers"]:
        raise RuntimeError("reference/live layer tensor mismatch")

    print("runtime smoke check passed")
    print(f"prediction: {live['predicted_digit']}")
    print(f"layers: {len(live['layers'])}")
    print("reference/live tensors: identical")


if __name__ == "__main__":
    main()
