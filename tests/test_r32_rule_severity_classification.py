"""
test_r32_rule_severity_classification.py
=============================================================
Metric   : Impact Prioritization                     (R32)
Category : Lint / Rule Violations
L4       : Rule Severity Classification
L5       : Impact Prioritization
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Severity Score = Errors*10 + Warnings*2 + Info*0.5
Threshold: 0 Error-level violations; < 10 Warning-level per KLOC
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import pytest

from conftest import (
    SAMPLE_DIR,
    bucket_violations,
    compute_severity_score,
    count_loc,
)

MAX_ERRORS = 0
MAX_WARNINGS_PER_KLOC = 10


class TestSeverityClassification:
    """R32: Violations are correctly classified into E/W/C/R buckets."""

    def test_error_type_maps_to_errors_bucket(self):
        """pylint type 'error' maps to the errors severity bucket."""
        viols = [{"type": "error", "symbol": "undefined-variable"}]
        b = bucket_violations(viols)
        assert len(b["errors"]) == 1
        assert len(b["warnings"]) == 0
        assert len(b["info"]) == 0

    def test_fatal_type_maps_to_errors_bucket(self):
        """pylint type 'fatal' also maps to the errors severity bucket."""
        viols = [{"type": "fatal", "symbol": "syntax-error"}]
        b = bucket_violations(viols)
        assert len(b["errors"]) == 1

    def test_warning_type_maps_to_warnings_bucket(self):
        """pylint type 'warning' maps to the warnings bucket."""
        viols = [{"type": "warning", "symbol": "unused-variable"}]
        b = bucket_violations(viols)
        assert len(b["warnings"]) == 1
        assert len(b["errors"]) == 0

    def test_convention_and_refactor_map_to_info_bucket(self):
        """pylint 'convention' and 'refactor' types map to the info bucket."""
        viols = [
            {"type": "convention", "symbol": "invalid-name"},
            {"type": "refactor", "symbol": "too-many-branches"},
        ]
        b = bucket_violations(viols)
        assert len(b["info"]) == 2
        assert len(b["errors"]) == 0
        assert len(b["warnings"]) == 0

    def test_mixed_code_contains_multiple_severity_levels(self, pylint_mixed_severity):
        """Mixed severity sample contains violations from different buckets."""
        b = bucket_violations(pylint_mixed_severity)
        present_buckets = sum(1 for lst in b.values() if len(lst) > 0)
        assert present_buckets >= 2, "Expected violations in at least 2 severity buckets"

    def test_error_violations_present_in_mixed_sample(self, pylint_mixed_severity):
        """Mixed sample includes at least one error-level violation (undefined-variable)."""
        b = bucket_violations(pylint_mixed_severity)
        assert len(b["errors"]) >= 1


class TestImpactPrioritizationFormula:
    """R32: Severity Score formula and threshold enforcement."""

    def test_severity_score_zero_for_no_violations(self):
        """Score is 0.0 when violations list is empty."""
        assert compute_severity_score([]) == pytest.approx(0.0)

    def test_severity_score_only_errors(self):
        """Score = Errors*10 when only error-type violations exist."""
        viols = [{"type": "error"}] * 3
        assert compute_severity_score(viols) == pytest.approx(30.0)

    def test_severity_score_only_warnings(self):
        """Score = Warnings*2 when only warning-type violations exist."""
        viols = [{"type": "warning"}] * 5
        assert compute_severity_score(viols) == pytest.approx(10.0)

    def test_severity_score_only_info(self):
        """Score = Info*0.5 when only info-type violations exist."""
        viols = [{"type": "convention"}] * 4
        assert compute_severity_score(viols) == pytest.approx(2.0)

    def test_severity_score_mixed_types(self):
        """Score = Errors*10 + Warnings*2 + Info*0.5 for mixed violations."""
        viols = (
            [{"type": "error"}] * 2
            + [{"type": "warning"}] * 3
            + [{"type": "convention"}] * 4
        )
        expected = 2 * 10 + 3 * 2 + 4 * 0.5
        assert compute_severity_score(viols) == pytest.approx(expected)

    def test_clean_code_has_zero_errors(self, pylint_clean):
        """Clean code must have 0 error-level violations."""
        b = bucket_violations(pylint_clean)
        assert len(b["errors"]) == MAX_ERRORS

    def test_warning_count_per_kloc_on_clean_code(self, pylint_clean):
        """Warnings per KLOC on clean code stays under the 10/KLOC limit."""
        loc = count_loc(SAMPLE_DIR / "sample_clean.py")
        b = bucket_violations(pylint_clean)
        warnings_per_kloc = len(b["warnings"]) / (loc / 1000) if loc else 0
        assert warnings_per_kloc <= MAX_WARNINGS_PER_KLOC

    def test_normalised_score_applied_correctly(self, pylint_mixed_severity):
        """Normalised score MAX(0, 100-severity_score) stays in [0,100]."""
        raw = compute_severity_score(pylint_mixed_severity)
        score = max(0, 100 - raw)
        assert 0 <= score <= 100
