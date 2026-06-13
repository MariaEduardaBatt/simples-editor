from __future__ import annotations

import json
import signal
import subprocess
import tempfile
import threading
import time
from queue import Empty, Queue

from flask import request
from flask_sock import Sock

from ..auth import AuthError, verify_supabase_jwt
from ..config import Settings
from ..services.compiler_service import CompilerError, compile_simples
from ..services.execution_service import ExecutionError, assemble_nasm, link_object

MAX_CODE_BYTES = 64 * 1024
STDIN_MAX_BYTES = 4 * 1024
WS_POLL_S = 0.05


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

            process = subprocess.Popen(
                [bin_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=tmpdir,
            )

            output_queue: Queue = Queue()
            stop_event = threading.Event()

            def _reader() -> None:
                try:
                    for line in iter(process.stdout.readline, b""):
                        if stop_event.is_set():
                            break
                        output_queue.put(("stdout", line))
                    for line in iter(process.stderr.readline, b""):
                        if stop_event.is_set():
                            break
                        output_queue.put(("stderr", line))
                finally:
                    process.wait()
                    output_queue.put(("exit", process.returncode))

            reader_thread = threading.Thread(target=_reader, daemon=True)
            reader_thread.start()

            start_time = time.monotonic()
            exec_timeout = settings.exec_timeout_s

            while True:
                try:
                    kind, data = output_queue.get_nowait()
                    if kind == "exit":
                        duration = int((time.monotonic() - start_time) * 1000)
                        _send(ws, {"type": "exit", "code": data, "duration_ms": duration})
                        break
                    _send(ws, {"type": kind, "data": data.decode(errors="replace")})
                    continue
                except Empty:
                    pass

                if time.monotonic() - start_time > exec_timeout:
                    stop_event.set()
                    process.terminate()
                    try:
                        process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    _send(ws, {"type": "timeout", "limit_s": exec_timeout})
                    break

                try:
                    raw = ws.receive(timeout=WS_POLL_S)
                    if raw is None:
                        break
                    msg = json.loads(raw)
                    t = msg.get("type", "")
                    if t == "stdin":
                        data = msg.get("data", "")
                        if data and len(data.encode("utf-8")) <= STDIN_MAX_BYTES:
                            process.stdin.write(data.encode("utf-8"))
                            process.stdin.flush()
                    elif t == "stop":
                        stop_event.set()
                        process.terminate()
                        try:
                            process.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                        _send(ws, {"type": "exit", "code": -signal.SIGTERM})
                        break
                    elif t == "ping":
                        _send(ws, {"type": "pong"})
                except json.JSONDecodeError:
                    pass

            if process.poll() is None:
                stop_event.set()
                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

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
