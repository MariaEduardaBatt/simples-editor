from __future__ import annotations

from datetime import datetime, timedelta, timezone

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


def test_verify_route_valid_token_returns_identity(client, settings):
    token = _make_token(settings.supabase_jwt_secret, sub="user-123", email="user@example.com")

    resp = client.post(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert resp.get_json() == {
        "valid": True,
        "user_id": "user-123",
        "email": "user@example.com",
    }


def test_verify_route_missing_token_returns_401(client):
    resp = client.post("/api/auth/verify")

    assert resp.status_code == 401
    assert resp.get_json() == {"error": "missing_bearer_token"}


def test_verify_route_malformed_token_returns_401(client):
    resp = client.post(
        "/api/auth/verify",
        headers={"Authorization": "Bearer"},
    )

    assert resp.status_code == 401
    assert resp.get_json() == {"error": "malformed_bearer_token"}


def test_verify_route_invalid_token_returns_401(client, settings):
    token = _make_token("fedcba9876543210fedcba9876543210")

    resp = client.post(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 401
    assert resp.get_json() == {"error": "invalid_token"}


def test_verify_route_expired_token_returns_401(client, settings):
    expired = datetime.now(tz=timezone.utc) - timedelta(minutes=1)
    token = _make_token(settings.supabase_jwt_secret, exp=expired)

    resp = client.post(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 401
    assert resp.get_json() == {"error": "expired_token"}
