from dataclasses import dataclass
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]


@dataclass(frozen=True)
class LabPaths:
    repo_root: Path
    web_dist: Path
    reference_trace: Path
    sample_image: Path
    route_models: dict[str, Path]
    route_code: dict[str, tuple[Path, ...]]


def build_paths(repo_root: Path = REPO_ROOT) -> LabPaths:
    root = repo_root.resolve()
    return LabPaths(
        repo_root=root,
        web_dist=root / "web" / "dist",
        reference_trace=root / "assets" / "traces" / "reference.json",
        sample_image=root / "assets" / "samples" / "reference-7.png",
        route_models={
            "direct": root / "assets" / "models" / "mnist_cnn.pth",
            "practical": root / "workspace" / "practical" / "model.pth",
            "challenge": root / "workspace" / "challenge" / "model.pth",
        },
        route_code={
            "direct": (
                root / "src" / "learning_lab" / "ml" / "model.py",
            ),
            "practical": (
                root / "workspace" / "practical" / "train.py",
                root / "src" / "learning_lab" / "ml" / "model.py",
            ),
            "challenge": (
                root / "workspace" / "challenge" / "train.py",
                root / "workspace" / "challenge" / "model.py",
            ),
        },
    )
