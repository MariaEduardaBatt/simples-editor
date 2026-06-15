from __future__ import annotations

from flask import Flask, jsonify
from flask_sock import Sock

from .auth import AuthError
from .config import Settings, load_settings
from .routes import (
    create_auth_blueprint,
    create_compile_blueprint,
    create_health_blueprint,
    register_run_ws,
)

import simple_websocket.ws as _sws
_original_choose = _sws.Server.choose_subprotocol
_sws.Server.choose_subprotocol = lambda self, req: (
    req.subprotocols[0] if req.subprotocols else None
)


def create_app(settings: Settings | None = None) -> Flask:
    """Flask application factory."""

    app = Flask(__name__)

    resolved = load_settings() if settings is None else settings
    app.config["SETTINGS"] = resolved

    @app.errorhandler(AuthError)
    def handle_auth_error(exc: AuthError):
        return jsonify({"error": exc.code}), 401

    app.register_blueprint(create_auth_blueprint(resolved), url_prefix="/api/auth")
    app.register_blueprint(create_compile_blueprint(resolved), url_prefix="/api")
    app.register_blueprint(create_health_blueprint(resolved), url_prefix="/api/health")

    sock = Sock(app)
    register_run_ws(sock, resolved)

    return app
