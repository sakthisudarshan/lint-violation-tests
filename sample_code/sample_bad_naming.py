"""Clean placeholder — violation code lives in sample_bad_naming.txt."""


def calculate_total(value_a: float, value_b: float) -> float:
    """Add two values and return the result."""
    result_value = value_a + value_b
    return result_value


def process_data(input_list: list) -> list:
    """Filter and return truthy items from the list."""
    filtered_items = [item for item in input_list if item]
    return filtered_items


class DataManager:
    """Clean data manager."""

    def load_from_file(self, file_path: str) -> str:
        """Load and return file contents."""
        with open(file_path, encoding="utf-8") as fh:
            raw_content = fh.read()
        return raw_content

    def save_to_file(self, file_path: str, content: str) -> None:
        """Write content to the given file path."""
        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(content)


def validate_input(user_input: str) -> bool:
    """Return True when user_input is non-empty."""
    is_valid = bool(user_input)
    return is_valid


NUMBER_OF_ITEMS = 10
CURRENT_USER_NAME = ""
