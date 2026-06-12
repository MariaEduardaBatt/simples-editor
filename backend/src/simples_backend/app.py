from __future__ import annotations

from flask import Flask, jsonify

from .auth import AuthError
from .config import Settings, load_settings
from .routes import create_auth_blueprint


def create_app(settings: Settings | None = None) -> Flask:
    """Flask application factory."""

    app = Flask(__name__)

    resolved = load_settings() if settings is None else settings
    app.config["SETTINGS"] = resolved

    @app.errorhandler(AuthError)
    def handle_auth_error(exc: AuthError):
        return jsonify({"error": exc.code}), 401

    app.register_blueprint(create_auth_blueprint(resolved), url_prefix="/api/auth")

    return app
