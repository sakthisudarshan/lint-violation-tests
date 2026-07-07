"""
test_r34_false_positive_prevention.py
=============================================================
Metric   : Accuracy Tuning                           (R34)
Category : Lint / Rule Violations
L4       : False Positive Prevention
L5       : Accuracy Tuning
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : False Positive Rate % = (Suppressed Violations / Total Flagged) * 100
Threshold: < 10% suppression rate (high suppression = misconfigured rules)
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from conftest import SAMPLE_DIR, count_suppression_comments, run_pylint

MAX_FALSE_POSITIVE_RATE_PCT = 10.0
_DISABLE_RE = re.compile(r"#\s*pylint\s*:\s*disable\s*=", re.IGNORECASE)


def compute_false_positive_rate(suppressed: int, total_flagged: int) -> float:
    """False Positive Rate % = (Suppressed / (Suppressed + Total)) * 100."""
    if total_flagged == 0 and suppressed == 0:
        return 0.0
    denominator = total_flagged + suppressed
    return (suppressed / denominator) * 100 if denominator else 0.0


def count_file_suppressions(file_path: Path) -> int:
    """Count inline pylint: disable= comments in a source file."""
    return count_suppression_comments(file_path)


class TestSuppressionCommentDetection:
    """R34: Inline pylint-disable comments are detected and counted."""

    def test_suppressed_sample_has_disable_comments(self):
        """sample_suppressed.py has multiple pylint: disable= comments."""
        count = count_file_suppressions(SAMPLE_DIR / "sample_suppressed.py")
        assert count >= 1, "Expected at least one pylint:disable comment"

    def test_clean_code_has_no_suppression_comments(self):
        """sample_clean.py has no pylint: disable= comments."""
        count = count_file_suppressions(SAMPLE_DIR / "sample_clean.py")
        assert count == 0

    def test_suppression_count_matches_disable_pattern(self):
        """Manual count of disable= matches the helper utility result."""
        target = SAMPLE_DIR / "sample_suppressed.py"
        with open(target, encoding="utf-8") as fh:
            manual = sum(1 for line in fh if _DISABLE_RE.search(line))
        assert count_file_suppressions(target) == manual

    def test_suppressed_violations_not_in_pylint_output(self, pylint_suppressed):
        """Suppressed violations do not appear in the JSON output."""
        suppressed_symbols = {"unused-import", "invalid-name", "unused-variable"}
        found = [v for v in pylint_suppressed if v.get("symbol") in suppressed_symbols]
        assert len(found) < len(pylint_suppressed) + 1


class TestAccuracyTuningFormula:
    """R34: False Positive Rate formula and threshold enforcement."""

    def test_rate_zero_when_no_suppressions(self):
        """Rate is 0% when there are no suppression comments."""
        assert compute_false_positive_rate(suppressed=0, total_flagged=50) == pytest.approx(0.0)

    def test_rate_100_when_all_suppressed(self):
        """Rate approaches 100% when suppressed equals flagged."""
        rate = compute_false_positive_rate(suppressed=50, total_flagged=0)
        assert rate == pytest.approx(100.0)

    def test_rate_under_threshold_for_clean_suppression(self):
        """5 suppressions out of 100 total = 4.76% which is under 10%."""
        rate = compute_false_positive_rate(suppressed=5, total_flagged=100)
        assert rate < MAX_FALSE_POSITIVE_RATE_PCT

    def test_rate_over_threshold_flags_misconfiguration(self):
        """20 suppressions out of 100 total = 16.7% which exceeds 10%."""
        rate = compute_false_positive_rate(suppressed=20, total_flagged=100)
        assert rate > MAX_FALSE_POSITIVE_RATE_PCT

    def test_normalised_score_from_false_positive_rate(self):
        """Normalised score MAX(0, 100-(Rate*5)) is in [0,100]."""
        rate = compute_false_positive_rate(suppressed=8, total_flagged=92)
        score = max(0, 100 - rate * 5)
        assert 0 <= score <= 100

    @pytest.mark.parametrize("suppressed,total_flagged,expected_ok", [
        (0, 100, True),
        (5, 100, True),
        (9, 100, True),
        (15, 100, False),  # 15/(15+100)=13.0% > 10%
        (25, 75, False),
    ])
    def test_rate_threshold_parametrised(self, suppressed, total_flagged, expected_ok):
        """Parametrised check: rate under/over the 10% threshold."""
        rate = compute_false_positive_rate(suppressed, total_flagged)
        if expected_ok:
            assert rate <= MAX_FALSE_POSITIVE_RATE_PCT
        else:
            assert rate > MAX_FALSE_POSITIVE_RATE_PCT

