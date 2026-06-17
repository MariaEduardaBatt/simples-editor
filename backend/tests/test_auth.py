from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from flask import Flask, g
import jwt

from simples_backend.auth import (
    AuthError,
    _b64_decode,
    _build_ec_key,
    _get_jwks_keys,
    extract_bearer_token,
    verify_jwt,
    verify_supabase_jwt,
)


def _make_token(
    secret: str,
    *,
    sub: str = "user-123",
    email: str | None = "user@example.com",
    exp: datetime | None = None,
    algorithm: str = "HS256",
    headers: dict | None = None,
) -> str:
    payload: dict[str, object] = {
        "sub": sub,
        "exp": exp or (datetime.now(tz=timezone.utc) + timedelta(minutes=5)),
    }
    if email is not None:
        payload["email"] = email

    return jwt.encode(payload, secret, algorithm=algorithm, headers=headers or {})


TEST_SECRET = "0123456789abcdef0123456789abcdef"


def test_extract_bearer_token_happy_path():
    assert extract_bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"


@pytest.mark.parametrize("header", [None, ""])
def test_extract_bearer_token_missing_header_raises(header):
    with pytest.raises(AuthError, match="missing_bearer_token"):
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
    with pytest.raises(AuthError, match="malformed_bearer_token"):
        extract_bearer_token(header)


def test_verify_supabase_jwt_valid_signature_and_exp_returns_identity():
    token = _make_token(TEST_SECRET, sub="user-123", email="user@example.com")

    identity = verify_supabase_jwt(token, TEST_SECRET)

    assert identity == {"user_id": "user-123", "email": "user@example.com"}


def test_verify_supabase_jwt_invalid_signature_raises_auth_error():
    token = _make_token(TEST_SECRET)

    with pytest.raises(AuthError, match="invalid_token"):
        verify_supabase_jwt(token, "fedcba9876543210fedcba9876543210")


def test_verify_supabase_jwt_expired_token_raises_auth_error():
    expired = datetime.now(tz=timezone.utc) - timedelta(minutes=1)
    token = _make_token(TEST_SECRET, exp=expired)

    with pytest.raises(AuthError, match="expired_token"):
        verify_supabase_jwt(token, TEST_SECRET)


def test_verify_jwt_decorator_sets_g_identity_and_invokes_wrapped_view():
    token = _make_token(TEST_SECRET, sub="user-abc", email="decorator@example.com")
    app = Flask(__name__)

    @verify_jwt(TEST_SECRET)
    def view_func():
        return g.identity

    with app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
        result = view_func()

    assert result == {"user_id": "user-abc", "email": "decorator@example.com"}


class TestAuthErrorStr:
    def test_str(self):
        err = AuthError("missing_bearer_token")
        assert str(err) == "missing_bearer_token"


class TestB64Decode:
    def test_decode_without_padding(self):
        result = _b64_decode("dGVzdA")
        assert result == b"test"

    def test_decode_with_full_padding(self):
        result = _b64_decode("dGVzdA==")
        assert result == b"test"

    def test_decode_empty(self):
        result = _b64_decode("")
        assert result == b""


class TestGetJwksKeys:
    def _gen_ec_key_data(self):
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        pub_numbers = public_key.public_numbers()

        def _b64encode_no_pad(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

        x_b64 = _b64encode_no_pad(pub_numbers.x.to_bytes(32, "big"))
        y_b64 = _b64encode_no_pad(pub_numbers.y.to_bytes(32, "big"))

        return {
            "kty": "EC",
            "crv": "P-256",
            "kid": "test-key-1",
            "x": x_b64,
            "y": y_b64,
        }

    @patch("simples_backend.auth._jwks_keys", None)
    @patch("simples_backend.auth.urllib.request.urlopen")
    def test_fetch_keys_from_supabase(self, mock_urlopen):
        key_data = self._gen_ec_key_data()

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"keys": [key_data]}).encode()
        mock_urlopen.return_value = mock_response

        keys = _get_jwks_keys("https://project.supabase.co")

        assert len(keys) == 1
        assert keys[0]["kid"] == "test-key-1"
        mock_urlopen.assert_called_once()
        url = mock_urlopen.call_args[0][0]
        assert "auth/v1/.well-known/jwks.json" in url

    @patch("simples_backend.auth._jwks_keys", None)
    def test_fetch_keys_from_supabase_with_rest_v1(self):
        from unittest.mock import patch as p

        key_data = self._gen_ec_key_data()

        with p("simples_backend.auth.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({"keys": [key_data]}).encode()
            mock_urlopen.return_value = mock_response

            keys = _get_jwks_keys("https://project.supabase.co/rest/v1/")

            url = mock_urlopen.call_args[0][0]
            assert "/rest/v1" not in url.split("co")[1]
            assert "auth/v1/.well-known/jwks.json" in url

    @patch("simples_backend.auth._jwks_keys", None)
    def test_caches_result(self):
        key_data = self._gen_ec_key_data()

        with patch("simples_backend.auth.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({"keys": [key_data]}).encode()
            mock_urlopen.return_value = mock_response

            keys1 = _get_jwks_keys("https://project.supabase.co")
            keys2 = _get_jwks_keys("https://project.supabase.co")

            assert mock_urlopen.call_count == 1
            assert keys1 == keys2

    @patch("simples_backend.auth._jwks_keys", None)
    def test_empty_keys_when_no_keys_in_response(self):
        with patch("simples_backend.auth.urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({"keys": []}).encode()
            mock_urlopen.return_value = mock_response

            keys = _get_jwks_keys("https://project.supabase.co")

            assert keys == []


class TestBuildEcKey:
    def _b64encode_no_pad(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    def test_build_public_key(self):
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        pub_numbers = public_key.public_numbers()

        key_data = {
            "x": self._b64encode_no_pad(pub_numbers.x.to_bytes(32, "big")),
            "y": self._b64encode_no_pad(pub_numbers.y.to_bytes(32, "big")),
        }

        rebuilt = _build_ec_key(key_data)
        rebuilt_numbers = rebuilt.public_numbers()

        assert rebuilt_numbers.x == pub_numbers.x
        assert rebuilt_numbers.y == pub_numbers.y


class TestVerifySupabaseJwtES256:
    def test_es256_verification_success(self):
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        pub_numbers = public_key.public_numbers()

        def _b64encode_no_pad(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

        kid = "test-key-1"

        token = _make_token(
            private_key,
            sub="user-es256",
            email="es256@example.com",
            algorithm="ES256",
            headers={"kid": kid},
        )

        key_data = {
            "kty": "EC",
            "crv": "P-256",
            "kid": kid,
            "x": _b64encode_no_pad(pub_numbers.x.to_bytes(32, "big")),
            "y": _b64encode_no_pad(pub_numbers.y.to_bytes(32, "big")),
        }

        with patch(
            "simples_backend.auth._get_jwks_keys",
            return_value=[key_data],
        ):
            identity = verify_supabase_jwt(
                token, "", supabase_url="https://project.supabase.co"
            )

        assert identity == {"user_id": "user-es256", "email": "es256@example.com"}

    def test_es256_no_matching_kid_falls_back_to_hs256(self):
        private_key = ec.generate_private_key(ec.SECP256R1())

        kid = "unknown-kid"
        token = _make_token(
            private_key,
            sub="user-fallback",
            algorithm="ES256",
            headers={"kid": kid},
        )

        with patch(
            "simples_backend.auth._get_jwks_keys",
            return_value=[{"kid": "other-key"}],
        ):
            with pytest.raises(AuthError, match="invalid_token"):
                verify_supabase_jwt(
                    token, TEST_SECRET, supabase_url="https://project.supabase.co"
                )

    def test_es256_jwks_fetch_failure_logs_and_falls_back(self):
        private_key = ec.generate_private_key(ec.SECP256R1())

        token = _make_token(
            private_key,
            sub="user-jwks-fail",
            algorithm="ES256",
            headers={"kid": "any-kid"},
        )

        with patch(
            "simples_backend.auth._get_jwks_keys",
            side_effect=Exception("connection refused"),
        ):
            with pytest.raises(AuthError, match="invalid_token"):
                verify_supabase_jwt(
                    token, TEST_SECRET, supabase_url="https://project.supabase.co"
                )

    def test_no_email_in_claims(self):
        token = _make_token(TEST_SECRET, sub="user-noemail", email=None)

        identity = verify_supabase_jwt(token, TEST_SECRET)

        assert identity == {"user_id": "user-noemail"}

    def test_non_string_email(self):
        payload = {
            "sub": "user-nonstring-email",
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
            "email": 12345,
        }
        token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")

        identity = verify_supabase_jwt(token, TEST_SECRET)

        assert "email" not in identity

    def test_empty_email_string(self):
        payload = {
            "sub": "user-empty-email",
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
            "email": "",
        }
        token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")

        identity = verify_supabase_jwt(token, TEST_SECRET)

        assert "email" not in identity
