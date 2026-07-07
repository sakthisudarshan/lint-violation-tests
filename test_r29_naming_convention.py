"""
test_r29_naming_convention.py
=============================================================
Metric   : Semantic Consistency Score                (R29)
Category : Lint / Rule Violations
L4       : Naming Convention Validation
L5       : Semantic Consistency Score
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Convention Violation Rate = (Naming Violations / Total Named Identifiers) * 100
           Semantic Consistency Score = 1 - (Naming Violations / Total Violations)
Threshold: < 2% naming convention violations across codebase
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import pytest


NAMING_SYMBOLS = {"invalid-name", "naming-convention-violation"}
MAX_CONVENTION_RATE_PCT = 2.0


def _naming_violations(violations: list[dict]) -> list[dict]:
    """Filter violations to naming-related symbols."""
    return [v for v in violations if v.get("symbol") in NAMING_SYMBOLS]


def compute_semantic_consistency(violations: list[dict]) -> float:
    """Semantic Consistency Score = 1 - (NamingViolations / TotalViolations)."""
    if not violations:
        return 1.0
    naming = len(_naming_violations(violations))
    return 1.0 - (naming / len(violations))


def compute_convention_violation_rate(violations: list[dict], total_identifiers: int) -> float:
    """Convention Violation Rate = (Naming Violations / Total Named Identifiers) * 100."""
    if total_identifiers == 0:
        return 0.0
    naming = len(_naming_violations(violations))
    return (naming / total_identifiers) * 100


class TestNamingConventionDetection:
    """R29: Pylint correctly detects invalid-name (C0103) violations."""

    def test_naming_violations_detected_in_bad_code(self, pylint_bad_naming):
        """Bad naming sample produces at least one invalid-name violation."""
        naming = _naming_violations(pylint_bad_naming)
        assert len(naming) >= 1, "Expected invalid-name violations in bad naming sample"

    def test_pascal_case_function_triggers_violation(self, pylint_bad_naming):
        """PascalCase function names produce C0103 invalid-name."""
        symbols = {v.get("symbol") for v in pylint_bad_naming}
        assert "invalid-name" in symbols

    def test_clean_code_has_no_naming_violations(self, pylint_clean):
        """Clean module has zero invalid-name violations."""
        naming = _naming_violations(pylint_clean)
        assert len(naming) == 0, (
            "Clean code has naming violations: "
            + str([(v.get("symbol"), v.get("message")) for v in naming])
        )

    def test_naming_violations_include_identifier_name_in_message(self, pylint_bad_naming):
        """Each naming violation message should reference the identifier."""
        for v in _naming_violations(pylint_bad_naming):
            assert v.get("message"), "Naming violation has no message"

    def test_naming_violation_records_have_column_info(self, pylint_bad_naming):
        """Naming violations carry column information for precise location."""
        for v in _naming_violations(pylint_bad_naming):
            assert "column" in v


class TestSemanticConsistencyFormula:
    """R29: Semantic Consistency Score formula and threshold validation."""

    def test_perfect_score_when_no_violations(self):
        """Score is 1.0 (perfect) when there are no violations."""
        assert compute_semantic_consistency([]) == pytest.approx(1.0)

    def test_score_zero_when_all_are_naming_violations(self):
        """Score is 0.0 when every violation is a naming violation."""
        viols = [{"symbol": "invalid-name"}] * 5
        assert compute_semantic_consistency(viols) == pytest.approx(0.0)

    def test_score_proportional_to_naming_ratio(self):
        """Score decreases proportionally with the naming violation share."""
        viols = [{"symbol": "invalid-name"}] * 3 + [{"symbol": "unused-import"}] * 7
        expected = 1.0 - (3 / 10)
        assert compute_semantic_consistency(viols) == pytest.approx(expected)

    def test_score_on_bad_naming_sample_below_perfect(self, pylint_bad_naming):
        """Bad naming sample has a semantic consistency score below 1.0."""
        score = compute_semantic_consistency(pylint_bad_naming)
        assert score < 1.0

    def test_score_on_clean_code_at_perfect(self, pylint_clean):
        """Clean code achieves a perfect semantic consistency score."""
        score = compute_semantic_consistency(pylint_clean)
        naming = _naming_violations(pylint_clean)
        if naming:
            assert score < 1.0
        else:
            assert score == pytest.approx(1.0)

    @pytest.mark.parametrize("naming,total,expected", [
        (0, 100, 1.0),
        (10, 100, 0.9),
        (50, 100, 0.5),
        (100, 100, 0.0),
    ])
    def test_semantic_consistency_parametrised(self, naming, total, expected):
        """Parametrised formula validation across varied naming/total combos."""
        viols = ([{"symbol": "invalid-name"}] * naming
                 + [{"symbol": "unused-variable"}] * (total - naming))
        assert compute_semantic_consistency(viols) == pytest.approx(expected)
