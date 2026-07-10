import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from .config import settings
from .database import engine, Base
from .api.router import api_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="竞对品牌研究看板", version="2.0.0")

# CORS — allow all origins in production so the dashboard is accessible from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


# ── Static files & SPA fallback ──────────────────────────────────────────
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
    # Mount /assets/ and other static resources
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    # Also mount any other top-level files (favicon, robots, etc.)
    for f in FRONTEND_DIR.iterdir():
        if f.is_file() and f.suffix != ".html":
            # These are served via catch-all; FastAPI StaticFiles can't mount root.
            pass

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_spa(full_path: str, request: Request):
        """Serve SPA: API routes already matched; everything else → index.html."""
        # API paths are handled by the router above; this is the fallback.
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
