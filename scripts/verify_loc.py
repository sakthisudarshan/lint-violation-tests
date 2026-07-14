"""Verify src/ meets the 50k LOC target and passes pylint."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
TARGET_LOC = 50_000


def count_loc(directory: Path) -> int:
    """Count non-empty, non-comment logical lines."""
    total = 0
    for py_file in directory.rglob("*.py"):
        for line in py_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                total += 1
    return total


def main() -> None:
    loc = count_loc(SRC_DIR)
    print(f"Main codebase LOC: {loc}")
    if loc < TARGET_LOC:
        print(f"FAIL: below target of {TARGET_LOC}")
        sys.exit(1)

    rcfile = ROOT_DIR / ".pylintrc"
    env = os.environ.copy()
    src_path = str(ROOT_DIR / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_path + (os.pathsep + existing if existing else "")

    result = subprocess.run(
        [
            sys.executable, "-m", "pylint",
            str(SRC_DIR), f"--rcfile={rcfile}", "--errors-only",
        ],
        cwd=str(ROOT_DIR),
        env=env,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print("FAIL: pylint reported issues on src/")
        sys.exit(1)

    print(f"PASS: {loc} LOC and pylint clean")


if __name__ == "__main__":
    main()
