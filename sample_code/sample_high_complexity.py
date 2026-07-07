"""Clean placeholder — violation code lives in sample_high_complexity.txt."""


def check_values(val_a: int, val_b: int, val_c: int) -> int:
    """Check a small number of values and return accumulated result."""
    result = 0
    if val_a > 0:
        result += 1
    if val_b > 0:
        result += 2
    if val_c > 0:
        result += 3
    return result


def process_nested(data: list) -> list:
    """Process nested data with modest nesting depth."""
    result = []
    if data:
        for group in data:
            if group:
                for item in group:
                    if item is not None:
                        result.append(item)
    return result


def accumulate(items: list) -> int:
    """Accumulate values from items list."""
    total = 0
    for item in items:
        total += item
    return total
