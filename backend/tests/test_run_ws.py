from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest

from simples_backend.auth import AuthError
from simples_backend.config import Settings
from simples_backend.routes.run_ws import extract_jwt_from_ws, handle_ws_connection
from simples_backend.services.execution_strategy import ExecutionResult

TEST_SECRET = "0123456789abcdef0123456789abcdef"


def _docker_frame(stream_id: int, payload: bytes) -> bytes:
    return bytes([stream_id]) + b"\x00\x00\x00" + len(payload).to_bytes(4, "big") + payload


TEST_SETTINGS = Settings(
    supabase_url="http://test",
    supabase_jwt_secret=TEST_SECRET,
)
TEST_IDENTITY = {"user_id": "user-123"}


def _make_token(
    secret: str = TEST_SECRET,
    *,
    sub: str = "user-123",
    email: str | None = "user@example.com",
    exp: datetime | None = None,
) -> str:
    payload: dict[str, object] = {
        "sub": sub,
        "exp": exp or (datetime.now(tz=timezone.utc) + timedelta(minutes=5)),
    }
    if email is not None:
        payload["email"] = email
    return jwt.encode(payload, secret, algorithm="HS256")


class TestExtractJwtFromWs:
    def test_from_sec_websocket_protocol(self, app):
        token = _make_token()
        with app.test_request_context(
            headers={"Sec-WebSocket-Protocol": f"bearer.{token}"}
        ):
            assert extract_jwt_from_ws() == token

    def test_from_query_param(self, app):
        token = _make_token()
        with app.test_request_context(query_string={"token": token}):
            assert extract_jwt_from_ws() == token

    def test_no_auth_raises(self, app):
        with app.test_request_context():
            with pytest.raises(AuthError, match="missing_bearer_token"):
                extract_jwt_from_ws()


class TestHandleWsConnection:
    @patch("simples_backend.routes.run_ws.extract_jwt_from_ws")
    def test_invalid_jwt_sends_error_and_closes(self, mock_extract):
        mock_extract.side_effect = AuthError("missing_bearer_token")
        mock_ws = MagicMock()
        handle_ws_connection(mock_ws, TEST_SETTINGS)
        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert any(m.get("type") == "internal_error" for m in sent)
        mock_ws.close.assert_called_once()

    def test_ping_pong(self):
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "ping"}),
            None,
        ]
        handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)
        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert any(m.get("type") == "pong" for m in sent)

    def test_missing_code(self):
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "compile_and_run", "code": ""}),
            None,
        ]
        handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)
        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert any(
            m.get("type") == "internal_error" and "missing code" in m.get("message", "")
            for m in sent
        )

    def test_code_too_large(self):
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "compile_and_run", "code": "x" * 70000}),
            None,
        ]
        handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)
        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert any(
            m.get("type") == "internal_error" and "code_too_large" in m.get("message", "")
            for m in sent
        )

    @patch("simples_backend.routes.run_ws.compile_simples")
    def test_compile_success_flow(self, mock_compile):
        mock_compile.return_value = "section .data\n  x dd 0\n"
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "compile_and_run", "code": "programa test\ninicio\nfim"}),
            None,
        ]

        with patch("simples_backend.routes.run_ws.assemble_nasm") as mock_asm:
            mock_asm.return_value = "/tmp/programa.o"
            with patch("simples_backend.routes.run_ws.link_object") as mock_link:
                mock_link.return_value = "/tmp/programa"
                with patch(
                    "simples_backend.routes.run_ws.PtyExecutionStrategy"
                ) as mock_strategy_cls:
                    mock_strategy = MagicMock()
                    mock_strategy_cls.return_value = mock_strategy
                    mock_strategy.execute.return_value = ExecutionResult(
                        exit_code=0, duration_ms=50, timed_out=False
                    )

                    handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)

        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        types = [m.get("type") for m in sent]
        assert "compile_started" in types
        assert "asm_generated" in types
        assert "exec_started" in types
        assert "exit" in types

        exit_msg = next(m for m in sent if m.get("type") == "exit")
        assert exit_msg["code"] == 0

    @patch("simples_backend.routes.run_ws.compile_simples")
    def test_compile_error_flow(self, mock_compile):
        from simples_backend.services.compiler_service import CompilerError

        mock_compile.side_effect = CompilerError("invalid char", phase="lexer", line=1, column=5)
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "compile_and_run", "code": "programa test\ninicio\nfim"}),
            None,
        ]
        handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)

        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert any(m.get("type") == "compile_started" for m in sent)
        assert any(
            m.get("type") == "compile_error"
            and m.get("phase") == "lexer"
            and m.get("line") == 1
            and m.get("column") == 5
            for m in sent
        )

    @patch("simples_backend.routes.run_ws.compile_simples")
    def test_assemble_error(self, mock_compile):
        from simples_backend.services.execution_service import ExecutionError

        mock_compile.return_value = "section .data\n"
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "compile_and_run", "code": "programa test\ninicio\nfim"}),
            None,
        ]

        with patch("simples_backend.routes.run_ws.assemble_nasm") as mock_asm:
            mock_asm.side_effect = ExecutionError("nasm failed", "nasm")
            handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)

        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert any(m.get("type") == "assemble_error" for m in sent)

    @patch("simples_backend.routes.run_ws.compile_simples")
    def test_stdin_and_stop_through_bridge(self, mock_compile):
        mock_compile.return_value = "section .text\n  global _start\n_start:\n  mov eax, 1\n  xor ebx, ebx\n  int 0x80\n"

        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "compile_and_run", "code": "programa test\ninicio\nfim"}),
            json.dumps({"type": "stdin", "data": "42\n"}),
            json.dumps({"type": "stop"}),
            None,
        ]

        strategy = MagicMock()
        strategy.execute.return_value = ExecutionResult(exit_code=0, duration_ms=100, timed_out=False)

        with patch("simples_backend.routes.run_ws.assemble_nasm") as mock_asm:
            mock_asm.return_value = "/tmp/programa.o"
            with patch("simples_backend.routes.run_ws.link_object") as mock_link:
                mock_link.return_value = "/tmp/programa"
                with patch("simples_backend.routes.run_ws.PtyExecutionStrategy", return_value=strategy):
                    handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)

        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        types = [m.get("type") for m in sent]
        assert "compile_started" in types
        assert "asm_generated" in types
        assert "exec_started" in types
        assert "exit" in types

    @patch("simples_backend.routes.run_ws.compile_simples")
    def test_timeout_does_not_send_exit(self, mock_compile):
        mock_compile.return_value = "section .text\n"

        def mock_execute(binary_dir, ws, timeout_s):
            ws.send(json.dumps({"type": "timeout", "limit_s": timeout_s}))
            return ExecutionResult(exit_code=137, duration_ms=10000, timed_out=True)

        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "compile_and_run", "code": "programa test\ninicio\nfim"}),
            None,
        ]

        strategy = MagicMock()
        strategy.execute.side_effect = mock_execute

        with patch("simples_backend.routes.run_ws.assemble_nasm") as mock_asm:
            mock_asm.return_value = "/tmp/programa.o"
            with patch("simples_backend.routes.run_ws.link_object") as mock_link:
                mock_link.return_value = "/tmp/programa"
                with patch("simples_backend.routes.run_ws.PtyExecutionStrategy", return_value=strategy):
                    handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)

        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        types = [m.get("type") for m in sent]

        assert "timeout" in types
        assert "exit" not in types

        timeout_msg = next(m for m in sent if m.get("type") == "timeout")
        assert timeout_msg["limit_s"] == 10

    def test_invalid_json_discarded(self):
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            "not json",
            None,
        ]
        handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)
        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert sent == []

    def test_stdin_in_idle_discarded(self):
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "stdin", "data": "42\n"}),
            None,
        ]
        handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)
        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert all(m.get("type") != "internal_error" for m in sent)

    def test_stop_in_idle_discarded(self):
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "stop"}),
            None,
        ]
        handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)
        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert all(m.get("type") != "internal_error" for m in sent)

    def test_unknown_message_type_discarded(self):
        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "unknown_event", "foo": "bar"}),
            None,
        ]
        handle_ws_connection(mock_ws, TEST_SETTINGS, identity=TEST_IDENTITY)
        sent = [json.loads(call[0][0]) for call in mock_ws.send.call_args_list]
        assert all(m.get("type") != "internal_error" for m in sent)
