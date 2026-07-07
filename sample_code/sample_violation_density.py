"""Clean placeholder — violation code lives in sample_violation_density.txt."""


def calculate_sum(value_a: int, value_b: int) -> int:
    """Return the sum of two integers."""
    return value_a + value_b


def multiply_pair(first: int, second: int) -> int:
    """Return the product of two integers."""
    return first * second


def compute_ratio(numerator: float, denominator: float) -> float:
    """Return numerator / denominator; returns 0.0 when denominator is zero."""
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


class DataContainer:
    """Minimal clean data container."""

    def __init__(self, value: int) -> None:
        self.value = value

    def get_value(self) -> int:
        """Return the stored value."""
        return self.value

    def double(self) -> int:
        """Return twice the stored value."""
        return self.value * 2
