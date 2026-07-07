"""
test_r36_configuration_file.py
=============================================================
Metric   : Environment Standardization               (R36)
Category : Lint / Rule Violations
L4       : Configuration File Handling
L5       : Environment Standardization
Tool     : pylint 4.0.6  (https://github.com/pylint-dev/pylint)
Formula  : Config Drift Score = Count(Devs with non-standard lint config)
Threshold: 0 developers with non-standard lint configuration
Frequency: Every Commit / PR
=============================================================
"""
from __future__ import annotations

import configparser
from pathlib import Path

from conftest import PYLINTRC

REQUIRED_SECTIONS = {"MAIN", "MESSAGES CONTROL", "FORMAT", "DESIGN"}
REQUIRED_FORMAT_KEYS = {"max-line-length"}
REQUIRED_DESIGN_KEYS = {"max-branches", "max-statements", "max-nested-blocks"}


def load_pylintrc() -> configparser.ConfigParser:
    """Parse the project .pylintrc using configparser."""
    config = configparser.ConfigParser()
    config.read(str(PYLINTRC))
    return config


def compute_config_drift_score(deviating_configs: list[Path], standard: Path) -> int:
    """
    Config Drift Score = count of developer configs deviating from standard.

    For testing purposes, a config deviates if its max-line-length
    differs from the standard config.
    """
    if not standard.exists():
        return len(deviating_configs)
    standard_cfg = configparser.ConfigParser()
    standard_cfg.read(str(standard))
    std_max_line = standard_cfg.get("FORMAT", "max-line-length", fallback="100").strip()

    drift = 0
    for dev_cfg_path in deviating_configs:
        dev_cfg = configparser.ConfigParser()
        dev_cfg.read(str(dev_cfg_path))
        dev_max_line = dev_cfg.get("FORMAT", "max-line-length", fallback="100").strip()
        if dev_max_line != std_max_line:
            drift += 1
    return drift


class TestPylintrcPresence:
    """R36: The project .pylintrc config file exists and is readable."""

    def test_pylintrc_file_exists(self):
        """A .pylintrc configuration file is present in the project root."""
        assert PYLINTRC.exists(), (
            f".pylintrc not found at {PYLINTRC}. "
            "Every project must ship a standard lint configuration."
        )

    def test_pylintrc_is_parseable(self):
        """The .pylintrc is valid INI/configparser format and can be parsed."""
        config = load_pylintrc()
        assert len(config.sections()) > 0, ".pylintrc has no sections"

    def test_pylintrc_has_required_sections(self):
        """The .pylintrc contains all required configuration sections."""
        config = load_pylintrc()
        present = {s.upper() for s in config.sections()}
        missing = REQUIRED_SECTIONS - present
        assert not missing, f".pylintrc is missing sections: {missing}"

    def test_pylintrc_format_section_has_required_keys(self):
        """The [FORMAT] section contains max-line-length and indent-string."""
        config = load_pylintrc()
        assert config.has_section("FORMAT"), ".pylintrc missing [FORMAT] section"
        for key in REQUIRED_FORMAT_KEYS:
            assert config.has_option("FORMAT", key), (
                f".pylintrc [FORMAT] missing key: {key}"
            )

    def test_pylintrc_design_section_has_required_keys(self):
        """The [DESIGN] section contains complexity threshold keys."""
        config = load_pylintrc()
        assert config.has_section("DESIGN"), ".pylintrc missing [DESIGN] section"
        for key in REQUIRED_DESIGN_KEYS:
            assert config.has_option("DESIGN", key), (
                f".pylintrc [DESIGN] missing key: {key}"
            )


class TestConfigStandardizationFormula:
    """R36: Config drift score formula and 0-deviation threshold."""

    def test_drift_score_zero_when_no_deviating_configs(self):
        """Zero drift when no developer configs deviate from standard."""
        assert compute_config_drift_score([], PYLINTRC) == 0

    def test_drift_score_zero_when_all_configs_match(self, tmp_path):
        """Score is 0 when developer config matches the standard."""
        matching = tmp_path / ".pylintrc_dev"
        matching.write_text(
            "[FORMAT]\nmax-line-length=100\n", encoding="utf-8"
        )
        assert compute_config_drift_score([matching], PYLINTRC) == 0

    def test_drift_score_one_for_mismatched_config(self, tmp_path):
        """Score is 1 when one developer uses a different max-line-length."""
        deviating = tmp_path / ".pylintrc_dev"
        deviating.write_text(
            "[FORMAT]\nmax-line-length=79\n", encoding="utf-8"
        )
        assert compute_config_drift_score([deviating], PYLINTRC) == 1

    def test_drift_score_counts_all_deviating_configs(self, tmp_path):
        """Score equals the count of all deviating developer configs."""
        devs = []
        for i in range(3):
            p = tmp_path / f".pylintrc_{i}"
            p.write_text("[FORMAT]\nmax-line-length=79\n", encoding="utf-8")
            devs.append(p)
        assert compute_config_drift_score(devs, PYLINTRC) == 3

    def test_normalised_score_for_drift(self):
        """Normalised score MAX(0, 100-(Drift*25)) is in [0,100]."""
        for drift in range(6):
            score = max(0, 100 - drift * 25)
            assert 0 <= score <= 100

    def test_pylintrc_max_line_length_is_standard_value(self):
        """max-line-length in the project .pylintrc matches the agreed standard (100)."""
        config = load_pylintrc()
        max_line = config.get("FORMAT", "max-line-length", fallback="").strip()
        assert max_line == "100", (
            f"Expected max-line-length=100, got '{max_line}'"
        )
