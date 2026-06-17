from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from ..auth import verify_jwt
from ..config import Settings
from ..rate_limiter import RateLimitExceeded, SlidingWindowRateLimiter
from ..services.compiler_service import CompilerError, compile_simples

MAX_CODE_SIZE = 1_000_000


def create_compile_blueprint(
    settings: Settings,
    user_limiter: SlidingWindowRateLimiter | None = None,
    ip_limiter: SlidingWindowRateLimiter | None = None,
) -> Blueprint:
    bp = Blueprint("compile", __name__)

    @bp.post("/compile")
    @verify_jwt(settings.supabase_jwt_secret)
    def compile_code():
        if request.content_length and request.content_length > MAX_CODE_SIZE:
            return jsonify({"error": "code_too_large"}), 413

        data = request.get_json(silent=True)
        if not data or "code" not in data:
            return jsonify({"error": "missing_code"}), 400

        code = data["code"]
        if not isinstance(code, str) or not code.strip():
            return jsonify({"error": "invalid_code"}), 400

        user_id = g.identity["user_id"]

        if user_limiter is not None:
            try:
                user_limiter.check(user_id)
            except RateLimitExceeded:
                return jsonify({
                    "error": "rate_limit_exceeded",
                    "detail": f"máximo de {settings.runs_per_minute} execuções por minuto",
                }), 429

        if ip_limiter is not None:
            ip = request.remote_addr or "unknown"
            try:
                ip_limiter.check(ip)
            except RateLimitExceeded:
                return jsonify({
                    "error": "rate_limit_exceeded",
                    "detail": f"máximo de {settings.runs_per_minute_ip} execuções por minuto por IP",
                }), 429

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
