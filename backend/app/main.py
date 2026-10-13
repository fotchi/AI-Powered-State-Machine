import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .auth import get_current_user, user_from_websocket_token
from .database import init_db, reconcile_orphaned_runs
from .logging_config import logger
from .routers import auth, runs, scenarios, scripts, coverage, artifacts, audit, metrics
from .database import get_run
from .realtime import subscribe, unsubscribe


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    reconcile_orphaned_runs()
    logger.info("FLYNC backend started")
    yield


app = FastAPI(title="FLYNC Integration API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8443", "http://127.0.0.1:8443", "http://localhost:5173", "http://127.0.0.1:5173"],
    # Couvre l'accès via l'IP LAN de la machine (ex: http://192.168.155.1:8443) --
    # vite.config.ts écoute sur 0.0.0.0, donc le frontend est aussi joignable
    # par une IP réseau locale, pas seulement localhost/127.0.0.1 ci-dessus.
    allow_origin_regex=r"http://(192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}):(8443|5173)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - started) * 1000
        logger.exception(f"{request.method} {request.url.path} -> UNHANDLED EXCEPTION ({duration_ms:.1f}ms)")
        raise
    duration_ms = (time.perf_counter() - started) * 1000
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)")
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    # Belt-and-suspenders alongside the middleware's logger.exception above:
    # guarantees a JSON 500 (not FastAPI's default HTML debug page) even if
    # something throws before the middleware's own try/except can log it.
    logger.error(f"Unhandled exception: {exc!r}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth.router)

_authenticated = [Depends(get_current_user)]
app.include_router(runs.router, dependencies=_authenticated)
app.include_router(scenarios.router, dependencies=_authenticated)
app.include_router(scripts.router, dependencies=_authenticated)
app.include_router(coverage.router, dependencies=_authenticated)
app.include_router(artifacts.router, dependencies=_authenticated)
app.include_router(audit.router, dependencies=_authenticated)  # + require_admin per-route
app.include_router(metrics.router, dependencies=_authenticated)  # + require_admin per-route


@app.get("/health")
def health():
    return {"status": "ok", "service": "flync-backend", "agents": ["scenario_agent", "script_agent"]}


@app.websocket("/runs/{run_id}/stream")
async def run_stream(websocket: WebSocket, run_id: str, token: str | None = None):
    try:
        user_from_websocket_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    run = get_run(run_id)
    if run is None:
        await websocket.send_json({"type": "error", "error": "Run not found"})
        await websocket.close(code=1008)
        return
    queue = subscribe(run_id, __import__("asyncio").get_running_loop())
    try:
        await websocket.send_json({"type": "snapshot", "run": run})
        while True:
            await websocket.send_text(await queue.get())
    except WebSocketDisconnect:
        pass
    finally:
        unsubscribe(run_id, queue)