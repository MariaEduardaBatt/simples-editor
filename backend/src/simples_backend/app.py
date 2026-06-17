from __future__ import annotations

import logging
import time

from flask import Flask, Response, g, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from flask_limiter import Limiter
from flask_limiter.errors import RateLimitExceeded as LimiterRateLimitExceeded
from flask_limiter.util import get_remote_address
from flask_sock import Sock

from .auth import AuthError
from .config import Settings, load_settings
from .logging_config import configure_logging
from .metrics import http_requests_total
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

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> Flask:
    configure_logging()

    app = Flask(__name__)

    resolved = load_settings() if settings is None else settings
    app.config["SETTINGS"] = resolved

    @app.before_request
    def _before_request():
        g.request_start = time.monotonic()

    @app.after_request
    def _after_request(response):
        duration_ms = int((time.monotonic() - g.request_start) * 1000)
        logger.info(
            "%s %s -> %s",
            request.method,
            request.path,
            response.status_code,
            extra={"duration_ms": duration_ms},
        )
        http_requests_total.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code,
        ).inc()
        return response

    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri="memory://",
        default_limits=[],
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

    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    sock = Sock(app)
    register_run_ws(sock, resolved, limiter=limiter)

    return app
