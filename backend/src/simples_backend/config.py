from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_jwt_secret: str
    exec_timeout_s: int = 10
    compile_timeout_s: int = 15
    max_code_kb: int = 64
    sandbox_image: str = "simples-runner:latest"
    stop_timeout_s: int = 12
    runs_per_minute: int = 30
    runs_per_minute_ip: int = 120
    redis_url: str = "memory://"


_REQUIRED_ENV_VARS = ("SUPABASE_URL", "JWT_SECRET")


def _int_env(env: Mapping[str, str], key: str, default: int) -> int:
    val = env.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if environ is None else environ

    missing = [key for key in _REQUIRED_ENV_VARS if not env.get(key)]
    if missing:
        raise RuntimeError(
            f"Required environment variables not set: {', '.join(missing)}"
        )

    return Settings(
        supabase_url=env["SUPABASE_URL"],
        supabase_jwt_secret=env["JWT_SECRET"],
        exec_timeout_s=_int_env(env, "EXEC_TIMEOUT_S", 10),
        compile_timeout_s=_int_env(env, "COMPILE_TIMEOUT_S", 15),
        max_code_kb=_int_env(env, "MAX_CODE_KB", 64),
        sandbox_image=env.get("SANDBOX_IMAGE", "simples-runner:latest"),
        stop_timeout_s=_int_env(env, "STOP_TIMEOUT_S", 12),
        runs_per_minute=_int_env(env, "RUNS_PER_MINUTE", 30),
        runs_per_minute_ip=_int_env(env, "RUNS_PER_MINUTE_IP", 120),
        redis_url=env.get("REDIS_URL", "memory://"),
    )
