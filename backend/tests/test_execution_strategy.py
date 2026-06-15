from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from simples_backend.services.execution_strategy import (
    ExecutionResult,
    ExecutionStrategy,
    PtyExecutionStrategy,
)


@pytest.fixture
def binary_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        bin_path = os.path.join(tmpdir, "programa")
        with open(bin_path, "wb") as f:
            f.write(b"dummy binary")
        yield tmpdir


def _docker_frame(stream_id: int, payload: bytes) -> bytes:
    return bytes([stream_id]) + b"\x00\x00\x00" + len(payload).to_bytes(4, "big") + payload


class TestExecutionResult:
    def test_dataclass_fields(self):
        result = ExecutionResult(exit_code=0, duration_ms=100, timed_out=False)
        assert result.exit_code == 0
        assert result.duration_ms == 100
        assert result.timed_out is False

    def test_timed_out_true(self):
        result = ExecutionResult(exit_code=-1, duration_ms=5000, timed_out=True)
        assert result.timed_out is True


class TestExecutionStrategyABC:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ExecutionStrategy()


class TestPtyExecutionStrategy:
    @patch("simples_backend.services.execution_strategy.docker")
    def test_init_default_image(self, mock_docker):
        strategy = PtyExecutionStrategy()
        assert strategy.image == "simples-runner:latest"
        mock_docker.from_env.assert_called_once()

    @patch("simples_backend.services.execution_strategy.docker")
    def test_init_custom_image(self, mock_docker):
        strategy = PtyExecutionStrategy(image="custom:tag")
        assert strategy.image == "custom:tag"

    def _setup_mocks(self, mock_client, binary_dir, recv_side_effect=None, wait_status=0, ws_receive=None):
        mock_container = MagicMock()
        mock_sock = MagicMock()
        mock_sock._sock = MagicMock()
        mock_container.attach_socket.return_value = mock_sock
        mock_sock._sock.setblocking = MagicMock()

        if recv_side_effect is not None:
            mock_sock._sock.recv.side_effect = recv_side_effect
        else:
            mock_sock._sock.recv.side_effect = [b""]

        mock_container.wait.return_value = {"StatusCode": wait_status}
        mock_ws = MagicMock()
        mock_ws.receive.return_value = ws_receive

        mock_client.api.create_host_config.return_value = {"NetworkMode": "none"}
        mock_client.api.create_container.return_value = {"Id": "fake-container-id"}
        mock_client.containers.get.return_value = mock_container

        return mock_container, mock_sock, mock_ws

    @patch("simples_backend.services.execution_strategy.docker")
    def test_execute_creates_container_with_correct_params(self, mock_docker, binary_dir):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_container, mock_sock, mock_ws = self._setup_mocks(mock_client, binary_dir)

        strategy = PtyExecutionStrategy()
        result = strategy.execute(binary_dir, mock_ws, timeout_s=10)

        assert isinstance(result, ExecutionResult)
        assert result.exit_code == 0
        assert result.duration_ms >= 0
        assert result.timed_out is False

        mock_client.api.create_host_config.assert_called_once_with(
            network_mode="none",
            mem_limit="128m",
            memswap_limit="128m",
            cpu_quota=50000,
            pids_limit=64,
            read_only=True,
            tmpfs={"/tmp": "size=8m"},
            cap_drop=["ALL"],
            binds={binary_dir: {"bind": "/sandbox", "mode": "ro"}},
        )
        mock_client.api.create_container.assert_called_once_with(
            image="simples-runner:latest",
            command=["/usr/bin/qemu-i386-static", "/sandbox/programa"],
            user="65534:65534",
            stdin_open=True,
            tty=True,
            detach=True,
            host_config={"NetworkMode": "none"},
            stop_timeout=12,
        )
        mock_client.containers.get.assert_called_once_with("fake-container-id")

    @patch("simples_backend.services.execution_strategy.docker")
    def test_execute_returns_result_with_exit_code_and_duration(self, mock_docker, binary_dir):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_container, mock_sock, mock_ws = self._setup_mocks(mock_client, binary_dir, wait_status=42)

        strategy = PtyExecutionStrategy()
        result = strategy.execute(binary_dir, mock_ws, timeout_s=10)

        assert result.exit_code == 42
        assert result.duration_ms >= 0

    @patch("simples_backend.services.execution_strategy.docker")
    def test_stdout_forwarded_to_ws(self, mock_docker, binary_dir):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_container, mock_sock, mock_ws = self._setup_mocks(
            mock_client, binary_dir,
            recv_side_effect=[
                _docker_frame(1, b"line1\n"),
                _docker_frame(1, b"line2\n"),
                b"",
            ],
        )

        strategy = PtyExecutionStrategy()
        strategy.execute(binary_dir, mock_ws, timeout_s=10)

        stdout_messages = [
            json.loads(call[0][0])
            for call in mock_ws.send.call_args_list
            if json.loads(call[0][0]).get("type") == "stdout"
        ]
        assert len(stdout_messages) >= 2
        assert stdout_messages[0]["data"] == "line1\n"
        assert stdout_messages[1]["data"] == "line2\n"

    @patch("simples_backend.services.execution_strategy.docker")
    def test_container_removed_after_execution(self, mock_docker, binary_dir):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_container, mock_sock, mock_ws = self._setup_mocks(mock_client, binary_dir)

        strategy = PtyExecutionStrategy()
        strategy.execute(binary_dir, mock_ws, timeout_s=10)

        mock_container.remove.assert_called_once_with(force=True)

    @patch("simples_backend.services.execution_strategy.docker")
    def test_stdin_forwarded_to_container(self, mock_docker, binary_dir):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_container, mock_sock, mock_ws = self._setup_mocks(
            mock_client, binary_dir,
            recv_side_effect=[],
            ws_receive=None,
        )

        reader_block = threading.Event()
        recv_calls = iter([_docker_frame(1, b"prompt> ")])

        def mock_recv(size):
            try:
                return next(recv_calls)
            except StopIteration:
                reader_block.wait(timeout=10)
                return b""

        mock_sock._sock.recv = MagicMock(side_effect=mock_recv)
        mock_container.wait.return_value = {"StatusCode": 0}

        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "stdin", "data": "42\n"}),
            None,
        ]

        strategy = PtyExecutionStrategy()
        strategy.execute(binary_dir, mock_ws, timeout_s=10)

        mock_sock._sock.sendall.assert_called()

    @patch("simples_backend.services.execution_strategy.docker")
    def test_stop_kills_container(self, mock_docker, binary_dir):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_container, mock_sock, mock_ws = self._setup_mocks(
            mock_client, binary_dir,
            recv_side_effect=[],
            ws_receive=None,
        )

        reader_block = threading.Event()
        recv_calls = iter([_docker_frame(1, b"output\n")])

        def mock_recv(size):
            try:
                return next(recv_calls)
            except StopIteration:
                reader_block.wait(timeout=10)
                return b""

        mock_sock._sock.recv = MagicMock(side_effect=mock_recv)
        mock_container.wait.return_value = {"StatusCode": 137}

        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "stop"}),
            None,
        ]

        strategy = PtyExecutionStrategy()
        result = strategy.execute(binary_dir, mock_ws, timeout_s=10)

        mock_container.kill.assert_any_call(signal="SIGTERM")

    @patch("simples_backend.services.execution_strategy.docker")
    def test_ping_pong(self, mock_docker, binary_dir):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_container, mock_sock, mock_ws = self._setup_mocks(
            mock_client, binary_dir,
            recv_side_effect=[],
            ws_receive=None,
        )

        reader_block = threading.Event()
        recv_calls = iter([_docker_frame(1, b"line\n")])

        def mock_recv(size):
            try:
                return next(recv_calls)
            except StopIteration:
                reader_block.wait(timeout=10)
                return b""

        mock_sock._sock.recv = MagicMock(side_effect=mock_recv)
        mock_container.wait.return_value = {"StatusCode": 0}

        mock_ws = MagicMock()
        mock_ws.receive.side_effect = [
            json.dumps({"type": "ping"}),
            None,
        ]

        strategy = PtyExecutionStrategy()
        strategy.execute(binary_dir, mock_ws, timeout_s=10)

        pong_messages = [
            json.loads(call[0][0])
            for call in mock_ws.send.call_args_list
            if json.loads(call[0][0]).get("type") == "pong"
        ]
        assert len(pong_messages) >= 1

    @patch("simples_backend.services.execution_strategy.docker")
    def test_timeout_triggers_kill_and_returns_timed_out(self, mock_docker, binary_dir):
        mock_client = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_container, mock_sock, mock_ws = self._setup_mocks(
            mock_client, binary_dir,
            recv_side_effect=[],
            ws_receive=None,
        )

        reader_block = threading.Event()

        def mock_recv(size):
            reader_block.wait(timeout=10)
            return b""

        mock_sock._sock.recv = MagicMock(side_effect=mock_recv)
        mock_container.wait.return_value = {"StatusCode": 137}

        mock_ws = MagicMock()
        mock_ws.receive.side_effect = lambda timeout=None: json.dumps(
            {"type": "ping"}
        )

        strategy = PtyExecutionStrategy()
        result = strategy.execute(binary_dir, mock_ws, timeout_s=0.05)

        assert result.timed_out is True
        mock_container.stop.assert_called_once_with(timeout=12)

        timeout_messages = [
            json.loads(call[0][0])
            for call in mock_ws.send.call_args_list
            if json.loads(call[0][0]).get("type") == "timeout"
        ]
        assert len(timeout_messages) >= 1
        assert timeout_messages[0]["limit_s"] == 0.05
