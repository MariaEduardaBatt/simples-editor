# Supabase Auth Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add backend Supabase auth support so Flask can validate JWTs locally and the frontend can verify a login token.

**Architecture:** Build a small Flask backend package with a strict config loader, a JWT verifier, and a `/api/auth/verify` endpoint. Keep auth state out of the database; the backend only validates Supabase access tokens and exposes reusable helpers for future protected routes.

**Tech Stack:** Flask, PyJWT, pytest.

---

## File structure

- Create `backend/pyproject.toml` for backend dependencies and test commands.
- Create `backend/src/simples_backend/__init__.py` as the package entry point.
- Create `backend/src/simples_backend/config.py` to load and validate `SUPABASE_URL` and `SUPABASE_JWT_SECRET`.
- Create `backend/src/simples_backend/auth.py` for bearer parsing, JWT verification, and the reusable `@verify_jwt` decorator.
- Create `backend/src/simples_backend/app.py` for the Flask app factory.
- Create `backend/src/simples_backend/routes/__init__.py` and `backend/src/simples_backend/routes/auth.py` for the auth blueprint and `/api/auth/verify`.
- Create `backend/tests/conftest.py`, `backend/tests/test_config.py`, `backend/tests/test_auth.py`, and `backend/tests/test_verify_route.py`.

### Task 1: Bootstrapping the backend package and env loader

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/src/simples_backend/__init__.py`
- Create: `backend/src/simples_backend/config.py`
- Create: `backend/tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest

from simples_backend.config import load_settings


def test_load_settings_requires_supabase_env_vars(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)

    with pytest.raises(RuntimeError, match="SUPABASE_URL, SUPABASE_JWT_SECRET"):
        load_settings()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_config.py -v`
Expected: FAIL because `load_settings()` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_jwt_secret: str


def load_settings() -> Settings:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    missing = []
    if not supabase_url:
        missing.append("SUPABASE_URL")
    if not supabase_jwt_secret:
        missing.append("SUPABASE_JWT_SECRET")
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
    return Settings(
        supabase_url=supabase_url,
        supabase_jwt_secret=supabase_jwt_secret,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/pyproject.toml backend/src/simples_backend/__init__.py backend/src/simples_backend/config.py backend/tests/test_config.py
git commit -m "feat: bootstrap backend config for Supabase auth"
```

### Task 2: Implementing JWT verification and the auth decorator

**Files:**
- Create: `backend/src/simples_backend/auth.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Write the failing test**

```python
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from simples_backend.auth import AuthError, extract_bearer_token, verify_supabase_jwt


def test_extract_bearer_token_reads_bearer_prefix():
    assert extract_bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"


def test_verify_supabase_jwt_returns_identity():
    secret = "test-secret"
    token = jwt.encode(
        {
            "sub": "user-123",
            "email": "student@example.edu",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )

    claims = verify_supabase_jwt(token, secret)

    assert claims == {
        "user_id": "user-123",
        "email": "student@example.edu",
    }


def test_verify_supabase_jwt_rejects_invalid_signature():
    token = jwt.encode(
        {"sub": "user-123", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "wrong-secret",
        algorithm="HS256",
    )

    with pytest.raises(AuthError):
        verify_supabase_jwt(token, "test-secret")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_auth.py -v`
Expected: FAIL because the auth helpers do not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from functools import wraps

import jwt
from flask import g, request
from jwt import ExpiredSignatureError, InvalidTokenError


class AuthError(Exception):
    pass


def extract_bearer_token(authorization_header: str | None) -> str:
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthError("missing_bearer_token")
    return authorization_header.removeprefix("Bearer ").strip()


def verify_supabase_jwt(token: str, secret: str) -> dict[str, str | None]:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except ExpiredSignatureError as exc:
        raise AuthError("expired_token") from exc
    except InvalidTokenError as exc:
        raise AuthError("invalid_token") from exc

    return {
        "user_id": payload["sub"],
        "email": payload.get("email"),
    }


def verify_jwt(secret: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            token = extract_bearer_token(request.headers.get("Authorization"))
            g.identity = verify_supabase_jwt(token, secret)
            return view(*args, **kwargs)

        return wrapped

    return decorator
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_auth.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/simples_backend/auth.py backend/tests/test_auth.py
git commit -m "feat: add Supabase JWT verification helpers"
```

### Task 3: Wiring the Flask app and `/api/auth/verify`

**Files:**
- Create: `backend/src/simples_backend/app.py`
- Create: `backend/src/simples_backend/routes/__init__.py`
- Create: `backend/src/simples_backend/routes/auth.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_verify_route.py`

- [ ] **Step 1: Write the failing test**

```python
from datetime import datetime, timedelta, timezone

import jwt


def test_verify_route_accepts_valid_token(client):
    token = jwt.encode(
        {
            "sub": "user-123",
            "email": "student@example.edu",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        "test-secret",
        algorithm="HS256",
    )

    response = client.post(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "valid": True,
        "user_id": "user-123",
        "email": "student@example.edu",
    }


def test_verify_route_rejects_missing_token(client):
    response = client.post("/api/auth/verify")

    assert response.status_code == 401
    assert response.get_json() == {"error": "missing_bearer_token"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_verify_route.py -v`
Expected: FAIL because the app factory and route do not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
from flask import Flask, Blueprint, jsonify, request

from simples_backend.auth import AuthError, extract_bearer_token, verify_supabase_jwt
from simples_backend.config import Settings, load_settings


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or load_settings()
    app = Flask(__name__)

    auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

    @auth_bp.post("/verify")
    def verify():
        try:
            token = extract_bearer_token(request.headers.get("Authorization"))
            claims = verify_supabase_jwt(token, settings.supabase_jwt_secret)
        except AuthError as exc:
            return jsonify({"error": str(exc)}), 401

        return jsonify({"valid": True, **claims})

    app.register_blueprint(auth_bp)
    return app
```

```python
import pytest

from simples_backend.app import create_app
from simples_backend.config import Settings


@pytest.fixture
def client():
    app = create_app(
        Settings(
            supabase_url="https://example.supabase.co",
            supabase_jwt_secret="test-secret",
        )
    )
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_verify_route.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/simples_backend/app.py backend/src/simples_backend/routes/__init__.py backend/src/simples_backend/routes/auth.py backend/tests/conftest.py backend/tests/test_verify_route.py
git commit -m "feat: expose Supabase auth verify endpoint"
```

### Final verification

- [ ] Run the full backend test suite.

Run: `pytest backend/tests -v`
Expected: all auth tests pass, including env loading, JWT verification, and the verify endpoint.
