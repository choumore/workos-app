#!/usr/bin/env python3
"""MemPalace companion server for WorkOS — bridges Obsidian vault + MemPalace search."""

import asyncio
import os
import re
import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="WorkOS MemPalace Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------

class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    wing: str | None = None

class ExportFile(BaseModel):
    path: str
    content: str

class ExportRequest(BaseModel):
    vault_path: str
    files: list[ExportFile]

class MineRequest(BaseModel):
    vault_path: str
    mode: str = "full"

# ---------- Path safety ----------

def validate_vault_path(vault_path: str) -> Path:
    """Resolve and validate vault path is absolute, exists, and is a directory."""
    expanded = Path(os.path.expanduser(vault_path)).resolve()
    if not expanded.is_absolute():
        raise HTTPException(400, "vault_path must be absolute")
    if not expanded.is_dir():
        raise HTTPException(400, f"vault_path does not exist or is not a directory: {expanded}")
    return expanded

def validate_file_path(vault_root: Path, relative_path: str) -> Path:
    """Ensure relative_path stays within vault_root — no traversal."""
    if ".." in relative_path.split("/"):
        raise HTTPException(400, f"Path traversal rejected: {relative_path}")
    # Only allow markdown files in expected subdirectories
    if not re.match(r'^[a-zA-Z0-9_-]+(/[a-zA-Z0-9_.@:\s-]+){0,3}\.md$', relative_path):
        raise HTTPException(400, f"Invalid file path format: {relative_path}")
    full = (vault_root / relative_path).resolve()
    if not str(full).startswith(str(vault_root)):
        raise HTTPException(400, f"Path traversal rejected: {relative_path}")
    return full

# ---------- MemPalace helpers ----------

def get_palace():
    """Attempt to import and return a MemPalace instance. Returns None if not installed."""
    try:
        from mempalace import MemPalace
        return MemPalace()
    except Exception:
        return None

# ---------- Endpoints ----------

@app.get("/status")
def status():
    palace = get_palace()
    initialized = palace is not None
    stats = {}
    if initialized:
        try:
            stats = palace.status()
        except Exception:
            pass
    return {
        "status": "ok",
        "mempalace_initialized": initialized,
        "stats": stats,
    }

@app.post("/search")
def search(req: SearchRequest):
    palace = get_palace()
    if not palace:
        raise HTTPException(503, "MemPalace not initialized — install with: pip install mempalace")
    try:
        kwargs = {"query": req.query, "limit": req.limit}
        if req.wing:
            kwargs["wing"] = req.wing
        results = palace.search(**kwargs)
        return {
            "results": [
                {"content": r.get("content", ""), "source": r.get("source", ""), "score": r.get("score", 0)}
                for r in (results if isinstance(results, list) else [])
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Search failed: {e}")

@app.get("/wings")
def wings():
    palace = get_palace()
    if not palace:
        raise HTTPException(503, "MemPalace not initialized")
    try:
        wing_list = palace.wings()
        return {"wings": wing_list if isinstance(wing_list, list) else []}
    except Exception as e:
        raise HTTPException(500, f"Failed to list wings: {e}")

@app.post("/export")
def export(req: ExportRequest):
    vault_root = validate_vault_path(req.vault_path)
    written = []
    for f in req.files:
        full_path = validate_file_path(vault_root, f.path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(f.content, encoding="utf-8")
        written.append(f.path)
    return {"written": written, "count": len(written)}

@app.post("/mine")
def mine(req: MineRequest):
    vault_root = validate_vault_path(req.vault_path)
    try:
        proc = subprocess.Popen(
            ["mempalace", "mine", str(vault_root), "--mode", req.mode],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return {"status": "started", "pid": proc.pid, "vault_path": str(vault_root)}
    except FileNotFoundError:
        raise HTTPException(503, "mempalace CLI not found — install with: pip install mempalace")
    except Exception as e:
        raise HTTPException(500, f"Failed to start mining: {e}")

# ---------- Main ----------

if __name__ == "__main__":
    import uvicorn
    print("MemPalace server running on http://localhost:8091")
    print("Endpoints: /status, /search, /wings, /export, /mine")
    uvicorn.run(app, host="0.0.0.0", port=8091)
