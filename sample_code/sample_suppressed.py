"""Module demonstrating inline suppression comments (pylint: disable)."""
import os   # pylint: disable=unused-import   <- suppressed W0611
import sys  # pylint: disable=unused-import   <- suppressed W0611


def function_with_suppressed_violation():
    """Function where violations are suppressed via inline comments."""
    x = 1  # pylint: disable=invalid-name    <- suppressed C0103
    unused = "never used"  # pylint: disable=unused-variable  <- suppressed W0612
    return x + 1


def another_suppressed_function(A, B):   # pylint: disable=invalid-name
    """Arguments suppressed."""
    result = A + B
    return result


# pylint: disable=invalid-name
PascalVar = 10   # suppressed - no violation reported
camelVar = 20    # suppressed
# pylint: enable=invalid-name


def clean_function(value: int) -> int:
    """No violations and no suppression needed here."""
    return value * 2
