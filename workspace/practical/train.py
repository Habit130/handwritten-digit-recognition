"""完整训练路线：下载 MNIST、训练标准网络并保存 raw state_dict。"""

import argparse
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from learning_lab.ml.model import DigitCNN


REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="训练标准 MNIST CNN")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.001)
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


def build_loaders(data_dir: Path, batch_size: int) -> tuple[DataLoader, DataLoader]:
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
        ]
    )
    train_dataset = datasets.MNIST(
        root=data_dir,
        train=True,
        download=True,
        transform=transform,
    )
    test_dataset = datasets.MNIST(
        root=data_dir,
        train=False,
        download=True,
        transform=transform,
    )
    generator = torch.Generator().manual_seed(130)
    return (
        DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0,
            generator=generator,
        ),
        DataLoader(
            test_dataset,
            batch_size=512,
            shuffle=False,
            num_workers=0,
        ),
    )


def train_epoch(
    model: DigitCNN,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
) -> float:
    model.train()
    total_loss = 0.0
    total_samples = 0
    for images, labels in loader:
        optimizer.zero_grad()
        logits = model(images)
        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()

        batch_size = images.shape[0]
        total_loss += float(loss.item()) * batch_size
        total_samples += batch_size
    return total_loss / total_samples


def evaluate(model: DigitCNN, loader: DataLoader) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.inference_mode():
        for images, labels in loader:
            predictions = model(images).argmax(dim=1)
            correct += int((predictions == labels).sum().item())
            total += labels.numel()
    return correct / total


def main() -> None:
    args = parse_args()
    if args.epochs < 1:
        raise ValueError("--epochs 必须至少为 1")
    if args.batch_size < 1:
        raise ValueError("--batch-size 必须至少为 1")

    torch.manual_seed(130)
    train_loader, test_loader = build_loaders(args.data_dir, args.batch_size)
    model = DigitCNN()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(1, args.epochs + 1):
        loss = train_epoch(model, train_loader, optimizer, loss_fn)
        accuracy = evaluate(model, test_loader)
        print(
            f"epoch {epoch:02d}/{args.epochs:02d}  "
            f"loss={loss:.4f}  test_accuracy={accuracy:.2%}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), args.output)
    print(f"raw state_dict 已保存：{args.output}")


if __name__ == "__main__":
    main()
