"""Target module for custom pylint rule validation (R35).

The custom plugin checks: no public function may have more than 3 parameters.
Functions here intentionally exceed that limit for testing purposes.
"""


def function_ok(a: int, b: int) -> int:
    """Compliant - 2 parameters."""
    return a + b


def function_borderline(a: int, b: int, c: int) -> int:
    """Compliant - exactly 3 parameters (the limit)."""
    return a + b + c


def function_violates_custom_rule(a: int, b: int, c: int, d: int) -> int:
    """CUSTOM RULE VIOLATION - 4 parameters exceeds project limit of 3."""
    return a + b + c + d


def another_violation(name: str, age: int, email: str, role: str) -> str:
    """CUSTOM RULE VIOLATION - 4 parameters."""
    return f"{name} {age} {email} {role}"


class ServiceHandler:
    """Service handler class."""

    def process(self, request: dict) -> dict:
        """Compliant - 1 parameter."""
        return request

    def validate(self, data: dict, schema: dict, strict: bool, verbose: bool) -> bool:
        """CUSTOM RULE VIOLATION - 4 parameters."""
        return bool(data) and bool(schema) and strict and verbose
