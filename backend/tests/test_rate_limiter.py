from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest

from simples_backend.config import Settings
from simples_backend.rate_limiter import RateLimitExceeded, SlidingWindowRateLimiter


TEST_SECRET = "0123456789abcdef0123456789abcdef"


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
NASM_OUTPUT = (
    "section .data\n  x dd 0\nsection .text\n"
    "  global _start\n_start:\n  mov eax, 1\n  xor ebx, ebx\n  int 0x80"
)


class TestSlidingWindowRateLimiter:
    def test_allows_up_to_limit(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_s=60)
        assert limiter.is_allowed("a") is True
        assert limiter.is_allowed("a") is True
        assert limiter.is_allowed("a") is True

    def test_blocks_after_limit(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_s=60)
        for _ in range(3):
            limiter.is_allowed("a")
        assert limiter.is_allowed("a") is False

    def test_remaining_counts(self):
        limiter = SlidingWindowRateLimiter(max_requests=5, window_s=60)
        assert limiter.remaining("a") == 5
        limiter.is_allowed("a")
        assert limiter.remaining("a") == 4
        for _ in range(4):
            limiter.is_allowed("a")
        assert limiter.remaining("a") == 0
        assert limiter.is_allowed("a") is False

    def test_different_keys_are_independent(self):
        limiter = SlidingWindowRateLimiter(max_requests=2, window_s=60)
        assert limiter.is_allowed("a") is True
        assert limiter.is_allowed("a") is True
        assert limiter.is_allowed("a") is False
        assert limiter.is_allowed("b") is True
        assert limiter.is_allowed("b") is True
        assert limiter.is_allowed("b") is False

    def test_window_slides(self):
        with patch("time.monotonic") as mock_time:
            mock_time.return_value = 0
            limiter = SlidingWindowRateLimiter(max_requests=2, window_s=10)
            assert limiter.is_allowed("a") is True
            assert limiter.is_allowed("a") is True
            assert limiter.is_allowed("a") is False

            mock_time.return_value = 11
            assert limiter.is_allowed("a") is True

    def test_reset_clears_key(self):
        limiter = SlidingWindowRateLimiter(max_requests=1, window_s=60)
        assert limiter.is_allowed("a") is True
        assert limiter.is_allowed("a") is False
        limiter.reset("a")
        assert limiter.is_allowed("a") is True

    def test_check_raises_exception(self):
        limiter = SlidingWindowRateLimiter(max_requests=1, window_s=60)
        limiter.check("a")
        with pytest.raises(RateLimitExceeded) as exc:
            limiter.check("a")
        assert exc.value.max_requests == 1
        assert exc.value.window_s == 60


class TestLimitsEndpoint:
    def test_limits_returns_settings(self, client, settings):
        resp = client.get("/api/limits")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["exec_timeout_s"] == settings.exec_timeout_s
        assert data["compile_timeout_s"] == settings.compile_timeout_s
        assert data["max_code_kb"] == settings.max_code_kb
        assert data["runs_per_minute"] == settings.runs_per_minute
        assert data["runs_per_minute_ip"] == settings.runs_per_minute_ip


def test_compile_rate_limit_exceeded_returns_429():
    """User exceeds limit → 429."""
    from simples_backend.app import create_app

    token = _make_token(TEST_SECRET, sub="rate-limited-user")
    low_limit = Settings(
        supabase_url="http://test",
        supabase_jwt_secret=TEST_SECRET,
        runs_per_minute=1,
    )
    app = create_app(low_limit)
    client = app.test_client()

    with patch("simples_backend.routes.compile.compile_simples", return_value=NASM_OUTPUT):
        resp1 = client.post(
            "/api/compile",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": CODE},
        )
        assert resp1.status_code == 200

        resp2 = client.post(
            "/api/compile",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": CODE},
        )
        assert resp2.status_code == 429
        data = resp2.get_json()
        assert data["error"] == "rate_limit_exceeded"


def test_compile_allows_within_limit(client, settings):
    """Normal request within limit succeeds."""
    token = _make_token(settings.supabase_jwt_secret)
    with patch("simples_backend.routes.compile.compile_simples", return_value=NASM_OUTPUT):
        resp = client.post(
            "/api/compile",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": CODE},
        )
    assert resp.status_code == 200
    assert resp.get_json() == {"nasm": NASM_OUTPUT}
