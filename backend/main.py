"""
LabQC API -- FastAPI application entry point.

Configures CORS, registers all module routers, serves frontend static files,
and exposes a root health-check endpoint.  No business logic lives here.

When running as a standalone Windows executable (PyInstaller), set the
environment variable LABQC_STANDALONE=1 to enable SPA static file serving
and disable CORS middleware (single-origin, not needed).
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.db.database import init_db
from backend.routers import audit, auth, eqa, lis, license, lots, qc, rag, settings, sigma, validation

# ── Determine execution mode ──────────────────────────────────────────
def _is_standalone() -> bool:
    return os.environ.get("LABQC_STANDALONE", "0") == "1"

def _get_dist_dir() -> Path:
    if _is_standalone():
        import sys
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS) / "frontend_dist"
        return (Path(__file__).resolve().parent.parent / "frontend" / "dist").resolve()
    return (Path(__file__).resolve().parent.parent / "frontend" / "dist").resolve()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: initialise the database on startup."""
    init_db()
    yield


app = FastAPI(
    title="LabQC API",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS -- allow Vite dev server during development (disabled in standalone)
# ---------------------------------------------------------------------------
if not _is_standalone():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ══════════════════════════════════════════════════════════════════════
# License enforcement middleware
# ══════════════════════════════════════════════════════════════════════
from starlette.responses import JSONResponse as _JSONResponse

UNPROTECTED = {"/license/status", "/license/activate", "/auth/login", "/auth/me", "/auth/users"}

PROTECTED_PREFIXES = ("/qc/", "/sigma/", "/validation/", "/audit/", "/lots/", "/rag/", "/eqa/", "/lis/", "/settings/", "/docs", "/openapi.json")


@app.middleware("http")
async def license_guard(request, call_next):
    """Block protected API routes if license is invalid — **standalone mode only**.
    Web/online deployments skip license enforcement entirely."""
    # Only enforce license in standalone (EXE) mode; online version is unrestricted
    if not _is_standalone():
        return await call_next(request)

    path = request.url.path
    # Always allow unprotected endpoints
    if path in UNPROTECTED:
        return await call_next(request)
    # Only block protected API routes; let SPA through
    if any(path.startswith(p) for p in PROTECTED_PREFIXES):
        from backend.license import check_license
        valid, msg = check_license()
        if not valid:
            return _JSONResponse({"detail": f"软件未激活：{msg}"}, status_code=403)
    return await call_next(request)


# ---------------------------------------------------------------------------\n# Routers\n# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(qc.router)
app.include_router(sigma.router)
app.include_router(validation.router)
app.include_router(audit.router)
app.include_router(lots.router)
app.include_router(rag.router)
app.include_router(eqa.router)
app.include_router(lis.router)
app.include_router(settings.router)
app.include_router(license.router)

# ---------------------------------------------------------------------------
# Static files & SPA (standalone mode only)
# ---------------------------------------------------------------------------
if _is_standalone():
    dist = _get_dist_dir()
    if dist.exists():
        # Mount /assets
        assets_dir = dist / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        # Serve root favicon and icons
        @app.get("/favicon.svg")
        async def favicon():
            fp = dist / "favicon.svg"
            if fp.exists():
                return FileResponse(str(fp))
            return {"status": "not found"}

        @app.get("/icons.svg")
        async def icons():
            fp = dist / "icons.svg"
            if fp.exists():
                return FileResponse(str(fp))
            return {"status": "not found"}

        # SPA fallback: serve index.html for all non-API routes
        from starlette.responses import Response

        @app.middleware("http")
        async def spa_fallback(request, call_next):
            """Catch-all: serve index.html for any route not matched by API routers."""
            response = await call_next(request)
            if response.status_code == 404 and not request.url.path.startswith("/auth") and \
               not request.url.path.startswith("/qc") and not request.url.path.startswith("/sigma") and \
               not request.url.path.startswith("/validation") and not request.url.path.startswith("/audit") and \
               not request.url.path.startswith("/lots") and not request.url.path.startswith("/rag") and \
               not request.url.path.startswith("/eqa") and not request.url.path.startswith("/lis") and \
               not request.url.path.startswith("/license") and not request.url.path.startswith("/settings") and not request.url.path.startswith("/docs") and \
               not request.url.path.startswith("/openapi.json"):
                index_path = dist / "index.html"
                if index_path.exists():
                    return FileResponse(str(index_path))
            return response

# ---------------------------------------------------------------------------
# Root — health check (API) or SPA index (standalone)
# ---------------------------------------------------------------------------
@app.get("/")
def root() -> dict:
    """Simple health-check endpoint. In standalone mode, serves the SPA."""
    if _is_standalone():
        dist = _get_dist_dir()
        if dist.exists():
            index_path = dist / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
    return {"status": "ok", "app": "LabQC"}
