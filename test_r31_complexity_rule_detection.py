"""
test_r31_complexity_rule_detection.py
=============================================================
Metric   : Structural Threshold Monitoring           (R31)
Category : Lint / Rule Violations
L4       : Complexity Rule Detection
L5       : Structural Threshold Monitoring
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Complexity Breach Count = Count(Functions > nesting depth 4 OR length > 50)
Threshold: 0 functions breaching nesting or length thresholds
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

from collections import Counter

import pytest

from conftest import SAMPLE_DIR, run_pylint

COMPLEXITY_SYMBOLS = {
    "too-many-branches",       # R0912
    "too-many-statements",     # R0915
    "too-many-nested-blocks",  # R1702
    "too-complex",             # R0914 (mccabe, if enabled)
    "too-many-boolean-expressions",  # R0916
}


def _complexity_violations(violations: list[dict]) -> list[dict]:
    """Filter violations to complexity-related symbols."""
    return [v for v in violations if v.get("symbol") in COMPLEXITY_SYMBOLS]


def compute_complexity_breach_count(violations: list[dict]) -> int:
    """Count distinct functions that have at least one complexity violation."""
    funcs_in_breach = {
        v.get("obj", v.get("module", "unknown"))
        for v in _complexity_violations(violations)
        if v.get("obj")
    }
    return len(funcs_in_breach)


class TestComplexityRuleDetection:
    """R31: Pylint detects functions exceeding structural thresholds."""

    def test_too_many_branches_detected(self, pylint_high_complexity):
        """R0912 too-many-branches fires on the complex sample."""
        symbols = {v.get("symbol") for v in pylint_high_complexity}
        assert "too-many-branches" in symbols, (
            f"Expected too-many-branches; found: {symbols}"
        )

    def test_too_many_nested_blocks_detected(self, pylint_high_complexity):
        """R1702 too-many-nested-blocks fires on deeply nested function."""
        symbols = {v.get("symbol") for v in pylint_high_complexity}
        assert "too-many-nested-blocks" in symbols, (
            f"Expected too-many-nested-blocks; found: {symbols}"
        )

    def test_too_many_statements_detected(self, pylint_high_complexity):
        """R0915 too-many-statements fires on long function."""
        symbols = {v.get("symbol") for v in pylint_high_complexity}
        assert "too-many-statements" in symbols, (
            f"Expected too-many-statements; found: {symbols}"
        )

    def test_clean_code_has_no_complexity_violations(self, pylint_clean):
        """Clean module has no complexity-related violations."""
        comp = _complexity_violations(pylint_clean)
        assert len(comp) == 0, (
            f"Clean code has complexity violations: "
            + str([(v.get("symbol"), v.get("obj")) for v in comp])
        )

    def test_complexity_violations_include_function_name(self, pylint_high_complexity):
        """Complexity violations carry the function name in the obj field."""
        comp = _complexity_violations(pylint_high_complexity)
        assert len(comp) >= 1
        for v in comp:
            assert v.get("obj"), f"Complexity violation missing obj field: {v}"


class TestStructuralThresholdFormula:
    """R31: Breach count formula and normalisation."""

    def test_breach_count_zero_for_clean_code(self, pylint_clean):
        """Zero functions in breach for the clean sample."""
        count = compute_complexity_breach_count(pylint_clean)
        assert count == 0

    def test_breach_count_positive_for_complex_code(self, pylint_high_complexity):
        """At least one function in breach for the complex sample."""
        count = compute_complexity_breach_count(pylint_high_complexity)
        assert count >= 1

    def test_normalised_score_for_breach_count(self, pylint_high_complexity):
        """Normalised score MAX(0, 100-(BreachCount*10)) is in [0,100]."""
        breach = compute_complexity_breach_count(pylint_high_complexity)
        score = max(0, 100 - breach * 10)
        assert 0 <= score <= 100

    @pytest.mark.parametrize("breach_count,expected_score", [
        (0, 100),
        (1, 90),
        (5, 50),
        (10, 0),
        (15, 0),
    ])
    def test_normalised_score_parametrised(self, breach_count, expected_score):
        """Parametrised normalisation: MAX(0, 100-(breach*10))."""
        score = max(0, 100 - breach_count * 10)
        assert score == expected_score

    def test_complexity_violations_counted_per_function(self):
        """Each distinct function with complexity issues counts once."""
        viols = [
            {"symbol": "too-many-branches", "obj": "func_a"},
            {"symbol": "too-many-statements", "obj": "func_a"},
            {"symbol": "too-many-nested-blocks", "obj": "func_b"},
        ]
        count = compute_complexity_breach_count(viols)
        assert count == 2
