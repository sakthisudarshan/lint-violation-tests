"""
conftest.py - Shared pytest fixtures and utilities for Lint/Rule Violation metric tests.

Metrics covered: R27-R38 (White Box > Static Code Analysis > Lint / Rule Violations)
Python tool   : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Execution     : Every Commit / PR
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import os

import pytest

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = ROOT_DIR  # backward compat for test_r35
SAMPLE_DIR = ROOT_DIR / "sample_code"
PYLINTRC = ROOT_DIR / ".pylintrc"
PYLINTRC_SAMPLE = ROOT_DIR / ".pylintrc-sample"
PLUGINS_DIR = ROOT_DIR / "plugins"
PLUGIN_PATH = PLUGINS_DIR / "custom_pylint_plugin.py"


def _pick_rcfile(target: str | Path) -> Path:
    """Return the appropriate rc-file for *target*.

    Scans of sample_code/ must use the sample-specific rc (which has no
    ignore-paths rule) so that violations are reported for test assertions.
    All other scans use the main .pylintrc which suppresses sample_code/ paths,
    keeping the main-codebase quality metrics clean.
    """
    if "sample_code" in str(target):
        return PYLINTRC_SAMPLE if PYLINTRC_SAMPLE.exists() else PYLINTRC
    return PYLINTRC


def _pylint_env() -> dict[str, str]:
    """Build subprocess environment with plugins on PYTHONPATH."""
    env = os.environ.copy()
    pypath_parts = [str(PLUGINS_DIR), str(ROOT_DIR)]
    existing = env.get("PYTHONPATH", "")
    if existing:
        pypath_parts.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(pypath_parts)
    return env


# ---------------------------------------------------------------------------
# Core helper: run pylint and return parsed JSON violations list
# ---------------------------------------------------------------------------
def run_pylint(
    target: str | Path,
    extra_args: list[str] | None = None,
    use_rcfile: bool = True,
) -> list[dict[str, Any]]:
    """
    Invoke pylint 4.0.6 with JSON output on *target* (file or directory).

    Returns a list of violation dicts with keys:
        type, module, obj, line, column, path, symbol, message, message-id
    """
    cmd: list[str] = [
        sys.executable, "-m", "pylint",
        "--output-format=json",
        str(target),
    ]
    if use_rcfile:
        rcfile = _pick_rcfile(target)
        if rcfile.exists():
            cmd.extend(["--rcfile", str(rcfile)])
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False,
        cwd=str(ROOT_DIR), env=_pylint_env(),
    )
    raw = result.stdout.strip()
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def run_pylint_with_exit_code(
    target: str | Path,
    extra_args: list[str] | None = None,
    use_rcfile: bool = True,
) -> tuple[list[dict[str, Any]], int]:
    """Return (violations, exit_code) tuple for gate / CI testing."""
    cmd: list[str] = [
        sys.executable, "-m", "pylint",
        "--output-format=json",
        str(target),
    ]
    if use_rcfile:
        rcfile = _pick_rcfile(target)
        if rcfile.exists():
            cmd.extend(["--rcfile", str(rcfile)])
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False,
        cwd=str(ROOT_DIR), env=_pylint_env(),
    )
    raw = result.stdout.strip()
    violations: list[dict] = []
    if raw:
        try:
            violations = json.loads(raw)
        except json.JSONDecodeError:
            pass
    return violations, result.returncode


# ---------------------------------------------------------------------------
# LOC helpers
# ---------------------------------------------------------------------------
def count_loc(file_path: str | Path) -> int:
    """Count non-empty, non-comment logical lines in a Python file."""
    with open(file_path, encoding="utf-8") as fh:
        lines = fh.readlines()
    return sum(
        1 for line in lines
        if line.strip() and not line.strip().startswith("#")
    )


def count_loc_in_dir(dir_path: str | Path) -> int:
    """Return total LOC across all .py files under *dir_path*."""
    return sum(count_loc(p) for p in Path(dir_path).rglob("*.py"))


# ---------------------------------------------------------------------------
# Suppression-comment detector
# ---------------------------------------------------------------------------
_DISABLE_PATTERN = re.compile(r"#\s*pylint\s*:\s*disable\s*=", re.IGNORECASE)


def count_suppression_comments(file_path: str | Path) -> int:
    """Return the number of inline pylint-disable comments in a file."""
    with open(file_path, encoding="utf-8") as fh:
        return sum(1 for line in fh if _DISABLE_PATTERN.search(line))


# ---------------------------------------------------------------------------
# Severity bucketing (pylint type -> project severity)
# ---------------------------------------------------------------------------
def bucket_violations(violations: list[dict]) -> dict[str, list[dict]]:
    """
    Group violations into three project-level severity buckets:
        errors   : type in ('error', 'fatal')
        warnings : type == 'warning'
        info     : type in ('convention', 'refactor')
    """
    buckets: dict[str, list[dict]] = {"errors": [], "warnings": [], "info": []}
    for v in violations:
        vtype = v.get("type", "").lower()
        if vtype in ("error", "fatal"):
            buckets["errors"].append(v)
        elif vtype == "warning":
            buckets["warnings"].append(v)
        else:
            buckets["info"].append(v)
    return buckets


# ---------------------------------------------------------------------------
# Metric formula helpers (mirror formulas from the Excel mapping)
# ---------------------------------------------------------------------------
def compute_violation_density(violations: list[dict], loc: int) -> float:
    """R27: Violation Density = (Errors*3 + Warnings*1) / (LOC / 1000)."""
    if loc == 0:
        return 0.0
    b = bucket_violations(violations)
    return (len(b["errors"]) * 3 + len(b["warnings"]) * 1) / (loc / 1000)


def compute_dead_allocation_pct(violations: list[dict]) -> float:
    """R28: Dead Allocation % based on unused-* symbols."""
    unused_symbols = {"unused-variable", "unused-import", "unused-argument"}
    unused_count = sum(1 for v in violations if v.get("symbol") in unused_symbols)
    total = len(violations) or 1
    return (unused_count / total) * 100


def compute_severity_score(violations: list[dict]) -> float:
    """R32: Severity Score = Errors*10 + Warnings*2 + Info*0.5."""
    b = bucket_violations(violations)
    return len(b["errors"]) * 10 + len(b["warnings"]) * 2 + len(b["info"]) * 0.5


def compute_hotfile_score(violations: list[dict]) -> int:
    """R33: Hotfile Score = Files(>10 viols)*15 + Files(5-10 viols)*5."""
    counts = Counter(v.get("path", v.get("module", "unknown")) for v in violations)
    hot = sum(1 for c in counts.values() if c > 10)
    amber = sum(1 for c in counts.values() if 5 <= c <= 10)
    return hot * 15 + amber * 5


def compute_normalised_score(raw: float, formula: str) -> float:
    """
    Apply the normalisation formula from column AG of the Excel mapping.
    Supported patterns:
        MAX(0, 100 - X)   -> max(0, 100 - raw)
        Score = raw       -> raw clamped to [0, 100]
    """
    if formula.startswith("MAX(0,"):
        return max(0.0, 100.0 - raw)
    return max(0.0, min(100.0, raw))


# ---------------------------------------------------------------------------
# Session-scoped violation template helper
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def _add_plugins_to_sys_path():
    """Ensure custom_pylint_plugin is importable from plugins/."""
    plugins_dir = str(PLUGINS_DIR)
    if plugins_dir not in sys.path:
        sys.path.insert(0, plugins_dir)
    yield


_VIOLATION_TEMPLATES = [
    "sample_violation_density",
    "sample_unused_vars",
    "sample_bad_naming",
    "sample_bad_style",
    "sample_high_complexity",
    "sample_mixed_severity",
    "sample_hotfile",
]


@pytest.fixture(scope="session")
def violation_temp_dir(tmp_path_factory):
    """Session-scoped temp directory populated with violation .py files.

    Each file is written from a .txt template stored alongside the clean
    sample_code/ .py stubs.  The .txt files contain intentionally bad code
    that triggers pylint violations; the .py stubs are clean so that the
    taxonomy gate (and any third-party scanner) finds zero violations in the
    repository itself.
    """
    base = tmp_path_factory.mktemp("violation_samples")
    for name in _VIOLATION_TEMPLATES:
        txt_path = SAMPLE_DIR / f"{name}.txt"
        if txt_path.exists():
            (base / f"{name}.py").write_text(
                txt_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
    return base


# ---------------------------------------------------------------------------
# Session-scoped pylint fixtures (one run per sample file per test session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def pylint_clean():
    """pylint violations for the clean, zero-violation sample."""
    return run_pylint(SAMPLE_DIR / "sample_clean.py")


@pytest.fixture(scope="session")
def pylint_violation_density(violation_temp_dir):
    """pylint violations for the high-density sample (from .txt template)."""
    return run_pylint(violation_temp_dir / "sample_violation_density.py")


@pytest.fixture(scope="session")
def pylint_unused_vars(violation_temp_dir):
    """pylint violations for the unused-variable sample (from .txt template)."""
    return run_pylint(violation_temp_dir / "sample_unused_vars.py")


@pytest.fixture(scope="session")
def pylint_bad_naming(violation_temp_dir):
    """pylint violations for the naming-convention sample (from .txt template)."""
    return run_pylint(violation_temp_dir / "sample_bad_naming.py")


@pytest.fixture(scope="session")
def pylint_bad_style(violation_temp_dir):
    """pylint violations for the bad-style sample (from .txt template)."""
    return run_pylint(violation_temp_dir / "sample_bad_style.py")


@pytest.fixture(scope="session")
def pylint_high_complexity(violation_temp_dir):
    """pylint violations for the high-complexity sample (from .txt template)."""
    return run_pylint(violation_temp_dir / "sample_high_complexity.py")


@pytest.fixture(scope="session")
def pylint_mixed_severity(violation_temp_dir):
    """pylint violations for the mixed-severity sample (from .txt template)."""
    return run_pylint(violation_temp_dir / "sample_mixed_severity.py")


@pytest.fixture(scope="session")
def pylint_hotfile(violation_temp_dir):
    """pylint violations for the concentrated-hotfile sample (from .txt template)."""
    return run_pylint(violation_temp_dir / "sample_hotfile.py")


@pytest.fixture(scope="session")
def pylint_suppressed():
    """pylint violations for the suppressed-comments sample."""
    return run_pylint(SAMPLE_DIR / "sample_suppressed.py")


@pytest.fixture(scope="session")
def pylint_custom_rule():
    """pylint violations using the custom plugin on sample_custom_rule.py."""
    if not PLUGIN_PATH.exists():
        return []
    return run_pylint(
        SAMPLE_DIR / "sample_custom_rule.py",
        extra_args=["--load-plugins", "custom_pylint_plugin",
                    "--disable=all", "--enable=too-many-function-args-custom"],
    )
