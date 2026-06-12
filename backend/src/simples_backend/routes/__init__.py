from __future__ import annotations

from .auth import create_auth_blueprint
from .compile import create_compile_blueprint
from .health import create_health_blueprint

__all__ = [
    "create_auth_blueprint",
    "create_compile_blueprint",
    "create_health_blueprint",
]
