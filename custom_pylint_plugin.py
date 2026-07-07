"""
custom_pylint_plugin.py
Project-specific pylint checker for R35 - Custom Rule Validation.

Rule: No public function (outside __init__) may have more than 3 parameters.
Message-id : W9001
Symbol     : too-many-function-args-custom
"""
from __future__ import annotations

from astroid import nodes
from pylint.checkers import BaseChecker

PROJECT_MAX_ARGS = 3
MSG_ID = "W9001"
MSG_SYMBOL = "too-many-function-args-custom"


class ProjectArgLimitChecker(BaseChecker):
    """Enforce a project-specific maximum of 3 parameters per public function."""

    name = "project-arg-limit"
    msgs = {
        MSG_ID: (
            "Public function '%s' has %d parameters; project limit is %d.",
            MSG_SYMBOL,
            "Project-specific rule: public functions must not exceed "
            f"{PROJECT_MAX_ARGS} parameters (excluding 'self'/'cls').",
        )
    }

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        """Check each function definition for the parameter limit."""
        if node.name.startswith("_"):
            return
        args = node.args
        params = args.args or []
        # Exclude self / cls for methods
        effective = [
            a for a in params if a.name not in ("self", "cls")
        ]
        if len(effective) > PROJECT_MAX_ARGS:
            self.add_message(
                MSG_SYMBOL,
                node=node,
                args=(node.name, len(effective), PROJECT_MAX_ARGS),
            )


def register(linter) -> None:
    """Register the checker with pylint."""
    linter.register_checker(ProjectArgLimitChecker(linter))
