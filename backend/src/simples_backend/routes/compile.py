from __future__ import annotations

from flask import Blueprint, g, jsonify, request
from flask_limiter import Limiter

from ..auth import verify_jwt
from ..config import Settings
from ..services.compiler_service import CompilerError, compile_simples

MAX_CODE_SIZE = 1_000_000


def _user_key() -> str:
    identity = g.get("identity")
    if identity:
        return identity.get("user_id", "unknown")
    return request.remote_addr or "unknown"


def create_compile_blueprint(
    settings: Settings,
    limiter: Limiter | None = None,
) -> Blueprint:
    bp = Blueprint("compile", __name__)

    @bp.post("/compile")
    @verify_jwt(settings.supabase_jwt_secret)
    @limiter.limit(lambda: f"{settings.runs_per_minute}/minute", key_func=_user_key)
    @limiter.limit(lambda: f"{settings.runs_per_minute_ip}/minute", key_func=lambda: request.remote_addr or "unknown")
    def compile_code():
        if request.content_length and request.content_length > MAX_CODE_SIZE:
            return jsonify({"error": "code_too_large"}), 413

        data = request.get_json(silent=True)
        if not data or "code" not in data:
            return jsonify({"error": "missing_code"}), 400

        code = data["code"]
        if not isinstance(code, str) or not code.strip():
            return jsonify({"error": "invalid_code"}), 400

        try:
            nasm = compile_simples(code)
            return jsonify({"nasm": nasm})
        except CompilerError as e:
            if e.phase is not None:
                return jsonify({
                    "error": {
                        "phase": e.phase,
                        "line": e.line,
                        "column": e.column,
                        "message": e.message,
                    }
                })
            return jsonify({"error": e.message})

    return bp
