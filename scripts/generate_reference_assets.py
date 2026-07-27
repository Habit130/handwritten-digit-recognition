import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from torchvision import datasets, transforms

from learning_lab.config import build_paths
from learning_lab.ml.model import DigitCNN
from learning_lab.ml.preprocess import pixels_to_tensor
from learning_lab.ml.trace import build_trace


def parse_args() -> argparse.Namespace:
    paths = build_paths()
    parser = argparse.ArgumentParser(description="生成真实固定参考轨迹")
    parser.add_argument(
        "--model",
        type=Path,
        default=paths.route_models["direct"],
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=paths.repo_root / "data",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = build_paths()
    state_dict = torch.load(args.model, map_location="cpu", weights_only=True)
    model = DigitCNN()
    model.load_state_dict(state_dict, strict=True)
    model.eval()

    dataset = datasets.MNIST(
        root=args.data_dir,
        train=False,
        download=True,
        transform=transforms.ToTensor(),
    )
    sample_tensor = None
    sample_label = None
    for image, label in dataset:
        if label == 7:
            sample_tensor = image
            sample_label = label
            break
    if sample_tensor is None or sample_label is None:
        raise RuntimeError("MNIST test dataset 中没有找到数字 7")

    pixels = [round(float(value), 5) for value in sample_tensor.flatten().tolist()]
    normalized = pixels_to_tensor(pixels)
    with torch.inference_mode():
        _, activations = model.forward_with_activations(normalized)
    trace = build_trace(
        activations=activations,
        input_pixels=pixels,
        source="reference",
        model_route="reference",
    )
    if trace["predicted_digit"] != sample_label:
        raise RuntimeError(
            "预训练模型没有正确识别固定样例："
            f"label={sample_label}, prediction={trace['predicted_digit']}"
        )

    paths.reference_trace.parent.mkdir(parents=True, exist_ok=True)
    paths.reference_trace.write_text(
        json.dumps(trace, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    image_values = (sample_tensor.squeeze(0).numpy() * 255).astype("uint8")
    paths.sample_image.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image_values, mode="L").save(paths.sample_image)
    print(f"参考轨迹：{paths.reference_trace}")
    print(f"固定样例：{paths.sample_image}")
    print(f"真实预测：{trace['predicted_digit']}")


if __name__ == "__main__":
    main()
