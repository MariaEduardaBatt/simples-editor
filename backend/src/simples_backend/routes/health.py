from __future__ import annotations

from urllib.error import URLError
from urllib.request import Request, urlopen

import docker
from docker.errors import DockerException
from flask import Blueprint, jsonify

from ..config import Settings

VERSION = "1.0.0"


def create_health_blueprint(settings: Settings) -> Blueprint:
    bp = Blueprint("health", __name__)

    @bp.get("")
    def health():
        components = {
            "supabase": _check_supabase(settings.supabase_url),
            "compiler": {"status": "unavailable"},
            "nasm": {"status": "unavailable"},
            "docker": _check_docker(settings.sandbox_image),
        }
        all_ok = all(c["status"] == "ok" for c in components.values())
        return jsonify(
            {
                "status": "healthy" if all_ok else "degraded",
                "version": VERSION,
                "components": components,
            }
        )

    return bp


def _check_supabase(url: str) -> dict:
    try:
        req = Request(url, method="GET")
        urlopen(req, timeout=3)
        return {"status": "ok"}
    except (URLError, OSError):
        return {"status": "unavailable"}


def _check_docker(sandbox_image: str) -> dict:
    try:
        client = docker.from_env()
        client.ping()
        try:
            client.images.get(sandbox_image)
            return {"status": "ok", "image": sandbox_image}
        except docker.errors.ImageNotFound:
            return {
                "status": "degraded",
                "image": sandbox_image,
                "error": "sandbox image not found",
            }
    except DockerException as e:
        return {"status": "unavailable", "error": str(e)}
