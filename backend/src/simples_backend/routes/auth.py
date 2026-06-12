from __future__ import annotations

from flask import Blueprint, g, jsonify

from ..auth import verify_jwt
from ..config import Settings


def create_auth_blueprint(settings: Settings) -> Blueprint:
    bp = Blueprint("auth", __name__)

    @bp.post("/verify")
    @verify_jwt(settings.supabase_jwt_secret)
    def verify():
        identity = g.identity
        return jsonify(
            {
                "valid": True,
                "user_id": identity["user_id"],
                "email": identity.get("email"),
            }
        )

    return bp
