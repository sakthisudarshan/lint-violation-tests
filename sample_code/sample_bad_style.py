"""Clean placeholder — violation code lives in sample_bad_style.txt."""


def long_line_function() -> str:
    """Function with properly sized lines."""
    result = "some string value"
    extended = result + " extended"
    return extended


def indentation_function() -> int:
    """Function with correct indentation."""
    value = 1
    if value:
        result = value * 2
        return result
    return 0


def clean_list_function() -> list:
    """Return a simple list."""
    data = [1, 2, 3]
    return data


def first_packed_function() -> None:
    """Placeholder for packed function tests."""


def second_packed_function() -> None:
    """Placeholder for packed function tests."""


def third_packed_function() -> None:
    """Placeholder for packed function tests."""


LONG_CONSTANT_NAME = "this value has a reasonable line length"
