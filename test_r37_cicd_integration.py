"""
test_r37_cicd_integration.py
=============================================================
Metric   : Automated Gatekeeping                     (R37)
Category : Lint / Rule Violations
L4       : CI/CD Integration Validation
L5       : Automated Gatekeeping
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Pipeline Gate Pass Rate % = (Passing Builds / Total Builds) * 100
Threshold: 100% of builds pass lint quality gate before merge
Frequency: Every Commit / PR

Pylint exit code semantics (bitfield):
    0  = no errors
    1  = fatal message
    2  = error message
    4  = warning message
    8  = refactor message
    16 = convention message
    32 = usage error
=============================================================
"""
from __future__ import annotations

import pytest

from conftest import SAMPLE_DIR, bucket_violations, run_pylint_with_exit_code

# Gate rule: builds fail when exit code has bit 1 (fatal) or bit 2 (error) set
ERROR_EXIT_BITS = 0b00000011  # bits 1 and 2


def gate_passes(exit_code: int) -> bool:
    """Return True when the pylint exit code indicates no fatal/error violations."""
    return (exit_code & ERROR_EXIT_BITS) == 0


def compute_pipeline_gate_pass_rate(results: list[bool]) -> float:
    """Pipeline Gate Pass Rate % = (Passing Builds / Total Builds) * 100."""
    if not results:
        return 100.0
    return (sum(results) / len(results)) * 100


class TestPylintGateBehaviour:
    """R37: Pylint exit code correctly signals pass/fail for CI gates."""

    def test_clean_code_exit_code_has_no_error_bits(self):
        """Clean code: pylint exits with 0 error bits set (gate passes)."""
        _, code = run_pylint_with_exit_code(SAMPLE_DIR / "sample_clean.py")
        assert gate_passes(code), (
            f"Clean code gate failed with exit code {code} (bits: {bin(code)})"
        )

    def test_error_code_triggers_gate_failure(self):
        """Sample with error-level violations: gate must fail."""
        _, code = run_pylint_with_exit_code(SAMPLE_DIR / "sample_mixed_severity.py")
        assert not gate_passes(code), (
            f"Expected gate failure for mixed-severity code, got exit code {code}"
        )

    def test_convention_only_code_can_pass_gate(self, pylint_bad_naming):
        """Convention/refactor only violations do not set error bits (gate may pass)."""
        _, code = run_pylint_with_exit_code(SAMPLE_DIR / "sample_bad_naming.py")
        error_bits_set = bool(code & ERROR_EXIT_BITS)
        naming_errors = [v for v in pylint_bad_naming if v.get("type") in ("error", "fatal")]
        if not naming_errors:
            assert not error_bits_set

    def test_gate_result_is_boolean(self):
        """gate_passes() always returns a bool regardless of exit code."""
        for code in range(64):
            result = gate_passes(code)
            assert isinstance(result, bool)

    def test_exit_code_bit_2_triggers_failure(self):
        """Bit 2 (error messages) in exit code causes gate to fail."""
        assert not gate_passes(2)
        assert not gate_passes(3)

    def test_exit_code_zero_means_pass(self):
        """Exit code 0 means no issues at all - gate must pass."""
        assert gate_passes(0)

    def test_exit_code_convention_only_gate_passes(self):
        """Exit code 16 (convention only) = gate passes under default gate rules."""
        assert gate_passes(16)

    def test_exit_code_warning_only_gate_passes(self):
        """Exit code 4 (warning only) = gate passes under default gate rules."""
        assert gate_passes(4)


class TestPipelineGatePassRateFormula:
    """R37: Pipeline Gate Pass Rate formula and 100% threshold enforcement."""

    def test_pass_rate_100_for_all_passing_builds(self):
        """100% when all builds pass the gate."""
        results = [True] * 10
        assert compute_pipeline_gate_pass_rate(results) == pytest.approx(100.0)

    def test_pass_rate_0_for_all_failing_builds(self):
        """0% when all builds fail the gate."""
        results = [False] * 10
        assert compute_pipeline_gate_pass_rate(results) == pytest.approx(0.0)

    def test_pass_rate_50_for_half_passing(self):
        """50% pass rate when half the builds pass."""
        results = [True] * 5 + [False] * 5
        assert compute_pipeline_gate_pass_rate(results) == pytest.approx(50.0)

    def test_pass_rate_100_for_no_results(self):
        """Empty results defaults to 100% (no failures known)."""
        assert compute_pipeline_gate_pass_rate([]) == pytest.approx(100.0)

    def test_threshold_requires_100_percent(self):
        """Any failing build means the 100% threshold is not achieved."""
        results = [True] * 9 + [False]
        rate = compute_pipeline_gate_pass_rate(results)
        assert rate < 100.0

    @pytest.mark.parametrize("passing,total", [
        (10, 10),
        (8, 10),
        (5, 10),
        (0, 10),
    ])
    def test_pass_rate_parametrised(self, passing, total):
        """Parametrised pass rate computation."""
        results = [True] * passing + [False] * (total - passing)
        rate = compute_pipeline_gate_pass_rate(results)
        assert rate == pytest.approx((passing / total) * 100)
