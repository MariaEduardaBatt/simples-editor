from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from simples_backend.services.execution_service import (
    ExecutionError,
    assemble_nasm,
    link_object,
)


class TestExecutionError:
    def test_fields(self):
        err = ExecutionError("nasm failed", "nasm")
        assert err.message == "nasm failed"
        assert err.phase == "nasm"


class TestAssembleNasm:
    def test_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("simples_backend.services.execution_service.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stderr = ""

                result = assemble_nasm("section .data\n", tmpdir)

                assert result == os.path.join(tmpdir, "programa.o")
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert "nasm" in args[0]
                assert "-f" in args
                assert "elf32" in args

    def test_nasm_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("simples_backend.services.execution_service.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "error: invalid instruction\n"

                with pytest.raises(ExecutionError) as exc_info:
                    assemble_nasm("invalid asm", tmpdir)

                assert exc_info.value.phase == "nasm"
                assert "invalid instruction" in exc_info.value.message

    def test_nasm_failure_empty_stderr(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("simples_backend.services.execution_service.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = ""

                with pytest.raises(ExecutionError) as exc_info:
                    assemble_nasm("invalid asm", tmpdir)

                assert exc_info.value.phase == "nasm"
                assert exc_info.value.message == "unknown nasm error"


class TestLinkObject:
    def test_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = os.path.join(tmpdir, "programa.o")
            with open(obj_path, "w") as f:
                f.write("")

            with patch("simples_backend.services.execution_service.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stderr = ""

                result = link_object(obj_path, tmpdir)

                assert result == os.path.join(tmpdir, "programa")
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert any("ld" in arg for arg in args)
                assert "-m" in args
                assert "elf_i386" in args

    def test_link_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = os.path.join(tmpdir, "programa.o")
            with open(obj_path, "w") as f:
                f.write("")

            with patch("simples_backend.services.execution_service.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "undefined reference to `_start'\n"

                with pytest.raises(ExecutionError) as exc_info:
                    link_object(obj_path, tmpdir)

                assert exc_info.value.phase == "ld"
                assert "undefined reference" in exc_info.value.message

    def test_link_failure_empty_stderr(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = os.path.join(tmpdir, "programa.o")
            with open(obj_path, "w") as f:
                f.write("")

            with patch("simples_backend.services.execution_service.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = ""

                with pytest.raises(ExecutionError) as exc_info:
                    link_object(obj_path, tmpdir)

                assert exc_info.value.phase == "ld"
                assert exc_info.value.message == "unknown ld error"

    def test_custom_ld_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = os.path.join(tmpdir, "programa.o")
            with open(obj_path, "w") as f:
                f.write("")

            with patch("simples_backend.services.execution_service.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stderr = ""

                with patch("simples_backend.services.execution_service.shutil.which", return_value="/usr/local/bin/i686-linux-gnu-ld"):
                    link_object(obj_path, tmpdir)

                args = mock_run.call_args[0][0]
                assert args[0] == "/usr/local/bin/i686-linux-gnu-ld"
