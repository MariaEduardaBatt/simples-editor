from __future__ import annotations

import os
import shutil
import subprocess
import tempfile


class CompilerError(Exception):
    def __init__(self, message: str):
        self.message = message


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
            raise CompilerError(result.stderr.strip())

        with open(output_path, "r", encoding="utf-8") as f:
            return f.read()
