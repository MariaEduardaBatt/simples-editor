from __future__ import annotations

import os
import shutil
import subprocess


class ExecutionError(Exception):
    def __init__(self, message: str, phase: str):
        self.message = message
        self.phase = phase


def assemble_nasm(asm: str, tmpdir: str, timeout: int = 15) -> str:
    """Assemble NASM source to ELF32 object file. Returns path to .o file."""
    asm_path = os.path.join(tmpdir, "programa.asm")
    obj_path = os.path.join(tmpdir, "programa.o")

    with open(asm_path, "w", encoding="utf-8") as f:
        f.write(asm)

    result = subprocess.run(
        ["nasm", "-f", "elf32", asm_path, "-o", obj_path],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise ExecutionError(
            result.stderr.strip() or "unknown nasm error", "nasm"
        )

    return obj_path


def link_object(obj_path: str, tmpdir: str, timeout: int = 15) -> str:
    """Link ELF32 object into executable. Returns path to binary."""
    bin_path = os.path.join(tmpdir, "programa")

    ld_path = shutil.which("i686-linux-gnu-ld") or "i686-linux-gnu-ld"

    result = subprocess.run(
        [ld_path, "-m", "elf_i386", obj_path, "-o", bin_path],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise ExecutionError(
            result.stderr.strip() or "unknown ld error", "ld"
        )

    return bin_path
