from __future__ import annotations

from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import Blueprint, jsonify

from ..config import Settings

VERSION = "1.0.0"


def create_health_blueprint(settings: Settings) -> Blueprint:
    bp = Blueprint("health", __name__)

    @bp.get("")
    def health():
        components = {
            "supabase": _check_supabase(settings.supabase_url),
            "compiler": {"status": "unavailable"},
            "nasm": {"status": "unavailable"},
            "docker": {"status": "unavailable"},
        }
        all_ok = all(c["status"] == "ok" for c in components.values())
        return jsonify(
            {
                "status": "healthy" if all_ok else "degraded",
                "version": VERSION,
                "components": components,
            }
        )

    return bp


def _check_supabase(url: str) -> dict:
    try:
        req = Request(url, method="GET")
        urlopen(req, timeout=3)
        return {"status": "ok"}
    except (URLError, OSError):
        return {"status": "unavailable"}
