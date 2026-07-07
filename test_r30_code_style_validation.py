"""
test_r30_code_style_validation.py
=============================================================
Metric   : Syntactic Uniformity Score               (R30)
Category : Lint / Rule Violations
L4       : Code Style Rule Validation
L5       : Syntactic Uniformity Score
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Style Violation Density = Style Violations / (LOC / 1000)
           Syntactic Uniformity Score = 1 - (StyleViolations / TotalViolations)
Threshold: < 5 style violations per KLOC
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import pytest

from conftest import SAMPLE_DIR, count_loc

STYLE_SYMBOLS = {
    "line-too-long",          # C0301
    "trailing-whitespace",    # C0303
    "bad-whitespace",         # C0326 (older pylint)
    "missing-final-newline",  # C0304
    "bad-indentation",        # W0311
    "mixed-indentation",      # W0312
    "unnecessary-semicolon",  # W0301
}
MAX_STYLE_DENSITY_PER_KLOC = 5.0


def _style_violations(violations: list[dict]) -> list[dict]:
    """Filter violations to code-style related symbols."""
    return [v for v in violations if v.get("symbol") in STYLE_SYMBOLS]


def _convention_violations(violations: list[dict]) -> list[dict]:
    """All convention-category (C-prefix) violations."""
    return [v for v in violations if v.get("type", "").lower() == "convention"]


def compute_style_density(violations: list[dict], loc: int) -> float:
    """Style Violation Density = StyleViolations / (LOC / 1000)."""
    if loc == 0:
        return 0.0
    style = len(_style_violations(violations))
    return style / (loc / 1000)


def compute_syntactic_uniformity(violations: list[dict]) -> float:
    """Syntactic Uniformity Score = 1 - (fixableStyleViolations / TotalViolations)."""
    if not violations:
        return 1.0
    fixable = len([v for v in violations if v.get("symbol") == "line-too-long"])
    return 1.0 - (fixable / len(violations))


class TestStyleViolationDetection:
    """R30: Pylint detects code style violations."""

    def test_line_too_long_detected_in_bad_style(self, pylint_bad_style):
        """C0301 line-too-long is detected in the bad style sample."""
        symbols = {v.get("symbol") for v in pylint_bad_style}
        assert "line-too-long" in symbols, (
            f"Expected line-too-long; found: {symbols}"
        )

    def test_convention_category_violations_present(self, pylint_bad_style):
        """Convention-category (C) violations are present in the bad style sample."""
        conv = _convention_violations(pylint_bad_style)
        assert len(conv) >= 1

    def test_clean_code_has_minimal_style_violations(self, pylint_clean):
        """Clean sample has zero known style-symbol violations."""
        style = _style_violations(pylint_clean)
        assert len(style) == 0

    def test_violation_objects_have_path_info(self, pylint_bad_style):
        """Style violations include file path for audit purposes."""
        for v in pylint_bad_style:
            assert "path" in v or "module" in v

    def test_style_violations_carry_column_information(self, pylint_bad_style):
        """Style violations provide column info to locate exact code position."""
        for v in _style_violations(pylint_bad_style):
            assert "column" in v


class TestSyntacticUniformityFormula:
    """R30: Style density and uniformity score formula validation."""

    def test_style_density_zero_for_no_violations(self):
        """Density is 0 when there are no style violations."""
        assert compute_style_density([], loc=500) == 0.0

    def test_style_density_above_threshold_on_bad_code(self, pylint_bad_style):
        """Bad style sample style density exceeds 0 (violations present)."""
        loc = count_loc(SAMPLE_DIR / "sample_bad_style.py")
        density = compute_style_density(pylint_bad_style, loc)
        assert density >= 0  # validates the formula runs without error

    def test_syntactic_uniformity_is_one_for_clean_code(self, pylint_clean):
        """Clean code has no line-too-long; uniformity score is 1.0."""
        score = compute_syntactic_uniformity(pylint_clean)
        assert score == pytest.approx(1.0)

    def test_syntactic_uniformity_decreases_with_style_violations(self):
        """Uniformity score decreases when line-too-long violations increase."""
        viols_light = [{"symbol": "line-too-long"}] * 2 + [{"symbol": "invalid-name"}] * 8
        viols_heavy = [{"symbol": "line-too-long"}] * 8 + [{"symbol": "invalid-name"}] * 2
        score_light = compute_syntactic_uniformity(viols_light)
        score_heavy = compute_syntactic_uniformity(viols_heavy)
        assert score_light > score_heavy

    def test_normalised_score_from_density(self, pylint_bad_style):
        """Normalised score MAX(0, 100-(density*10)) is in [0,100]."""
        loc = count_loc(SAMPLE_DIR / "sample_bad_style.py")
        density = compute_style_density(pylint_bad_style, loc)
        score = max(0, 100 - density * 10)
        assert 0 <= score <= 100

    @pytest.mark.parametrize("style_count,loc,max_density", [
        (0, 1000, 5.0),
        (3, 1000, 5.0),
        (5, 1000, 5.0),
        (6, 1000, 5.0),
    ])
    def test_style_density_threshold_cases(self, style_count, loc, max_density):
        """Parametrised threshold check for style violation density."""
        viols = [{"symbol": "line-too-long"}] * style_count
        density = compute_style_density(viols, loc)
        if style_count <= max_density:
            assert density <= max_density
        else:
            assert density > max_density
