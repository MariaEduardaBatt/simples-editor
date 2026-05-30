from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask, g
import jwt

from simples_backend.auth import AuthError, extract_bearer_token, verify_jwt, verify_supabase_jwt


def _make_token(secret: str, *, sub: str = "user-123", email: str | None = "user@example.com", exp: datetime | None = None) -> str:
    payload: dict[str, object] = {
        "sub": sub,
        "exp": exp or (datetime.now(tz=timezone.utc) + timedelta(minutes=5)),
    }
    if email is not None:
        payload["email"] = email

    return jwt.encode(payload, secret, algorithm="HS256")


def test_extract_bearer_token_happy_path():
    assert extract_bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"


@pytest.mark.parametrize("header", [None, ""])
def test_extract_bearer_token_missing_header_raises(header):
    with pytest.raises(AuthError, match="Authorization"):
        extract_bearer_token(header)


@pytest.mark.parametrize(
    "header",
    [
        "Basic abc.def.ghi",
        "Bearer",
        "Bearer ",
        "Bearer abc def",
    ],
)
def test_extract_bearer_token_malformed_header_raises(header):
    with pytest.raises(AuthError, match="Malformed"):
        extract_bearer_token(header)


def test_verify_supabase_jwt_valid_signature_and_exp_returns_identity():
    secret = "secret"
    token = _make_token(secret, sub="user-123", email="user@example.com")

    identity = verify_supabase_jwt(token, secret)

    assert identity == {"user_id": "user-123", "email": "user@example.com"}


def test_verify_supabase_jwt_invalid_signature_raises_auth_error():
    token = _make_token("correct-secret")

    with pytest.raises(AuthError, match="Invalid"):
        verify_supabase_jwt(token, "wrong-secret")


def test_verify_supabase_jwt_expired_token_raises_auth_error():
    secret = "secret"
    expired = datetime.now(tz=timezone.utc) - timedelta(minutes=1)
    token = _make_token(secret, exp=expired)

    with pytest.raises(AuthError, match="expired"):
        verify_supabase_jwt(token, secret)


def test_verify_jwt_decorator_sets_g_identity_and_invokes_wrapped_view():
    secret = "secret"
    token = _make_token(secret, sub="user-abc", email="decorator@example.com")
    app = Flask(__name__)

    @verify_jwt(secret)
    def view_func():
        return g.identity

    with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
        result = view_func()

    assert result == {"user_id": "user-abc", "email": "decorator@example.com"}
