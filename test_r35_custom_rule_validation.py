"""
test_r35_custom_rule_validation.py
=============================================================
Metric   : Project-Specific Enforcement              (R35)
Category : Lint / Rule Violations
L4       : Custom Rule Validation
L5       : Project-Specific Enforcement
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Plugin   : custom_pylint_plugin.py (W9001 - too-many-function-args-custom)
Formula  : Custom Rule Pass Rate % = (Custom Checks Passing / Total Custom Checks) * 100
Threshold: 100% of project-specific custom rules passing
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from conftest import BASE_DIR, PLUGIN_PATH, SAMPLE_DIR, run_pylint

CUSTOM_SYMBOL = "too-many-function-args-custom"
PROJECT_MAX_ARGS = 3

# Functions in sample_custom_rule.py that SHOULD violate the custom rule
EXPECTED_VIOLATING_FUNCTIONS = {
    "function_violates_custom_rule",
    "another_violation",
    "validate",  # method inside ServiceHandler
}
# Functions that SHOULD pass
EXPECTED_COMPLIANT_FUNCTIONS = {
    "function_ok",
    "function_borderline",
    "process",
}


def _run_with_custom_plugin(target: Path) -> list[dict]:
    """Run pylint with custom plugin enabled, only the custom rule active."""
    if not PLUGIN_PATH.exists():
        return []
    init_hook = f"import sys; sys.path.insert(0, '{str(BASE_DIR).replace(chr(92), chr(47))}')"
    return run_pylint(
        target,
        extra_args=[
            "--init-hook", init_hook,
            "--load-plugins", "custom_pylint_plugin",
            "--disable=all",
            f"--enable={CUSTOM_SYMBOL}",
        ],
    )


def compute_custom_rule_pass_rate(violations: list[dict], total_checks: int) -> float:
    """Custom Rule Pass Rate % = (Passing Checks / Total Custom Checks) * 100."""
    if total_checks == 0:
        return 100.0
    failing = len([v for v in violations if v.get("symbol") == CUSTOM_SYMBOL])
    passing = max(0, total_checks - failing)
    return (passing / total_checks) * 100


class TestCustomPluginLoading:
    """R35: Custom pylint plugin is importable and registers correctly."""

    def test_plugin_file_exists(self):
        """custom_pylint_plugin.py is present in the project root."""
        assert PLUGIN_PATH.exists(), (
            f"Plugin not found at {PLUGIN_PATH}"
        )

    def test_plugin_module_importable(self):
        """The plugin module can be imported without errors."""
        if not PLUGIN_PATH.exists():
            pytest.skip("Plugin file not present")
        sys.path.insert(0, str(BASE_DIR))
        try:
            import custom_pylint_plugin as plugin  # pylint: disable=import-outside-toplevel
            assert hasattr(plugin, "register"), "Plugin must expose a register() function"
        finally:
            sys.path.pop(0)

    def test_plugin_register_callable(self):
        """register() in the plugin is callable."""
        if not PLUGIN_PATH.exists():
            pytest.skip("Plugin file not present")
        sys.path.insert(0, str(BASE_DIR))
        try:
            import custom_pylint_plugin as plugin  # pylint: disable=import-outside-toplevel
            assert callable(plugin.register)
        finally:
            sys.path.pop(0)


class TestCustomRuleViolationDetection:
    """R35: Custom rule fires on violating functions and not on compliant ones."""

    def test_custom_rule_fires_on_target_file(self):
        """Custom plugin detects violations in sample_custom_rule.py."""
        if not PLUGIN_PATH.exists():
            pytest.skip("Plugin file not present")
        violations = _run_with_custom_plugin(SAMPLE_DIR / "sample_custom_rule.py")
        custom_viols = [v for v in violations if v.get("symbol") == CUSTOM_SYMBOL]
        assert len(custom_viols) >= 1, (
            f"Expected custom rule violations; got: {violations}"
        )

    def test_custom_rule_does_not_fire_on_clean_file(self):
        """Custom plugin does not fire on the clean sample (all functions <= 3 args)."""
        if not PLUGIN_PATH.exists():
            pytest.skip("Plugin file not present")
        violations = _run_with_custom_plugin(SAMPLE_DIR / "sample_clean.py")
        custom_viols = [v for v in violations if v.get("symbol") == CUSTOM_SYMBOL]
        assert len(custom_viols) == 0

    def test_violating_function_names_in_violations(self):
        """Violation obj fields reference the expected violating function names."""
        if not PLUGIN_PATH.exists():
            pytest.skip("Plugin file not present")
        violations = _run_with_custom_plugin(SAMPLE_DIR / "sample_custom_rule.py")
        violated_fns = {v.get("obj", "") for v in violations if v.get("symbol") == CUSTOM_SYMBOL}
        assert EXPECTED_VIOLATING_FUNCTIONS & violated_fns, (
            f"Expected {EXPECTED_VIOLATING_FUNCTIONS} in {violated_fns}"
        )


class TestProjectEnforcementFormula:
    """R35: Custom Rule Pass Rate formula and 100% threshold."""

    def test_pass_rate_100_with_no_custom_violations(self):
        """Pass rate is 100% when no custom-rule violations exist."""
        assert compute_custom_rule_pass_rate([], total_checks=10) == pytest.approx(100.0)

    def test_pass_rate_zero_when_all_checks_fail(self):
        """Pass rate is 0% when all custom checks have violations."""
        viols = [{"symbol": CUSTOM_SYMBOL}] * 5
        assert compute_custom_rule_pass_rate(viols, total_checks=5) == pytest.approx(0.0)

    def test_pass_rate_partial_failure(self):
        """Pass rate = 60% when 3 out of 5 checks pass (2 violations)."""
        viols = [{"symbol": CUSTOM_SYMBOL}] * 2
        rate = compute_custom_rule_pass_rate(viols, total_checks=5)
        assert rate == pytest.approx(60.0)

    def test_pass_rate_threshold_must_be_100(self):
        """Any failing custom check means the 100% threshold is not met."""
        viols = [{"symbol": CUSTOM_SYMBOL}]
        rate = compute_custom_rule_pass_rate(viols, total_checks=1)
        assert rate < 100.0, "Even 1 custom rule violation must fail the threshold"
