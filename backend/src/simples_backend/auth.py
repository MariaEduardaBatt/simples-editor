from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, TypeVar, cast

import jwt
from flask import g, request


@dataclass(frozen=True)
class AuthError(Exception):
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return self.message


def extract_bearer_token(authorization_header: str | None) -> str:
    if not authorization_header:
        raise AuthError("Missing Authorization header")

    parts = authorization_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise AuthError("Malformed Authorization header")

    return parts[1]


def verify_supabase_jwt(token: str, secret: str) -> dict[str, str]:
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("Invalid token") from exc

    sub = cast(str | None, claims.get("sub"))
    if not sub:
        raise AuthError("Invalid token")

    identity: dict[str, str] = {"user_id": sub}

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
