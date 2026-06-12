from __future__ import annotations

import pytest

from simples_backend.config import Settings


TEST_SECRET = "0123456789abcdef0123456789abcdef"


@pytest.fixture()
def settings() -> Settings:
    return Settings(supabase_url="http://test", supabase_jwt_secret=TEST_SECRET)


@pytest.fixture()
def app(settings: Settings):
    from simples_backend.app import create_app

    return create_app(settings)


@pytest.fixture()
def client(app):
    return app.test_client()
