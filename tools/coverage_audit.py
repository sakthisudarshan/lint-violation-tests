"""Coverage audit for R27-R38 metrics."""
import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT_DIR / "tests"
REPORTS_DIR = ROOT_DIR / "reports"
SAMPLE_DIR = ROOT_DIR / "sample_code"

sys.stdout.reconfigure(encoding="utf-8")

# ── 1. Test files ──────────────────────────────────────────────────────────
test_map = {
    "R27": "test_r27_violation_density.py",
    "R28": "test_r28_unused_variable_detection.py",
    "R29": "test_r29_naming_convention.py",
    "R30": "test_r30_code_style_validation.py",
    "R31": "test_r31_complexity_rule_detection.py",
    "R32": "test_r32_rule_severity_classification.py",
    "R33": "test_r33_multiple_violations.py",
    "R34": "test_r34_false_positive_prevention.py",
    "R35": "test_r35_custom_rule_validation.py",
    "R36": "test_r36_configuration_file.py",
    "R37": "test_r37_cicd_integration.py",
    "R38": "test_r38_violation_reporting.py",
}
print("=" * 70)
print("  COVERAGE AUDIT  -  R27 to R38  (Lint / Rule Violations)")
print("=" * 70)

print("\n[1] TEST FILES (one per metric)")
all_tests_ok = True
for rid, fname in test_map.items():
    exists = (TESTS_DIR / fname).exists()
    if not exists:
        all_tests_ok = False
    lines = (
        len((TESTS_DIR / fname).read_text(encoding="utf-8-sig", errors="ignore").splitlines())
        if exists else 0
    )
    tag = "OK" if exists else "MISSING"
    print(f"  {tag:8} {rid}  {fname}  ({lines} lines)")

# ── 2. Sample code files ───────────────────────────────────────────────────
print("\n[2] SAMPLE CODE FILES (in sample_code/)")
sample_map = {
    "R27": "sample_violation_density.py",
    "R28": "sample_unused_vars.py",
    "R29": "sample_bad_naming.py",
    "R30": "sample_bad_style.py",
    "R31": "sample_high_complexity.py",
    "R32": "sample_mixed_severity.py",
    "R33": "sample_hotfile.py",
    "R34": "sample_suppressed.py",
    "R35": "sample_custom_rule.py",
    "R36": "(.pylintrc config)",
    "R37": "(all sample files)",
    "R38": "(all sample files)",
    "CLEAN": "sample_clean.py",
}
for rid, fname in sample_map.items():
    if fname.startswith("("):
        print(f"  OK       {rid}  {fname}")
    else:
        path = SAMPLE_DIR / fname
        exists = path.exists()
        lines = len(path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()) if exists else 0
        tag = "OK" if exists else "MISSING"
        print(f"  {tag:8} {rid}  {fname}  ({lines} lines)")

# ── 3. Infrastructure files ────────────────────────────────────────────────
print("\n[3] INFRASTRUCTURE & CONFIG FILES")
infra = {
    ".pylintrc":                        "Pylint configuration (max-args, max-branches, etc.)",
    "requirements.txt":                 "pylint==4.0.6, pytest, pytest-json-report",
    "tests/conftest.py":                "Pytest fixtures / shared setup",
    "pytest.ini":                       "Pytest settings",
    "plugins/custom_pylint_plugin.py":  "W9001 custom rule checker (R35)",
    "tools/generate_metrics_excel.py":  "Script: runs pylint + computes + exports Excel",
}
for fname, desc in infra.items():
    exists = (ROOT_DIR / fname).exists()
    tag = "OK" if exists else "MISSING"
    print(f"  {tag:8} {fname:35}  {desc}")

# ── 4. Output files ────────────────────────────────────────────────────────
print("\n[4] OUTPUT / REPORT FILES")
outputs = {
    "reports/pylint_output_raw.json":                   "Raw pylint JSON (main codebase scan)",
    "reports/Pylint_Lint_Violation_Metrics_R27_R38.xlsx": "Excel report with Raw + Derived + Normalised values",
}
for fname, desc in outputs.items():
    path = ROOT_DIR / fname
    if path.exists():
        size = path.stat().st_size
        print(f"  OK       {fname}  ({size:,} bytes)  -  {desc}")
    else:
        print(f"  MISSING  {fname}  -  {desc}")

# ── 5. Pylint violation coverage per metric ────────────────────────────────
print("\n[5] PYLINT VIOLATION DATA COVERAGE PER METRIC")
json_path = REPORTS_DIR / "pylint_output_raw.json"
if json_path.exists():
    data = json.loads(json_path.read_text(encoding="utf-8"))
else:
    data = []

symbols = {}
for v in data:
    symbols[v["symbol"]] = symbols.get(v["symbol"], 0) + 1

types_present = {v["type"] for v in data}
files_with_3plus = sum(
    1 for p in set(v["path"] for v in data)
    if sum(1 for v in data if v["path"] == p) >= 3
)
suppression_count = sum(
    1 for p in SAMPLE_DIR.rglob("*.py")
    for line in p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
    if "pylint" in line.lower() and "disable" in line.lower()
)
fully_filled = sum(
    1 for v in data
    if all(v.get(f) not in (None, "") for f in
           ["type", "module", "line", "path", "symbol", "message", "message-id"])
)

metric_coverage = [
    ("R27", "Violation Density per KLOC",       "Total violations",                      len(data),          len(data) > 0),
    ("R28", "Resource Waste Identification",     "unused-variable/import/argument",
        sum(symbols.get(s, 0) for s in ["unused-variable", "unused-import", "unused-argument"]),
        sum(symbols.get(s, 0) for s in ["unused-variable", "unused-import", "unused-argument"]) > 0),
    ("R29", "Semantic Consistency Score",        "invalid-name (C0103)",                  symbols.get("invalid-name", 0), symbols.get("invalid-name", 0) > 0),
    ("R30", "Syntactic Uniformity Score",        "line-too-long / style violations",
        sum(symbols.get(s, 0) for s in ["line-too-long", "trailing-whitespace", "bad-indentation", "multiple-statements"]),
        sum(symbols.get(s, 0) for s in ["line-too-long", "trailing-whitespace", "bad-indentation", "multiple-statements"]) > 0),
    ("R31", "Structural Threshold Monitoring",   "complexity violations",
        sum(symbols.get(s, 0) for s in ["too-many-branches", "too-many-statements", "too-many-nested-blocks", "too-many-arguments", "too-many-positional-arguments"]),
        sum(symbols.get(s, 0) for s in ["too-many-branches", "too-many-statements", "too-many-nested-blocks", "too-many-arguments", "too-many-positional-arguments"]) > 0),
    ("R32", "Impact Prioritization",             "severity types (E/W/C/R)",              len(types_present), len(types_present) == 4),
    ("R33", "Aggregated Risk Assessment",        "files with 3+ violations",              files_with_3plus,   files_with_3plus > 0),
    ("R34", "Accuracy Tuning",                   "pylint:disable suppressions",           suppression_count,  suppression_count > 0),
    ("R35", "Project-Specific Enforcement",      "W9001 custom rule violations",          symbols.get("too-many-function-args-custom", 0), symbols.get("too-many-function-args-custom", 0) > 0),
    ("R36", "Environment Standardization",       ".pylintrc config file",                 1 if (ROOT_DIR / ".pylintrc").exists() else 0, (ROOT_DIR / ".pylintrc").exists()),
    ("R37", "Automated Gatekeeping",             "total violations for gate",             len(data),          len(data) > 0),
    ("R38", "Quality Audit Trail",               "violations with all fields filled",     fully_filled,       fully_filled > 0),
]

all_covered = True
for rid, metric, label, value, ok in metric_coverage:
    if not ok:
        all_covered = False
    status = "COVERED" if ok else "NOT COVERED"
    print(f"  {status:12}  {rid}  {metric:36}  {label}: {value}")

# ── 6. Git / GitHub status ────────────────────────────────────────────────
print("\n[6] GIT REPOSITORY STATUS")
branch = subprocess.run(
    ["git", "branch", "--show-current"], capture_output=True, text=True, cwd=ROOT_DIR,
).stdout.strip()
remote = subprocess.run(
    ["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=ROOT_DIR,
).stdout.strip()
file_count = subprocess.run(
    ["git", "ls-files"], capture_output=True, text=True, cwd=ROOT_DIR,
).stdout.strip().count("\n") + 1
print(f"  Branch       : {branch}")
print(f"  Remote URL   : {remote}")
print(f"  Files in repo: {file_count}")

# ── Final verdict ─────────────────────────────────────────────────────────
print()
print("=" * 70)
if all_covered and all_tests_ok:
    print("  VERDICT: ALL R27-R38 METRICS ARE FULLY COVERED")
else:
    print("  VERDICT: SOME METRICS ARE MISSING COVERAGE - SEE ABOVE")
print("=" * 70)
