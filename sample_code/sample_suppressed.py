"""Module demonstrating inline suppression comments (pylint: disable)."""
import os   # pylint: disable=unused-import
import sys  # pylint: disable=unused-import


def function_with_suppressed_violation():
    """Function where violations are suppressed via inline comments."""
    x = 1  # pylint: disable=invalid-name
    unused = "never used"  # pylint: disable=unused-variable
    return x + 1


def another_suppressed_function(arg_a, arg_b):  # pylint: disable=invalid-name
    """Arguments suppressed."""
    result = arg_a + arg_b
    return result


# pylint: disable=invalid-name
PascalVar = 10
camelVar = 20
# pylint: enable=invalid-name


def clean_function(value: int) -> int:
    """No violations and no suppression needed here."""
    return value * 2
