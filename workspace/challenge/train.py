"""核心挑战 2：在受控骨架中完成训练循环并保存 raw state_dict。"""

import argparse
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model import DigitCNN


REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核心训练代码挑战")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=REPO_ROOT / "data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("model.pth"),
    )
    return parser.parse_args()


def build_loader(data_dir: Path, batch_size: int) -> DataLoader:
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
        ]
    )
    dataset = datasets.MNIST(
        root=data_dir,
        train=True,
        download=True,
        transform=transform,
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )


def main() -> None:
    args = parse_args()
    torch.manual_seed(130)
    loader = build_loader(args.data_dir, args.batch_size)
    model = DigitCNN()
    loss_fn = nn.CrossEntropyLoss()

    # TODO 3: 创建 Adam optimizer；在每个 batch 中完成
    # zero_grad → forward → loss → backward → step。
    raise NotImplementedError("TODO 3：请完成训练循环")

    # 完成 TODO 3 后移除上面的异常，并启用以下两行：
    # args.output.parent.mkdir(parents=True, exist_ok=True)
    # torch.save(model.state_dict(), args.output)


if __name__ == "__main__":
    main()
