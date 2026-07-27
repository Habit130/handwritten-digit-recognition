from collections.abc import Mapping
from pathlib import Path

import torch
from torch import Tensor

from learning_lab.config import LabPaths
from learning_lab.errors import LabError
from learning_lab.ml.model import DigitCNN
from learning_lab.ml.preprocess import pixels_to_tensor
from learning_lab.ml.trace import build_trace


class ModelRuntime:
    def __init__(self, paths: LabPaths) -> None:
        self._paths = paths
        self._model: DigitCNN | None = None
        self._route: str | None = None

    @property
    def route(self) -> str | None:
        return self._route

    def status(self) -> dict[str, object]:
        return {
            "loaded": self._model is not None,
            "route": self._route,
            "model_path": (
                str(self._paths.route_models[self._route].relative_to(self._paths.repo_root))
                if self._route is not None
                else None
            ),
        }

    def load(self, route: str) -> dict[str, object]:
        model_path = self._paths.route_models.get(route)
        if model_path is None:
            raise LabError(
                stage="route_validation",
                message="未知的挑战路线。",
                detail=f"route {route!r} is not allowed",
                status_code=404,
            )
        if not model_path.is_file():
            raise LabError(
                stage="model_load",
                message="指定路线的模型文件不存在。",
                detail=f"missing file: {model_path}",
                status_code=404,
            )

        try:
            state_dict = torch.load(
                model_path,
                map_location="cpu",
                weights_only=True,
            )
        except Exception as error:
            raise LabError(
                stage="model_load",
                message="无法读取模型文件。",
                detail=f"{type(error).__name__}: {error}",
            ) from error

        if not isinstance(state_dict, Mapping) or not state_dict:
            raise LabError(
                stage="model_validation",
                message="模型文件必须是非空的 raw state_dict。",
                detail=f"received {type(state_dict).__name__}",
            )
        if not all(
            isinstance(key, str) and isinstance(value, Tensor)
            for key, value in state_dict.items()
        ):
            raise LabError(
                stage="model_validation",
                message="模型文件必须只包含 raw state_dict 的参数 tensor。",
                detail="every key must be str and every value must be torch.Tensor",
            )

        model = DigitCNN()
        try:
            model.load_state_dict(state_dict, strict=True)
            model.eval()
            with torch.inference_mode():
                output = model(torch.zeros((1, 1, 28, 28), dtype=torch.float32))
        except Exception as error:
            raise LabError(
                stage="model_validation",
                message="模型参数与标准网络结构不兼容。",
                detail=f"{type(error).__name__}: {error}",
            ) from error

        if tuple(output.shape) != (1, 10) or not torch.isfinite(output).all():
            raise LabError(
                stage="model_validation",
                message="模型没有产生有效的十分类输出。",
                detail=(
                    f"shape={list(output.shape)}, "
                    f"all_finite={bool(torch.isfinite(output).all())}"
                ),
            )

        self._model = model
        self._route = route
        return self.status()

    def infer(self, pixels: list[float]) -> dict[str, object]:
        if self._model is None or self._route is None:
            raise LabError(
                stage="inference",
                message="真实实验前必须先加载一条路线的模型。",
                detail="no model is currently loaded",
                status_code=409,
            )

        inputs = pixels_to_tensor(pixels)
        try:
            with torch.inference_mode():
                _, activations = self._model.forward_with_activations(inputs)
        except Exception as error:
            raise LabError(
                stage="inference",
                message="模型推理失败。",
                detail=f"{type(error).__name__}: {error}",
                status_code=500,
            ) from error

        return build_trace(
            activations=activations,
            input_pixels=pixels,
            source="live",
            model_route=self._route,
        )
