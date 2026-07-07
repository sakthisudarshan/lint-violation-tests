"""Clean placeholder — violation code lives in sample_unused_vars.txt."""


def process_user_data(user_id: int) -> str:
    """Process user data and return a string result."""
    return str(user_id)


def calculate_metrics(data: list) -> int:
    """Count and return the number of items in data."""
    count = 0
    for _ in data:
        count += 1
    return count


def build_report(title: str, body: str) -> str:
    """Build a simple report string from title and body."""
    return title + "\n" + body


class DataProcessor:
    """Clean data processor."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.records: list = []

    def load(self, source: str) -> None:
        """Load records — stores source reference."""
        self.records = [source]
