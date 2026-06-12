from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..auth import verify_jwt
from ..config import Settings
from ..services.compiler_service import CompilerError, compile_simples

MAX_CODE_SIZE = 1_000_000


def create_compile_blueprint(settings: Settings) -> Blueprint:
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

        try:
            nasm = compile_simples(code)
            return jsonify({"nasm": nasm})
        except CompilerError as e:
            return jsonify({"error": e.message})

    return bp
