"""
test_r28_unused_variable_detection.py
=============================================================
Metric   : Resource Waste Identification             (R28)
Category : Lint / Rule Violations
L4       : Unused Variable Detection
L5       : Resource Waste Identification
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Dead Allocation % = (Unused Variables / Total Declared) * 100
Threshold: < 1% unused variable declarations per module
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import pytest

from conftest import (
    compute_dead_allocation_pct,
)

UNUSED_SYMBOLS = {"unused-variable", "unused-import", "unused-argument"}
MAX_DEAD_ALLOCATION_PCT = 1.0


class TestUnusedVariableDetection:
    """R28: Pylint correctly identifies unused variable violations."""

    def test_unused_variable_symbols_present_in_bad_code(self, pylint_unused_vars):
        """Bad sample produces at least one unused-* violation."""
        detected = [v for v in pylint_unused_vars if v.get("symbol") in UNUSED_SYMBOLS]
        assert len(detected) >= 1, "Expected unused-variable/import/argument violations"

    def test_unused_import_detected(self, pylint_unused_vars):
        """W0611 unused-import is detected in the sample module."""
        symbols = {v.get("symbol") for v in pylint_unused_vars}
        assert "unused-import" in symbols

    def test_unused_variable_detected(self, pylint_unused_vars):
        """W0612 unused-variable is detected in the sample module."""
        symbols = {v.get("symbol") for v in pylint_unused_vars}
        assert "unused-variable" in symbols

    def test_clean_code_has_no_unused_violations(self, pylint_clean):
        """Clean module has zero unused-variable/import/argument violations."""
        detected = [v for v in pylint_clean if v.get("symbol") in UNUSED_SYMBOLS]
        assert len(detected) == 0, (
            "Clean code unexpectedly has unused violations: "
            + str([v.get("symbol") for v in detected])
        )

    def test_violation_records_include_line_numbers(self, pylint_unused_vars):
        """Each unused-* violation must include a line number for traceability."""
        for v in pylint_unused_vars:
            if v.get("symbol") in UNUSED_SYMBOLS:
                assert "line" in v and isinstance(v["line"], int)
                assert v["line"] > 0


class TestResourceWasteFormula:
    """R28: Dead Allocation % formula computation and thresholds."""

    def test_dead_allocation_zero_for_no_violations(self):
        """0 violations produces 0% dead allocation."""
        assert compute_dead_allocation_pct([]) == 0.0

    def test_dead_allocation_one_hundred_when_all_are_unused(self):
        """100% when every violation is an unused-variable."""
        viols = [{"symbol": "unused-variable"}] * 5
        assert compute_dead_allocation_pct(viols) == pytest.approx(100.0)

    def test_dead_allocation_proportional_to_unused_count(self):
        """Rate is proportional: 2 unused out of 10 = 20%."""
        viols = [{"symbol": "unused-variable"}] * 2
        viols += [{"symbol": "invalid-name"}] * 8
        pct = compute_dead_allocation_pct(viols)
        assert pct == pytest.approx(20.0)

    def test_dead_allocation_pct_on_bad_sample(self, pylint_unused_vars):
        """The bad sample exceeds 0% dead allocation (violations found)."""
        pct = compute_dead_allocation_pct(pylint_unused_vars)
        assert pct > 0.0, "Expected non-zero dead allocation in unused_vars sample"

    def test_normalised_score_for_bad_code_is_below_100(self, pylint_unused_vars):
        """Normalised score MAX(0, 100-(Dead%*50)) decreases with waste."""
        pct = compute_dead_allocation_pct(pylint_unused_vars)
        score = max(0, 100 - pct * 50)
        assert score < 100, "Score should be penalised for unused variable violations"

    @pytest.mark.parametrize("unused,total,expected_pct", [
        (0, 10, 0.0),
        (1, 100, 1.0),
        (5, 50, 10.0),
        (10, 10, 100.0),
    ])
    def test_dead_allocation_formula_parametrised(self, unused, total, expected_pct):
        """Parametrised formula check across multiple input combinations."""
        viols = [{"symbol": "unused-variable"}] * unused
        viols += [{"symbol": "invalid-name"}] * (total - unused)
        assert compute_dead_allocation_pct(viols) == pytest.approx(expected_pct)
