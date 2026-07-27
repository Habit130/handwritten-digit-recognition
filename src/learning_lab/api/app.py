from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from learning_lab import __version__
from learning_lab.api.schemas import InferenceRequest
from learning_lab.config import LabPaths, build_paths
from learning_lab.content.routes import build_routes
from learning_lab.errors import LabError
from learning_lab.ml.contract import build_contract
from learning_lab.ml.runtime import ModelRuntime
from learning_lab.ml.trace import load_reference_trace


def _read_route_code(route: str, paths: LabPaths) -> dict[str, object]:
    allowed_files = paths.route_code.get(route)
    if allowed_files is None:
        raise LabError(
            stage="route_validation",
            message="未知的挑战路线。",
            detail=f"route {route!r} is not allowed",
            status_code=404,
        )

    files: list[dict[str, str]] = []
    for file_path in allowed_files:
        resolved = file_path.resolve()
        try:
            relative_path = resolved.relative_to(paths.repo_root)
        except ValueError as error:
            raise LabError(
                stage="code_load",
                message="教学代码路径越出了项目目录。",
                detail=str(resolved),
                status_code=500,
            ) from error
        if not resolved.is_file():
            raise LabError(
                stage="code_load",
                message="挑战路线的教学代码不存在。",
                detail=f"missing file: {resolved}",
                status_code=500,
            )
        try:
            content = resolved.read_text(encoding="utf-8")
        except OSError as error:
            raise LabError(
                stage="code_load",
                message="挑战路线的教学代码无法读取。",
                detail=f"{type(error).__name__}: {error}",
                status_code=500,
            ) from error
        files.append({"path": relative_path.as_posix(), "content": content})
    return {"route": route, "files": files}


def create_app(
    *,
    paths: LabPaths | None = None,
    runtime: ModelRuntime | None = None,
    mount_static: bool = True,
) -> FastAPI:
    resolved_paths = paths or build_paths()
    model_runtime = runtime or ModelRuntime(resolved_paths)

    app = FastAPI(
        title="手写数字识别学习实验室",
        version=__version__,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.paths = resolved_paths
    app.state.runtime = model_runtime
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["127.0.0.1", "localhost", "testserver"],
    )

    @app.middleware("http")
    async def add_security_headers(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'none'; "
            "frame-ancestors 'none'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.exception_handler(LabError)
    async def handle_lab_error(_request: Request, error: LabError) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content=error.as_payload())

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(
        _request: Request, error: RequestValidationError
    ) -> JSONResponse:
        lab_error = LabError(
            stage="request_validation",
            message="请求数据不符合本地 API 契约。",
            detail=str(error),
            status_code=422,
        )
        return JSONResponse(
            status_code=lab_error.status_code,
            content=lab_error.as_payload(),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        _request: Request, error: Exception
    ) -> JSONResponse:
        lab_error = LabError(
            stage="internal",
            message="本地运行时发生未预期错误。",
            detail=f"{type(error).__name__}: {error}",
            status_code=500,
        )
        return JSONResponse(
            status_code=lab_error.status_code,
            content=lab_error.as_payload(),
        )

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "version": __version__,
            "model": model_runtime.status(),
        }

    @app.get("/api/contract")
    def contract() -> dict[str, object]:
        return build_contract()

    @app.get("/api/reference-trace")
    def reference_trace() -> dict[str, object]:
        return load_reference_trace(resolved_paths.reference_trace)

    @app.get("/api/routes")
    def routes() -> list[dict[str, object]]:
        return build_routes(resolved_paths)

    @app.get("/api/code/{route}")
    def route_code(route: str) -> dict[str, object]:
        return _read_route_code(route, resolved_paths)

    @app.post("/api/models/{route}/load")
    def load_model(route: str) -> dict[str, object]:
        return model_runtime.load(route)

    @app.get("/api/models/status")
    def model_status() -> dict[str, object]:
        return model_runtime.status()

    @app.post("/api/infer")
    def infer(request: InferenceRequest) -> dict[str, object]:
        return model_runtime.infer(request.pixels)

    if mount_static:
        index_path = resolved_paths.web_dist / "index.html"
        if not index_path.is_file():
            raise RuntimeError(
                "预构建 Web 资产缺失："
                f"{index_path}。维护者必须先在 web/ 中运行 npm run build。"
            )
        app.mount(
            "/",
            StaticFiles(directory=resolved_paths.web_dist, html=True),
            name="web",
        )

    return app


def validate_runtime_assets(paths: LabPaths) -> None:
    required_files: tuple[Path, ...] = (
        paths.web_dist / "index.html",
        paths.reference_trace,
        paths.sample_image,
        paths.route_models["direct"],
    )
    missing = [str(path) for path in required_files if not path.is_file()]
    if missing:
        joined = "\n".join(f"- {path}" for path in missing)
        raise RuntimeError(f"学习实验室缺少固定运行资产：\n{joined}")
