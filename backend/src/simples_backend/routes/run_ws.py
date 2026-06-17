from __future__ import annotations

import json
import logging
import tempfile
from enum import Enum, auto

from flask import request
from flask_sock import Sock

from flask_limiter import Limiter
from flask_limiter.errors import RateLimitExceeded as LimiterRateLimitExceeded

from ..auth import AuthError, verify_supabase_jwt
from ..config import Settings
from ..services.compiler_service import CompilerError, compile_simples
from ..services.execution_service import ExecutionError, assemble_nasm, link_object
from ..services.execution_strategy import PtyExecutionStrategy

logger = logging.getLogger(__name__)

MAX_CODE_BYTES = 64 * 1024


class ConnectionState(Enum):
    IDLE = auto()
    COMPILING = auto()
    EXECUTING = auto()


def extract_jwt_from_ws() -> str:
    protocols = request.headers.get("Sec-WebSocket-Protocol", "")
    for protocol in protocols.split(","):
        protocol = protocol.strip()
        if protocol.startswith("bearer."):
            return protocol[len("bearer."):]
    token = request.args.get("token")
    if token:
        return token
    raise AuthError("missing_bearer_token")


def _send(ws, msg: dict) -> None:
    try:
        ws.send(json.dumps(msg, ensure_ascii=False))
    except Exception:
        pass


def handle_compile_and_run(ws, code: str, settings: Settings) -> ConnectionState:
    _send(ws, {"type": "compile_started"})

    try:
        with tempfile.TemporaryDirectory(prefix="sim-") as tmpdir:
            nasm = compile_simples(code)
            _send(ws, {"type": "asm_generated", "asm": nasm})

            try:
                obj_path = assemble_nasm(nasm, tmpdir, settings.compile_timeout_s)
            except ExecutionError as e:
                _send(ws, {"type": "assemble_error", "stderr": e.message})
                return ConnectionState.IDLE

            try:
                bin_path = link_object(obj_path, tmpdir, settings.compile_timeout_s)
            except ExecutionError as e:
                _send(ws, {"type": "link_error", "stderr": e.message})
                return ConnectionState.IDLE

            _send(ws, {"type": "exec_started"})

            strategy = PtyExecutionStrategy(image=settings.sandbox_image, stop_timeout_s=settings.stop_timeout_s)
            result = strategy.execute(tmpdir, ws, settings.exec_timeout_s)

            if not result.timed_out:
                _send(ws, {
                    "type": "exit",
                    "code": result.exit_code,
                    "duration_ms": result.duration_ms,
                })

    except CompilerError as e:
        if e.phase is not None:
            _send(ws, {
                "type": "compile_error",
                "phase": e.phase,
                "line": e.line,
                "column": e.column,
                "message": e.message,
            })
        else:
            _send(ws, {"type": "internal_error", "message": e.message})
    except Exception as e:
        _send(ws, {"type": "internal_error", "message": str(e)})

    return ConnectionState.IDLE


def handle_ws_connection(
    ws,
    settings: Settings,
    limiter: Limiter | None = None,
    identity: dict | None = None,
) -> None:
    if identity is None:
        try:
            jwt_token = extract_jwt_from_ws()
            identity = verify_supabase_jwt(jwt_token, settings.supabase_jwt_secret, settings.supabase_url)
        except AuthError as e:
            _send(ws, {"type": "internal_error", "message": e.code})
            try:
                ws.close()
            except Exception:
                pass
            return

    state = ConnectionState.IDLE

    while True:
        try:
            raw = ws.receive()
        except Exception:
            break
        if raw is None:
            break

        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("invalid frame discarded (not JSON)")
            continue

        t = msg.get("type", "")

        if t == "ping":
            _send(ws, {"type": "pong"})
            continue

        if t == "compile_and_run":
            if state != ConnectionState.IDLE:
                logger.warning("ignored compile_and_run in state %s", state.name)
                continue

            user_id = identity["user_id"]

            if limiter is not None:
                try:
                    with limiter.limit(
                        f"{settings.runs_per_minute}/minute",
                        key_func=lambda: user_id,
                    ):
                        with limiter.limit(
                            f"{settings.runs_per_minute_ip}/minute",
                            key_func=lambda: request.remote_addr or "unknown",
                        ):
                            pass
                except LimiterRateLimitExceeded:
                    _send(ws, {
                        "type": "internal_error",
                        "message": "rate_limit_exceeded",
                        "detail": "máximo de execuções por minuto excedido",
                    })
                    continue

            code = msg.get("code", "")
            if not isinstance(code, str) or not code.strip():
                _send(ws, {"type": "internal_error", "message": "missing code"})
                continue

            if len(code.encode("utf-8")) > MAX_CODE_BYTES:
                _send(ws, {"type": "internal_error", "message": "code_too_large"})
                continue

            state = ConnectionState.COMPILING
            state = handle_compile_and_run(ws, code, settings)
            continue

        if t == "stdin" and state != ConnectionState.EXECUTING:
            logger.warning("ignored stdin in state %s", state.name)
            continue

        if t == "stop" and state != ConnectionState.EXECUTING:
            logger.warning("ignored stop in state %s", state.name)
            continue

        if t not in ("ping", "compile_and_run", "stdin", "stop"):
            logger.warning("unknown message type '%s' discarded in state %s", t, state.name)


def register_run_ws(
    sock: Sock,
    settings: Settings,
    limiter: Limiter | None = None,
) -> None:
    @sock.route("/ws/run")
    def ws_run(ws):
        handle_ws_connection(ws, settings, limiter=limiter)
