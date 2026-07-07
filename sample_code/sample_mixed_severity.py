"""Module mixing E (error), W (warning), C (convention), R (refactor) severity levels."""
import os    # W0611


def function_with_errors():
    """Contains an error-level violation."""
    value = undefined_variable   # E0602 undefined-variable (Error)
    return value


def function_with_warnings(data):
    """Contains warning-level violations."""
    unused_var = "not used"    # W0612 (Warning)
    return len(data)


def PascalCaseFunction(Arg):   # C0103 (Convention)
    """Convention-level naming violation."""
    LocalVar = Arg * 2         # C0103 (Convention)
    return LocalVar


def function_too_complex(a, b, c, d, e, f):  # R0913 (Refactor)
    """Refactor-level violation (too many arguments)."""
    return a + b + c + d + e + f
