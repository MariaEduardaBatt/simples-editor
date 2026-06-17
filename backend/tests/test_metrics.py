from __future__ import annotations

from unittest.mock import patch

from simples_backend.services.compiler_service import CompilerError

CODE = "programa exemplo\ninteiro x\ninicio\nfim"
NASM_OUTPUT = "section .data\n  x dd 0\nsection .text\n  global _start\n_start:\n  mov eax, 1\n  xor ebx, ebx\n  int 0x80"


def _make_token(secret: str) -> str:
    import jwt
    from datetime import datetime, timedelta, timezone
    return jwt.encode(
        {"sub": "user-123", "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5)},
        secret,
        algorithm="HS256",
    )


def test_metrics_endpoint_returns_200(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200


def test_metrics_endpoint_prometheus_format(client):
    resp = client.get("/metrics")
    assert resp.content_type.startswith("text/plain; version=")
    assert "charset=utf-8" in resp.content_type


def test_metrics_contains_compile_histogram(client):
    resp = client.get("/metrics")
    assert "simples_compile_duration_seconds" in resp.text


def test_metrics_contains_compile_errors_total(client):
    resp = client.get("/metrics")
    assert "simples_compile_errors_total" in resp.text


def test_metrics_contains_execution_histogram(client):
    resp = client.get("/metrics")
    assert "simples_execution_duration_seconds" in resp.text


def test_metrics_contains_executions_total(client):
    resp = client.get("/metrics")
    assert "simples_executions_total" in resp.text


def test_metrics_contains_active_sandboxes(client):
    resp = client.get("/metrics")
    assert "simples_active_sandboxes" in resp.text


def test_metrics_contains_websocket_connections(client):
    resp = client.get("/metrics")
    assert "simples_websocket_connections" in resp.text


def test_metrics_contains_http_requests_total(client):
    resp = client.get("/metrics")
    assert "simples_http_requests_total" in resp.text


def test_compile_success_increments_metrics(client, settings):
    token = _make_token(settings.supabase_jwt_secret)

    with patch("simples_backend.routes.compile.compile_simples", return_value=NASM_OUTPUT):
        resp_before = client.get("/metrics")
        assert resp_before.status_code == 200

        resp = client.post(
            "/api/compile",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": CODE},
        )
        assert resp.status_code == 200

        resp_after = client.get("/metrics")
        assert resp_after.status_code == 200

    text_before = resp_before.text
    text_after = resp_after.text

    for line in text_after.splitlines():
        if line.startswith("simples_compile_duration_seconds_count"):
            count_before = _extract_value(text_before, "simples_compile_duration_seconds_count")
            count_after = float(line.split()[1])
            assert count_after == count_before + 1, "compile histogram count should increase"
            break


def _extract_value(text: str, metric_name: str) -> float:
    for line in text.splitlines():
        if line.startswith(metric_name) and "{" not in line:
            return float(line.split()[1])
    return 0.0


def test_compile_error_increments_error_counter(client, settings):
    token = _make_token(settings.supabase_jwt_secret)

    with patch(
        "simples_backend.routes.compile.compile_simples",
        side_effect=CompilerError("syntax error", phase="parser", line=1, column=5),
    ):
        resp_before = client.get("/metrics")
        error_before = sum(
            float(line.split()[1])
            for line in resp_before.text.splitlines()
            if line.startswith('simples_compile_errors_total{error_type="parser"}')
        )

        resp = client.post(
            "/api/compile",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": CODE},
        )
        assert resp.status_code == 200

        resp_after = client.get("/metrics")
        error_after = sum(
            float(line.split()[1])
            for line in resp_after.text.splitlines()
            if line.startswith('simples_compile_errors_total{error_type="parser"}')
        )

    assert error_after == error_before + 1
