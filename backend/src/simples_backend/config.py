from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_jwt_secret: str


_REQUIRED_ENV_VARS = ("SUPABASE_URL", "SUPABASE_JWT_SECRET")


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if environ is None else environ

    missing = [key for key in _REQUIRED_ENV_VARS if not env.get(key)]
    if missing:
        raise RuntimeError(
            f"Required environment variables not set: {', '.join(missing)}"
        )

    return Settings(
        supabase_url=env["SUPABASE_URL"],
        supabase_jwt_secret=env["SUPABASE_JWT_SECRET"],
    )
