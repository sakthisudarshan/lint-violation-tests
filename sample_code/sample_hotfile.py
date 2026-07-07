"""Clean placeholder — violation code lives in sample_hotfile.txt."""


VALUE_X = 1
VALUE_Y = 2
VALUE_Z = VALUE_X + VALUE_Y


def func_one(val: int) -> None:
    """First clean function."""


def func_two(val: int) -> None:
    """Second clean function."""


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
        """Clean method."""
        return 0
