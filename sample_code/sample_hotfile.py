"""Clean placeholder — violation code lives in sample_hotfile.txt."""


VALUE_X = 1
VALUE_Y = 2
VALUE_Z = VALUE_X + VALUE_Y


def func_one(val: int) -> int:
    """First clean function — returns val unchanged."""
    return val


def func_two(val: int) -> int:
    """Second clean function — returns val unchanged."""
    return val


def func_three(val_c: int, val_d: int, val_e: int) -> int:
    """Third clean function — returns sum."""
    return val_c + val_d + val_e


def func_four(val: int) -> int:
    """Fourth clean function."""
    result_val = val * 2
    return result_val


class GoodClass:
    """Properly named class."""

    def good_method(self) -> int:
        """First clean method."""
        return 0

    def describe(self) -> str:
        """Second clean method — satisfies pylint min-public-methods."""
        return "GoodClass"
