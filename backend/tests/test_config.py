import pytest

from simples_backend.config import Settings, _int_env, load_settings


def test_load_settings_requires_supabase_env_vars(monkeypatch):
    monkeypatch.delenv('SUPABASE_URL', raising=False)
    monkeypatch.delenv('JWT_SECRET', raising=False)

    with pytest.raises(RuntimeError, match='SUPABASE_URL, JWT_SECRET'):
        load_settings()


def test_load_settings_success(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'http://test')
    monkeypatch.setenv('JWT_SECRET', 'my-secret')
    monkeypatch.setenv('EXEC_TIMEOUT_S', '20')

    settings = load_settings()

    assert settings.supabase_url == 'http://test'
    assert settings.supabase_jwt_secret == 'my-secret'
    assert settings.exec_timeout_s == 20
    assert settings.sandbox_image == 'simples-runner:latest'


def test_load_settings_with_environ_dict(monkeypatch):
    env = {
        'SUPABASE_URL': 'http://custom',
        'JWT_SECRET': 'custom-secret',
        'EXEC_TIMEOUT_S': '30',
        'MAX_CODE_KB': '128',
        'SANDBOX_IMAGE': 'custom-image:v2',
    }
    settings = load_settings(env)

    assert settings.supabase_url == 'http://custom'
    assert settings.supabase_jwt_secret == 'custom-secret'
    assert settings.exec_timeout_s == 30
    assert settings.max_code_kb == 128
    assert settings.sandbox_image == 'custom-image:v2'


def test__int_env_missing_key_returns_default():
    assert _int_env({}, 'NONEXISTENT', 42) == 42


def test__int_env_valid_int_returns_value():
    assert _int_env({'MY_KEY': '10'}, 'MY_KEY', 42) == 10


def test__int_env_invalid_string_returns_default():
    assert _int_env({'MY_KEY': 'not-a-number'}, 'MY_KEY', 42) == 42


def test__int_env_empty_string_returns_default():
    assert _int_env({'MY_KEY': ''}, 'MY_KEY', 42) == 42


def test_settings_frozen():
    s = Settings(supabase_url='http://test', supabase_jwt_secret='secret')
    with pytest.raises(Exception):
        s.supabase_url = 'http://other'

