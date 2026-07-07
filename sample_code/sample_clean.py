"""Clean Python module - zero lint violations expected."""
from __future__ import annotations

MAX_RETRIES: int = 3
DEFAULT_TIMEOUT: float = 30.0


def calculate_discount(price: float, percentage: float) -> float:
    """Return the discount amount calculated from a price and percentage."""
    if not 0.0 <= percentage <= 100.0:
        raise ValueError(
            f"Percentage must be between 0 and 100, got {percentage}"
        )
    return price * (percentage / 100.0)


def process_items(items: list[str]) -> list[str]:
    """Return a filtered list of stripped, non-empty items."""
    return [item.strip() for item in items if item.strip()]


def count_positives(numbers: list[float]) -> int:
    """Return the count of strictly positive numbers in the list."""
    return sum(1 for n in numbers if n > 0)


class ShoppingCart:
    """Represents a shopping cart with items and computed totals."""

    def __init__(self) -> None:
        self._items: list[tuple[str, float]] = []

    def add_item(self, name: str, price: float) -> None:
        """Add a named item with a price to the cart."""
        self._items.append((name, price))

    def total(self) -> float:
        """Return the sum of all item prices in the cart."""
        return sum(price for _, price in self._items)

    def item_count(self) -> int:
        """Return the number of items currently in the cart."""
        return len(self._items)
