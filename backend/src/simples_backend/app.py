from __future__ import annotations

import logging

from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.errors import RateLimitExceeded as LimiterRateLimitExceeded
from flask_limiter.util import get_remote_address
from flask_sock import Sock

from .auth import AuthError
from .config import Settings, load_settings
from .routes import (
    create_auth_blueprint,
    create_compile_blueprint,
    create_health_blueprint,
    create_limits_blueprint,
    register_run_ws,
)

import simple_websocket.ws as _sws
_original_choose = _sws.Server.choose_subprotocol
_sws.Server.choose_subprotocol = lambda self, req: (
    req.subprotocols[0] if req.subprotocols else None
)


def create_app(settings: Settings | None = None) -> Flask:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    """Flask application factory."""

    app = Flask(__name__)

    resolved = load_settings() if settings is None else settings
    app.config["SETTINGS"] = resolved

    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri=resolved.redis_url,
        default_limits=[],
        storage_options={"connect_timeout": 5},
        strategy="fixed-window",
    )

    @app.errorhandler(AuthError)
    def handle_auth_error(exc: AuthError):
        return jsonify({"error": exc.code}), 401

    @app.errorhandler(LimiterRateLimitExceeded)
    def handle_rate_limit(exc: LimiterRateLimitExceeded):
        return jsonify({
            "error": "rate_limit_exceeded",
            "detail": "máximo de execuções excedido",
        }), 429

    app.register_blueprint(create_auth_blueprint(resolved), url_prefix="/api/auth")
    app.register_blueprint(
        create_compile_blueprint(resolved, limiter=limiter),
        url_prefix="/api",
    )
    app.register_blueprint(create_health_blueprint(resolved), url_prefix="/api/health")
    app.register_blueprint(create_limits_blueprint(resolved), url_prefix="/api")

    sock = Sock(app)
    register_run_ws(sock, resolved, limiter=limiter)

    return app
