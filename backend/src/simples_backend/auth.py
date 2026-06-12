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


def verify_supabase_jwt(token: str, secret: str) -> Identity:
    try:
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


def verify_jwt(secret: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            token = extract_bearer_token(request.headers.get("Authorization"))
            g.identity = verify_supabase_jwt(token, secret)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
