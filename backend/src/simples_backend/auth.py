from __future__ import annotations

import base64
import json
import logging
import urllib.request
from functools import wraps
from typing import Any, Callable, TypeVar, TypedDict, cast

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from flask import g, request

logger = logging.getLogger(__name__)


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


_jwks_keys: list[dict] | None = None


def _b64_decode(value: str) -> bytes:
    padding = 4 - len(value) % 4
    if padding != 4:
        value += "=" * padding
    return base64.urlsafe_b64decode(value)


def _get_jwks_keys(supabase_url: str) -> list[dict]:
    global _jwks_keys
    if _jwks_keys is None:
        base = supabase_url.rstrip("/")
        if "/rest/v1" in base:
            base = base.split("/rest/v1")[0]
        jwks_url = f"{base}/auth/v1/.well-known/jwks.json"
        logger.info("fetching JWKS from %s", jwks_url)
        resp = urllib.request.urlopen(jwks_url, timeout=10)
        data = json.loads(resp.read())
        _jwks_keys = data.get("keys", [])
        logger.info("JWKS loaded: %d keys", len(_jwks_keys))
    return _jwks_keys


def _build_ec_key(key_data: dict):
    x_bytes = _b64_decode(key_data["x"])
    y_bytes = _b64_decode(key_data["y"])
    x_int = int.from_bytes(x_bytes, "big")
    y_int = int.from_bytes(y_bytes, "big")
    return ec.EllipticCurvePublicNumbers(x_int, y_int, ec.SECP256R1()).public_key()


def verify_supabase_jwt(token: str, secret: str, supabase_url: str = "") -> Identity:
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "")
        kid = header.get("kid", "")
        logger.info("JWT alg=%s kid=%s", alg, kid)

        claims = None

        verify_opts = {"require": ["exp", "sub"], "verify_aud": False}

        if alg == "ES256":
            try:
                keys = _get_jwks_keys(supabase_url)
                match = next((k for k in keys if k.get("kid") == kid), None)
                if match:
                    pubkey = _build_ec_key(match)
                    claims = jwt.decode(
                        token,
                        pubkey,
                        algorithms=["ES256"],
                        options=verify_opts,
                    )
                    logger.info("JWT verified with ES256+JWKS")
                else:
                    logger.warning("no JWKS key found for kid=%s", kid)
            except Exception as exc:
                logger.error("ES256+JWKS failed: %s: %s", type(exc).__name__, exc)

        if claims is None and alg == "HS256":
            claims = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options=verify_opts,
            )
            logger.info("JWT verified with HS256")

    except jwt.ExpiredSignatureError as exc:
        raise AuthError("expired_token") from exc
    except jwt.InvalidTokenError as exc:
        logger.error("JWT invalid: %s: %s", type(exc).__name__, exc)
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
