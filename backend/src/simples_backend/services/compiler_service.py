from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile

ERROR_FORMAT_RE = re.compile(
    r"^(lexer|parser|semantic|codegen):(\d+):(\d+):\s*(.*)$"
)


class CompilerError(Exception):
    def __init__(
        self,
        message: str,
        phase: str | None = None,
        line: int = 0,
        column: int = 0,
    ):
        self.message = message
        self.phase = phase
        self.line = line
        self.column = column


def _parse_stderr(stderr: str) -> CompilerError:
    stripped = stderr.strip()
    match = ERROR_FORMAT_RE.match(stripped)
    if match:
        return CompilerError(
            message=match.group(4),
            phase=match.group(1),
            line=int(match.group(2)),
            column=int(match.group(3)),
        )
    return CompilerError(message=stripped)


def compile_simples(code: str) -> str:
    """Compile SIMPLES source code to NASM assembly.

    Raises CompilerError on failure.
    """

    simplesc_path = shutil.which("simplesc")
    if not simplesc_path:
        raise CompilerError("compiler not found")

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.simples")
        output_path = os.path.join(tmpdir, "output.asm")

        with open(input_path, "w", encoding="utf-8") as f:
            f.write(code)

        result = subprocess.run(
            [simplesc_path, input_path, "-o", output_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise _parse_stderr(result.stderr)

        with open(output_path, "r", encoding="utf-8") as f:
            return f.read()
