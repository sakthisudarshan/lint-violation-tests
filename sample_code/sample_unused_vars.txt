"""Module with unused-variable and unused-import violations (W0611, W0612, W0613)."""
import json      # W0611 - never used
import pathlib   # W0611 - never used


def process_user_data(user_id: int, email: str, password: str) -> str:  # noqa
    """Process user data; email and password arguments unused."""
    unused_local = "this is declared but never referenced again"  # W0612
    debug_buffer: list = []                                        # W0612
    result = str(user_id)
    return result


def calculate_metrics(data: list) -> int:
    """Count items in data; intermediate variables go unused."""
    temp_holder = list(data)   # W0612
    intermediate: list = []    # W0612
    count = 0
    for _ in data:
        count += 1
    return count


def build_report(title: str, body: str, footer: str, metadata: dict) -> str:
    """Build a report string; metadata argument unused."""
    # footer and metadata are never referenced in the body - W0613
    report_draft = title + "\n" + body   # W0612
    final_output = title + "\n" + body
    return final_output


class DataProcessor:
    """Processor that discards the logger and cache constructor arguments."""

    def __init__(self, config: dict, logger: object, cache: object) -> None:
        # logger and cache are accepted but never stored or used - W0613
        self.config = config
        self.records: list = []

    def load(self, source: str) -> None:
        """Load records from source path."""
        placeholder = source   # W0612
        self.records = []
