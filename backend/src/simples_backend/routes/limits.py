from __future__ import annotations

from flask import Blueprint, jsonify

from ..config import Settings


def create_limits_blueprint(settings: Settings) -> Blueprint:
    bp = Blueprint("limits", __name__)

    @bp.get("/limits")
    def limits():
        return jsonify({
            "exec_timeout_s": settings.exec_timeout_s,
            "compile_timeout_s": settings.compile_timeout_s,
            "max_code_kb": settings.max_code_kb,
            "runs_per_minute": settings.runs_per_minute,
            "runs_per_minute_ip": settings.runs_per_minute_ip,
        })

    return bp
