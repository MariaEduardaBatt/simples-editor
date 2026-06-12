import pytest

from simples_backend.config import load_settings


def test_load_settings_requires_supabase_env_vars(monkeypatch):
    monkeypatch.delenv('SUPABASE_URL', raising=False)
    monkeypatch.delenv('SUPABASE_JWT_SECRET', raising=False)

    with pytest.raises(RuntimeError, match='SUPABASE_URL, SUPABASE_JWT_SECRET'):
        load_settings()
