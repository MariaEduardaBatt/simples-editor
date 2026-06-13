from __future__ import annotations

import json
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Empty, Queue

import docker


@dataclass
class ExecutionResult:
    exit_code: int
    duration_ms: int
    timed_out: bool


class ExecutionStrategy(ABC):
    @abstractmethod
    def execute(self, binary_dir: str, ws, timeout_s: int) -> ExecutionResult:
        ...


class PtyExecutionStrategy(ExecutionStrategy):
    def __init__(self, image: str = "simples-runner:latest"):
        self.image = image
        self.client = docker.from_env()

    def execute(self, binary_dir: str, ws, timeout_s: int) -> ExecutionResult:
        container = self.client.containers.run(
            image=self.image,
            command=["/usr/bin/qemu-i386-static", "/sandbox/programa"],
            volumes={binary_dir: {"bind": "/sandbox", "mode": "ro"}},
            network_mode="none",
            mem_limit="128m",
            memswap_limit="128m",
            cpu_quota=50000,
            pids_limit=64,
            read_only=True,
            tmpfs={"/tmp": "size=8m"},
            user="65534:65534",
            cap_drop=["ALL"],
            stdin_open=True,
            tty=True,
            detach=True,
        )

        sock = container.attach_socket(
            params={"stdin": 1, "stdout": 1, "stderr": 1, "stream": 1}
        )
        sock._sock.setblocking(False)

        output_queue: Queue[tuple[str, object]] = Queue()
        stop_event = threading.Event()
        start = time.monotonic()
        timed_out = False

        def _send(msg: dict) -> None:
            try:
                ws.send(json.dumps(msg, ensure_ascii=False))
            except Exception:
                pass

        def _reader() -> None:
            try:
                while not stop_event.is_set():
                    try:
                        data = sock._sock.recv(4096)
                        if not data:
                            break
                        output_queue.put(("stdout", data))
                    except BlockingIOError:
                        time.sleep(0.01)
            except Exception:
                pass
            finally:
                output_queue.put(("_exit", None))

        reader_thread = threading.Thread(target=_reader, daemon=True)
        reader_thread.start()

        try:
            while True:
                try:
                    kind, data = output_queue.get_nowait()
                    if kind == "_exit":
                        break
                    _send({
                        "type": "stdout",
                        "data": data.decode("utf-8", errors="replace"),
                    })
                    continue
                except Empty:
                    pass

                elapsed = time.monotonic() - start
                if elapsed > timeout_s:
                    try:
                        container.kill(signal="SIGTERM")
                        time.sleep(1)
                        container.kill(signal="SIGKILL")
                    except Exception:
                        pass
                    timed_out = True
                    _send({"type": "timeout", "limit_s": timeout_s})
                    break

                try:
                    raw = ws.receive(timeout=0.05)
                except Exception:
                    break
                if raw is None:
                    break

                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                t = msg.get("type", "")
                if t == "stdin":
                    data = msg.get("data", "")
                    if data:
                        sock._sock.sendall(data.encode("utf-8"))
                elif t == "stop":
                    try:
                        container.kill(signal="SIGTERM")
                    except Exception:
                        pass
                    break
                elif t == "ping":
                    _send({"type": "pong"})
        finally:
            stop_event.set()
            reader_thread.join(timeout=2)

        try:
            result = container.wait(timeout=5)
            exit_code = result["StatusCode"]
        except Exception:
            exit_code = -1

        duration_ms = int((time.monotonic() - start) * 1000)

        try:
            container.remove(force=True)
        except Exception:
            pass

        return ExecutionResult(
            exit_code=exit_code,
            duration_ms=duration_ms,
            timed_out=timed_out,
        )
