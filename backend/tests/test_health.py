from __future__ import annotations


def test_health_returns_200_without_auth(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_health_returns_expected_structure(client):
    resp = client.get("/api/health")
    body = resp.get_json()

    assert "status" in body
    assert "version" in body
    assert "components" in body

    assert "supabase" in body["components"]
    assert "compiler" in body["components"]
    assert "nasm" in body["components"]
    assert "docker" in body["components"]


def test_health_version_is_string(client):
    resp = client.get("/api/health")
    assert isinstance(resp.get_json()["version"], str)


def test_health_component_has_status(client):
    resp = client.get("/api/health")
    components = resp.get_json()["components"]
    for name, info in components.items():
        assert "status" in info, f"component {name!r} is missing status"
