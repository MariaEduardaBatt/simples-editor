from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

compile_duration = Histogram(
    "simples_compile_duration_seconds",
    "Tempo de compilação do código SIMPLES",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

compile_errors_total = Counter(
    "simples_compile_errors_total",
    "Total de erros de compilação",
    labelnames=["error_type"],
)

execution_duration = Histogram(
    "simples_execution_duration_seconds",
    "Tempo de execução do código compilado",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

executions_total = Counter(
    "simples_executions_total",
    "Total de execuções",
    labelnames=["status"],
)

active_sandboxes = Gauge(
    "simples_active_sandboxes",
    "Número de sandboxes ativos no momento",
)

websocket_connections = Gauge(
    "simples_websocket_connections",
    "Número de conexões WebSocket ativas",
)

http_requests_total = Counter(
    "simples_http_requests_total",
    "Total de requisições HTTP",
    labelnames=["method", "endpoint", "status"],
)
