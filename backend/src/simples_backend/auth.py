from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, TypedDict, cast

import jwt
from flask import g, request


class AuthError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code

    def __str__(self) -> str:
        return self.code


class Identity(TypedDict, total=False):
    user_id: str
    email: str


def extract_bearer_token(authorization_header: str | None) -> str:
    if not authorization_header:
        raise AuthError("missing_bearer_token")

    parts = authorization_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise AuthError("malformed_bearer_token")

    return parts[1]


_jwks_client: jwt.PyJWKClient | None = None


def _get_jwks_client(supabase_url: str) -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        base = supabase_url.rstrip("/")
        if "/rest/v1" in base:
            base = base.split("/rest/v1")[0]
        jwks_url = f"{base}/auth/v1/.well-known/jwks.json"
        _jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_client


def verify_supabase_jwt(token: str, secret: str, supabase_url: str = "") -> Identity:
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "")

        if alg == "ES256":
            jwks_client = _get_jwks_client(supabase_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                options={"require": ["exp", "sub"]},
            )
        else:
            claims = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={"require": ["exp", "sub"]},
            )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("expired_token") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("invalid_token") from exc

    sub = cast(str | None, claims.get("sub"))
    if not sub:
        raise AuthError("invalid_token")

    identity: Identity = {"user_id": sub}

    email = claims.get("email")
    if isinstance(email, str) and email:
        identity["email"] = email

    return identity


F = TypeVar("F", bound=Callable[..., Any])


def verify_jwt(secret: str, supabase_url: str = "") -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            token = extract_bearer_token(request.headers.get("Authorization"))
            g.identity = verify_supabase_jwt(token, secret, supabase_url)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
