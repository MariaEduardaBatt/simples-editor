from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt


def _make_token(
    secret: str,
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


CODE = "programa exemplo\ninteiro x\ninicio\nfim"
NASM_OUTPUT = "section .data\n  x dd 0\nsection .text\n  global _start\n_start:\n  mov eax, 1\n  xor ebx, ebx\n  int 0x80"


def test_compile_success_returns_nasm(client, settings):
    token = _make_token(settings.supabase_jwt_secret)

    with patch("simples_backend.routes.compile.compile_simples", return_value=NASM_OUTPUT):
        resp = client.post(
            "/api/compile",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": CODE},
        )

    assert resp.status_code == 200
    assert resp.get_json() == {"nasm": NASM_OUTPUT}


def test_compile_compiler_error_returns_error(client, settings):
    token = _make_token(settings.supabase_jwt_secret)

    with patch(
        "simples_backend.routes.compile.compile_simples",
        side_effect=__import__("simples_backend.services.compiler_service").services.compiler_service.CompilerError(
            "lexer:1:1: invalid character"
        ),
    ):
        resp = client.post(
            "/api/compile",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": CODE},
        )

    assert resp.status_code == 200
    assert resp.get_json() == {"error": "lexer:1:1: invalid character"}


def test_compile_missing_code_returns_400(client, settings):
    token = _make_token(settings.supabase_jwt_secret)

    resp = client.post(
        "/api/compile",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert resp.status_code == 400
    assert resp.get_json() == {"error": "missing_code"}


def test_compile_invalid_code_not_string_returns_400(client, settings):
    token = _make_token(settings.supabase_jwt_secret)

    resp = client.post(
        "/api/compile",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": 42},
    )

    assert resp.status_code == 400
    assert resp.get_json() == {"error": "invalid_code"}


def test_compile_empty_code_returns_400(client, settings):
    token = _make_token(settings.supabase_jwt_secret)

    resp = client.post(
        "/api/compile",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "   "},
    )

    assert resp.status_code == 400
    assert resp.get_json() == {"error": "invalid_code"}


def test_compile_missing_token_returns_401(client):
    resp = client.post("/api/compile", json={"code": CODE})

    assert resp.status_code == 401
    assert resp.get_json() == {"error": "missing_bearer_token"}
