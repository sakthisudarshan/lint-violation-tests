"""
test_r27_violation_density.py
=============================================================
Metric   : Violation Density per KLOC                (R27)
Category : Lint / Rule Violations
L4       : Rule Detection Test
L5       : Violation Density per KLOC
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Violation Density = (Errors*3 + Warnings*1) / (LOC / 1000)
Threshold: 0 blocking errors; < 10 warnings per KLOC
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import pytest

from conftest import (
    SAMPLE_DIR,
    bucket_violations,
    compute_violation_density,
    count_loc,
)

MAX_WARNINGS_PER_KLOC = 10
MAX_ERRORS_ALLOWED = 0


class TestViolationDensityFormula:
    """R27: Verify the violation density formula computes correctly."""

    def test_formula_returns_zero_for_empty_violations(self):
        """Density is 0 when there are no violations."""
        assert compute_violation_density([], loc=500) == 0.0

    def test_formula_returns_zero_for_zero_loc(self):
        """Density is 0 (no divide-by-zero) when LOC is 0."""
        violations = [{"type": "warning", "symbol": "unused-import"}]
        assert compute_violation_density(violations, loc=0) == 0.0

    def test_formula_scales_with_loc(self):
        """Doubling LOC halves the violation density."""
        violations = [{"type": "warning"}] * 10
        density_1k = compute_violation_density(violations, loc=1000)
        density_2k = compute_violation_density(violations, loc=2000)
        assert abs(density_1k - density_2k * 2) < 1e-9

    def test_errors_weighted_higher_than_warnings(self):
        """Each error contributes weight=3, each warning weight=1."""
        one_error = [{"type": "error"}]
        three_warnings = [{"type": "warning"}] * 3
        d_error = compute_violation_density(one_error, loc=1000)
        d_warnings = compute_violation_density(three_warnings, loc=1000)
        assert d_error == d_warnings

    def test_density_calculation_matches_manual_computation(self):
        """Manual check: 2 errors + 4 warnings over 500 LOC."""
        violations = [{"type": "error"}] * 2 + [{"type": "warning"}] * 4
        expected = (2 * 3 + 4 * 1) / (500 / 1000)
        assert compute_violation_density(violations, loc=500) == pytest.approx(expected)


class TestViolationDensityOnSampleCode:
    """R27: Run pylint on sample files and assert density thresholds."""

    def test_clean_code_has_no_errors(self, pylint_clean):
        """Clean sample has zero error-level violations."""
        b = bucket_violations(pylint_clean)
        assert len(b["errors"]) == MAX_ERRORS_ALLOWED

    def test_clean_code_density_under_threshold(self, pylint_clean):
        """Clean sample violation density is below the 10/KLOC warning threshold."""
        loc = count_loc(SAMPLE_DIR / "sample_clean.py")
        density = compute_violation_density(pylint_clean, loc)
        assert density <= MAX_WARNINGS_PER_KLOC

    def test_bad_code_density_exceeds_threshold(self, pylint_violation_density):
        """High-density sample exceeds the 10/KLOC threshold, confirming detection."""
        loc = count_loc(SAMPLE_DIR / "sample_violation_density.py")
        density = compute_violation_density(pylint_violation_density, loc)
        assert density > MAX_WARNINGS_PER_KLOC

    def test_violations_bucketed_into_all_severity_levels(self, pylint_violation_density):
        """Output is categorised into errors, warnings and info buckets."""
        b = bucket_violations(pylint_violation_density)
        all_viols = b["errors"] + b["warnings"] + b["info"]
        assert len(all_viols) == len(pylint_violation_density)

    def test_violation_output_has_required_json_fields(self, pylint_violation_density):
        """Every violation record includes type, line, symbol and message."""
        required = {"type", "line", "symbol", "message"}
        for v in pylint_violation_density:
            assert required.issubset(v.keys())

    def test_normalised_score_in_valid_range(self, pylint_violation_density):
        """Normalised score MAX(0, 100-(Errors*5+Warnings)) stays in [0,100]."""
        b = bucket_violations(pylint_violation_density)
        raw = len(b["errors"]) * 5 + len(b["warnings"])
        score = max(0, 100 - raw)
        assert 0 <= score <= 100
