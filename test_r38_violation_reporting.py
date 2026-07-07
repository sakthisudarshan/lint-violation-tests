"""
test_r38_violation_reporting.py
=============================================================
Metric   : Quality Audit Trail                       (R38)
Category : Lint / Rule Violations
L4       : Violation Reporting Validation
L5       : Quality Audit Trail
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Report Coverage % = (Violations with line-number + symbol / Total) * 100
Threshold: >= 95% of violations have complete audit log entry
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import pytest


MIN_REPORT_COVERAGE_PCT = 95.0

# Fields every pylint JSON violation record must contain for a complete audit trail
AUDIT_REQUIRED_FIELDS = {
    "type",      # severity level
    "line",      # exact line number
    "column",    # exact column
    "symbol",    # rule ID in human-readable form
    "message",   # description
    "path",      # file path
    "message-id", # alphanumeric rule code (e.g. C0103)
}


def is_complete_audit_entry(violation: dict) -> bool:
    """Return True if a violation contains all required audit fields with non-None values."""
    for field in AUDIT_REQUIRED_FIELDS:
        if field not in violation or violation[field] is None:
            return False
    if not isinstance(violation["line"], int) or violation["line"] <= 0:
        return False
    if not violation["symbol"]:
        return False
    return True


def compute_report_coverage(violations: list[dict]) -> float:
    """
    Report Coverage % = (Complete Audit Entries / Total Violations) * 100.
    Returns 100.0 for an empty list (no violations = no missing entries).
    """
    if not violations:
        return 100.0
    complete = sum(1 for v in violations if is_complete_audit_entry(v))
    return (complete / len(violations)) * 100


class TestViolationReportCompleteness:
    """R38: Every pylint JSON violation record has a complete audit trail."""

    def test_all_violations_have_line_numbers(self, pylint_violation_density):
        """Each violation carries a positive integer line number."""
        for v in pylint_violation_density:
            assert "line" in v, f"Missing 'line' in violation: {v}"
            assert isinstance(v["line"], int) and v["line"] > 0

    def test_all_violations_have_symbol(self, pylint_violation_density):
        """Each violation carries a non-empty rule symbol string."""
        for v in pylint_violation_density:
            assert "symbol" in v, f"Missing 'symbol' in violation: {v}"
            assert v["symbol"], f"Empty symbol in violation: {v}"

    def test_all_violations_have_message(self, pylint_violation_density):
        """Each violation carries a non-empty human-readable message."""
        for v in pylint_violation_density:
            assert "message" in v, f"Missing 'message' in violation: {v}"
            assert v["message"], f"Empty message in violation: {v}"

    def test_all_violations_have_message_id(self, pylint_violation_density):
        """Each violation carries a message-id (e.g. C0103, W0612)."""
        for v in pylint_violation_density:
            assert "message-id" in v, f"Missing 'message-id' in violation: {v}"

    def test_all_violations_have_column_info(self, pylint_violation_density):
        """Each violation carries a column number for precise location."""
        for v in pylint_violation_density:
            assert "column" in v, f"Missing 'column' in violation: {v}"

    def test_all_violations_have_type_field(self, pylint_violation_density):
        """Each violation has a type field indicating severity."""
        valid_types = {"error", "warning", "convention", "refactor", "fatal"}
        for v in pylint_violation_density:
            assert "type" in v
            assert v["type"].lower() in valid_types, (
                f"Unknown violation type '{v['type']}'"
            )

    def test_violations_reference_source_file(self, pylint_violation_density):
        """Each violation references the source file via path or module."""
        for v in pylint_violation_density:
            has_location = bool(v.get("path") or v.get("module"))
            assert has_location, f"Violation has no file reference: {v}"


class TestAuditTrailCoverageFormula:
    """R38: Report Coverage % formula and >= 95% threshold validation."""

    def test_coverage_100_for_empty_violations(self):
        """100% coverage when no violations reported (nothing missing)."""
        assert compute_report_coverage([]) == pytest.approx(100.0)

    def test_coverage_100_for_fully_complete_entries(self):
        """100% coverage when all required fields are present."""
        complete = {
            "type": "warning",
            "line": 10,
            "column": 4,
            "symbol": "unused-variable",
            "message": "Unused variable 'x'",
            "path": "file.py",
            "message-id": "W0612",
        }
        assert compute_report_coverage([complete]) == pytest.approx(100.0)

    def test_coverage_0_for_all_missing_fields(self):
        """0% coverage when all violations lack required fields."""
        incomplete = [{"type": "warning"}]  # missing line, symbol, etc.
        assert compute_report_coverage(incomplete) == pytest.approx(0.0)

    def test_coverage_50_for_half_complete(self):
        """50% coverage when half of violations have all required fields."""
        complete = {
            "type": "warning", "line": 5, "column": 0,
            "symbol": "unused-import", "message": "Unused import",
            "path": "a.py", "message-id": "W0611",
        }
        incomplete = {"type": "warning"}
        assert compute_report_coverage([complete, incomplete]) == pytest.approx(50.0)

    def test_pylint_output_meets_95_coverage_threshold(self, pylint_violation_density):
        """Real pylint JSON output meets the >= 95% audit completeness threshold."""
        coverage = compute_report_coverage(pylint_violation_density)
        assert coverage >= MIN_REPORT_COVERAGE_PCT, (
            f"Report coverage {coverage:.1f}% is below the {MIN_REPORT_COVERAGE_PCT}% threshold"
        )

    def test_audit_completeness_on_hotfile_sample(self, pylint_hotfile):
        """Hotfile sample violations also meet the >= 95% completeness threshold."""
        coverage = compute_report_coverage(pylint_hotfile)
        assert coverage >= MIN_REPORT_COVERAGE_PCT

    def test_is_complete_entry_helper_logic(self):
        """is_complete_audit_entry() correctly identifies incomplete records."""
        complete = {
            "type": "error", "line": 1, "column": 0,
            "symbol": "undefined-variable", "message": "x undefined",
            "path": "f.py", "message-id": "E0602",
        }
        assert is_complete_audit_entry(complete) is True

        missing_line = {k: v for k, v in complete.items() if k != "line"}
        assert is_complete_audit_entry(missing_line) is False

        zero_line = {**complete, "line": 0}
        assert is_complete_audit_entry(zero_line) is False

        empty_symbol = {**complete, "symbol": ""}
        assert is_complete_audit_entry(empty_symbol) is False
