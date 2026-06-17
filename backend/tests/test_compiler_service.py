from __future__ import annotations

from unittest.mock import patch

import pytest

from simples_backend.services.compiler_service import (
    CompilerError,
    _parse_stderr,
    compile_simples,
)


class TestCompilerError:
    def test_fields(self):
        err = CompilerError("msg", phase="lexer", line=1, column=5)
        assert err.message == "msg"
        assert err.phase == "lexer"
        assert err.line == 1
        assert err.column == 5

    def test_no_phase(self):
        err = CompilerError("msg")
        assert err.message == "msg"
        assert err.phase is None


class TestParseStderr:
    def test_parsed_format(self):
        err = _parse_stderr("lexer:1:5: invalid character")
        assert err.phase == "lexer"
        assert err.line == 1
        assert err.column == 5
        assert err.message == "invalid character"

    def test_unparseable_stderr(self):
        err = _parse_stderr("some random error message")
        assert err.message == "some random error message"
        assert err.phase is None

    def test_empty_stderr(self):
        err = _parse_stderr("")
        assert err.message == ""

    def test_whitespace_stderr(self):
        err = _parse_stderr("  ")
        assert err.message == ""

    def test_semantic_error(self):
        err = _parse_stderr("semantic:3:10: variable not declared")
        assert err.phase == "semantic"
        assert err.line == 3
        assert err.column == 10
        assert err.message == "variable not declared"


class TestCompileSimples:
    def test_compiler_not_found(self):
        with patch("simples_backend.services.compiler_service.shutil.which", return_value=None):
            with pytest.raises(CompilerError, match="compiler not found"):
                compile_simples("programa exemplo\ninicio\nfim")

    @patch("simples_backend.services.compiler_service.shutil.which", return_value="/usr/bin/simplesc")
    @patch("simples_backend.services.compiler_service.subprocess.run")
    def test_compile_success(self, mock_run, mock_which):
        import os
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""

        asm_content = "section .data\nsection .text"
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("simples_backend.services.compiler_service.tempfile.TemporaryDirectory") as mock_tmpdir:
                mock_tmpdir.return_value.__enter__.return_value = tmpdir
                output_path = os.path.join(tmpdir, "output.asm")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(asm_content)

                result = compile_simples("programa exemplo\ninicio\nfim")

                assert result == asm_content

    @patch("simples_backend.services.compiler_service.shutil.which", return_value="/usr/bin/simplesc")
    @patch("simples_backend.services.compiler_service.subprocess.run")
    def test_compile_timeout(self, mock_run, mock_which):
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("simplesc", 15)

        with pytest.raises(CompilerError, match="timeout: compilation exceeded 15 seconds"):
            compile_simples("programa exemplo\ninicio\nfim")

    @patch("simples_backend.services.compiler_service.shutil.which", return_value="/usr/bin/simplesc")
    @patch("simples_backend.services.compiler_service.subprocess.run")
    def test_compile_compiler_error(self, mock_run, mock_which):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "lexer:1:1: invalid token\n"

        with pytest.raises(CompilerError) as exc_info:
            compile_simples("programa exemplo\ninicio\nfim")

        assert exc_info.value.phase == "lexer"
        assert exc_info.value.message == "invalid token"
