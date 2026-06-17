from __future__ import annotations

import subprocess

import pytest

SANDBOX_IMAGE = "simples-runner:latest"


def _run_container(command: list[str], read_only: bool = True, network_mode: str = "none",
                   pids_limit: int = 64, mem_limit: str = "128m",
                   cap_drop: list[str] | None = None,
                   timeout: int = 15) -> tuple[int, str, str]:
    cap_drop = cap_drop or ["ALL"]
    cmd = [
        "docker", "run", "--rm",
        "--network", network_mode,
        "--memory", mem_limit,
        "--memory-swap", mem_limit,
        "--pids-limit", str(pids_limit),
    ]
    for cap in cap_drop:
        cmd.extend(["--cap-drop", cap])
    cmd.extend([
        "--user", "65534:65534",
    ])
    if read_only:
        cmd.append("--read-only")
        cmd.extend(["--tmpfs", "/tmp:size=8m"])
    cmd.append(SANDBOX_IMAGE)
    cmd.extend(command)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def _run_container_detached(command: list[str], read_only: bool = True, network_mode: str = "none",
                            pids_limit: int = 64, mem_limit: str = "128m",
                            cap_drop: list[str] | None = None,
                            wait_timeout: int = 30) -> tuple[int, str, str]:
    cap_drop = cap_drop or ["ALL"]
    cmd = [
        "docker", "run", "-d",
        "--network", network_mode,
        "--memory", mem_limit,
        "--memory-swap", mem_limit,
        "--pids-limit", str(pids_limit),
    ]
    for cap in cap_drop:
        cmd.extend(["--cap-drop", cap])
    cmd.extend([
        "--user", "65534:65534",
    ])
    if read_only:
        cmd.append("--read-only")
        cmd.extend(["--tmpfs", "/tmp:size=8m"])
    cmd.append(SANDBOX_IMAGE)
    cmd.extend(command)

    run_result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    container_id = run_result.stdout.strip()

    try:
        subprocess.run(
            ["docker", "wait", container_id],
            capture_output=True, text=True, timeout=wait_timeout,
        )
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", container_id], capture_output=True, timeout=10)

    log_result = subprocess.run(
        ["docker", "logs", container_id],
        capture_output=True, text=True, timeout=15,
    )
    inspect_result = subprocess.run(
        ["docker", "inspect", container_id, "--format", "{{.State.ExitCode}}"],
        capture_output=True, text=True, timeout=15,
    )
    subprocess.run(["docker", "rm", "-f", container_id], capture_output=True, timeout=10)

    exit_code = int(inspect_result.stdout.strip())
    return exit_code, log_result.stdout, log_result.stderr


class TestSandboxAudit:
    @pytest.mark.integration
    def test_write_to_root_is_blocked(self):
        returncode, stdout, stderr = _run_container(
            ["sh", "-c", "touch /test-root-file 2>&1; echo exit=$?"],
        )
        assert returncode != 0 or "exit=0" not in stdout, (
            f"Expected write to / to be blocked, got exit={returncode}, "
            f"stdout={stdout!r}, stderr={stderr!r}"
        )

    @pytest.mark.integration
    def test_write_to_tmp_is_allowed(self):
        returncode, stdout, stderr = _run_container(
            ["sh", "-c", "touch /tmp/test-file && echo ok"],
        )
        assert returncode == 0, f"Expected write to /tmp to succeed: {stderr}"
        assert "ok" in stdout

    @pytest.mark.integration
    def test_fork_bomb_is_blocked(self):
        returncode, stdout, stderr = _run_container_detached(
            ["sh", "-c", "i=0; while true; do i=$((i+1)); true & done"],
            pids_limit=64,
        )
        assert returncode != 0, (
            f"Expected fork bomb to be blocked, but container exited 0. "
            f"stdout={stdout!r}, stderr={stderr!r}"
        )

    @pytest.mark.integration
    def test_network_is_blocked(self):
        returncode, stdout, stderr = _run_container(
            ["sh", "-c", "wget -q --timeout=3 http://google.com 2>&1; echo exit=$?"],
            network_mode="none",
        )
        assert "exit=0" not in stdout, (
            f"Expected network to be blocked, got stdout={stdout!r}, "
            f"stderr={stderr!r}"
        )

    @pytest.mark.integration
    def test_cap_drop_all_prevents_raw_sockets(self):
        returncode, stdout, stderr = _run_container(
            ["sh", "-c", "ping -c 1 127.0.0.1 2>&1; echo exit=$?"],
        )
        assert "exit=0" not in stdout, (
            f"Expected ping to fail with cap_drop=ALL, got stdout={stdout!r}, "
            f"stderr={stderr!r}"
        )

    @pytest.mark.integration
    def test_non_root_user_cannot_write_to_system_dirs(self):
        returncode, stdout, stderr = _run_container(
            ["sh", "-c", "touch /usr/test-file 2>&1; echo exit=$?"],
        )
        assert "exit=0" not in stdout, (
            f"Expected non-root user to be blocked from writing to /usr, "
            f"got stdout={stdout!r}, stderr={stderr!r}"
        )

    @pytest.mark.integration
    def test_memory_limit_enforced(self):
        returncode, stdout, stderr = _run_container_detached(
            ["sh", "-c", "dd if=/dev/zero of=/dev/null bs=256M count=1 2>&1; echo exit=$?"],
            mem_limit="128m",
        )
        assert returncode != 0 or "exit=0" not in stdout, (
            f"Expected memory limit to kill process, got stdout={stdout!r}, "
            f"stderr={stderr!r}"
        )


class TestSandboxAuditWithSameFlags:
    @pytest.mark.integration
    def test_all_security_flags_match_production(self):
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "128m",
            "--memory-swap", "128m",
            "--pids-limit", "64",
            "--read-only",
            "--tmpfs", "/tmp:size=8m",
            "--cap-drop", "ALL",
            "--user", "65534:65534",
            SANDBOX_IMAGE,
            "sh", "-c",
            "id && echo ok",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        assert result.returncode == 0, (
            f"Production security flags should still allow normal execution. "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
        assert "uid=65534" in result.stdout
        assert "ok" in result.stdout
