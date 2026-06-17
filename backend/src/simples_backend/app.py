from __future__ import annotations

import logging

from flask import Flask, jsonify
from flask_sock import Sock

from .auth import AuthError
from .config import Settings, load_settings
from .rate_limiter import RateLimitExceeded, SlidingWindowRateLimiter
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

    user_limiter = SlidingWindowRateLimiter(
        max_requests=resolved.runs_per_minute, window_s=60
    )
    ip_limiter = SlidingWindowRateLimiter(
        max_requests=resolved.runs_per_minute_ip, window_s=60
    )

    @app.errorhandler(AuthError)
    def handle_auth_error(exc: AuthError):
        return jsonify({"error": exc.code}), 401

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(exc: RateLimitExceeded):
        return jsonify({
            "error": "rate_limit_exceeded",
            "detail": f"máximo de {exc.max_requests} execuções por {exc.window_s}s",
        }), 429

    app.register_blueprint(create_auth_blueprint(resolved), url_prefix="/api/auth")
    app.register_blueprint(
        create_compile_blueprint(resolved, user_limiter=user_limiter, ip_limiter=ip_limiter),
        url_prefix="/api",
    )
    app.register_blueprint(create_health_blueprint(resolved), url_prefix="/api/health")
    app.register_blueprint(create_limits_blueprint(resolved), url_prefix="/api")

    sock = Sock(app)
    register_run_ws(sock, resolved, user_limiter=user_limiter, ip_limiter=ip_limiter)

    return app
