from __future__ import annotations

import json
import tempfile

from flask import request
from flask_sock import Sock

from ..auth import AuthError, verify_supabase_jwt
from ..config import Settings
from ..services.compiler_service import CompilerError, compile_simples
from ..services.execution_service import ExecutionError, assemble_nasm, link_object
from ..services.execution_strategy import PtyExecutionStrategy

MAX_CODE_BYTES = 64 * 1024


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


def handle_compile_and_run(ws, code: str, settings: Settings) -> None:
    _send(ws, {"type": "compile_started"})

    try:
        with tempfile.TemporaryDirectory(prefix="sim-") as tmpdir:
            nasm = compile_simples(code)
            _send(ws, {"type": "asm_generated", "asm": nasm})

            try:
                obj_path = assemble_nasm(nasm, tmpdir, settings.compile_timeout_s)
            except ExecutionError as e:
                _send(ws, {"type": "assemble_error", "stderr": e.message})
                return

            try:
                bin_path = link_object(obj_path, tmpdir, settings.compile_timeout_s)
            except ExecutionError as e:
                _send(ws, {"type": "link_error", "stderr": e.message})
                return

            _send(ws, {"type": "exec_started"})

            strategy = PtyExecutionStrategy(image=settings.sandbox_image)
            result = strategy.execute(tmpdir, ws, settings.exec_timeout_s)

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


def handle_ws_connection(ws, settings: Settings, identity: dict | None = None) -> None:
    if identity is None:
        try:
            jwt_token = extract_jwt_from_ws()
            identity = verify_supabase_jwt(jwt_token, settings.supabase_jwt_secret)
        except AuthError as e:
            _send(ws, {"type": "internal_error", "message": e.code})
            try:
                ws.close()
            except Exception:
                pass
            return

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
            continue

        t = msg.get("type", "")

        if t == "ping":
            _send(ws, {"type": "pong"})
            continue

        if t != "compile_and_run":
            continue

        code = msg.get("code", "")
        if not isinstance(code, str) or not code.strip():
            _send(ws, {"type": "internal_error", "message": "missing code"})
            continue

        if len(code.encode("utf-8")) > MAX_CODE_BYTES:
            _send(ws, {"type": "internal_error", "message": "code_too_large"})
            continue

        handle_compile_and_run(ws, code, settings)


def register_run_ws(sock: Sock, settings: Settings) -> None:
    @sock.route("/ws/run")
    def ws_run(ws):
        handle_ws_connection(ws, settings)
