"""Dashboard localhost — FastAPI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from trading_system import __version__
from trading_system.dashboard.data import load_dashboard_snapshot

TEMPLATES_DIR = Path(__file__).with_name("templates")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app = FastAPI(title="Trading System Dashboard", version=__version__)


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    snap = load_dashboard_snapshot()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "version": __version__,
            "balance": snap["balance"],
            "orders": snap["orders"],
            "signals": snap["signals"],
            "n_orders": snap["n_orders"],
            "n_signals": snap["n_signals"],
            "avg_rating": snap["avg_rating"],
        },
    )


@app.get("/api/snapshot")
def api_snapshot() -> dict:
    return load_dashboard_snapshot()
