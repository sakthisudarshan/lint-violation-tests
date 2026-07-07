"""
test_r33_multiple_violations.py
=============================================================
Metric   : Aggregated Risk Assessment                (R33)
Category : Lint / Rule Violations
L4       : Multiple Violations Detection
L5       : Aggregated Risk Assessment
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Hotfile Score = Count(Files>10 viols)*15 + Count(Files 5-10 viols)*5
Threshold: 0 files with > 10 violations; < 5 files in amber (5-10) range
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

from collections import Counter

import pytest

from conftest import SAMPLE_DIR, compute_hotfile_score, run_pylint

MAX_RED_FILES = 0     # files with > 10 violations
MAX_AMBER_FILES = 5   # files with 5-10 violations


def _violations_per_file(violations: list[dict]) -> Counter:
    """Return a Counter mapping file path -> violation count."""
    return Counter(
        v.get("path", v.get("module", "unknown")) for v in violations
    )


def compute_aggregated_risk_score(violations: list[dict]) -> float:
    """
    Aggregated Risk Score = TotalViolations / DistinctFiles.
    (Average violations per file - proxy for instability.)
    """
    if not violations:
        return 0.0
    per_file = _violations_per_file(violations)
    return len(violations) / len(per_file)


class TestHotfileDetection:
    """R33: Files with concentrated violations are identified as hotfiles."""

    def test_hotfile_sample_exceeds_10_violations(self, pylint_hotfile):
        """The dedicated hotfile sample has > 10 violations in one file."""
        per_file = _violations_per_file(pylint_hotfile)
        hot_files = [f for f, c in per_file.items() if c > 10]
        assert len(hot_files) >= 1, (
            f"Expected >= 1 file with >10 violations; per_file counts = {dict(per_file)}"
        )

    def test_hotfile_score_positive_for_concentrated_code(self, pylint_hotfile):
        """Hotfile score is > 0 for concentrated violation sample."""
        score = compute_hotfile_score(pylint_hotfile)
        assert score > 0

    def test_clean_code_has_no_hotfiles(self, pylint_clean):
        """Clean code: no file exceeds 10 violations."""
        per_file = _violations_per_file(pylint_clean)
        hot_files = [f for f, c in per_file.items() if c > 10]
        assert len(hot_files) == MAX_RED_FILES

    def test_violations_are_associated_with_file_paths(self, pylint_hotfile):
        """Each violation record carries a path or module identifier."""
        for v in pylint_hotfile:
            assert "path" in v or "module" in v

    def test_total_violation_count_reflects_all_files(self, pylint_hotfile):
        """Sum of per-file counts equals the total violations list length."""
        per_file = _violations_per_file(pylint_hotfile)
        assert sum(per_file.values()) == len(pylint_hotfile)


class TestAggregatedRiskFormula:
    """R33: Hotfile score and aggregated risk computation."""

    def test_hotfile_score_formula_with_known_inputs(self):
        """2 red files and 3 amber files = 2*15 + 3*5 = 45."""
        viols = []
        for i in range(2):
            viols += [{"path": f"red_file_{i}.py"}] * 11
        for i in range(3):
            viols += [{"path": f"amber_file_{i}.py"}] * 7
        score = compute_hotfile_score(viols)
        assert score == 2 * 15 + 3 * 5

    def test_hotfile_score_zero_for_no_violations(self):
        """Zero violations = zero hotfile score."""
        assert compute_hotfile_score([]) == 0

    def test_hotfile_score_zero_for_spread_out_violations(self):
        """Violations spread across many files (< 5 per file) = score 0."""
        viols = [{"path": f"file_{i}.py"} for i in range(30)]
        score = compute_hotfile_score(viols)
        assert score == 0

    def test_aggregated_risk_score_per_file_average(self):
        """Average violations per file = 5 for 20 violations across 4 files."""
        viols = []
        for i in range(4):
            viols += [{"path": f"file_{i}.py"}] * 5
        avg = compute_aggregated_risk_score(viols)
        assert avg == pytest.approx(5.0)

    def test_normalised_hotfile_score(self, pylint_hotfile):
        """Normalised score MAX(0, 100-Hotfile_Score) is in [0,100]."""
        score = compute_hotfile_score(pylint_hotfile)
        normalised = max(0, 100 - score)
        assert 0 <= normalised <= 100

    @pytest.mark.parametrize("red,amber,expected_score", [
        (0, 0, 0),
        (1, 0, 15),
        (0, 1, 5),
        (2, 3, 45),
        (3, 1, 50),
    ])
    def test_hotfile_score_parametrised(self, red, amber, expected_score):
        """Parametrised hotfile score formula validation."""
        viols = []
        for i in range(red):
            viols += [{"path": f"red_{i}.py"}] * 11
        for i in range(amber):
            viols += [{"path": f"amber_{i}.py"}] * 7
        assert compute_hotfile_score(viols) == expected_score
