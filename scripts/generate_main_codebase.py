"""
Generate pylint-clean application code under src/enterprise_platform/.

Target: 50,000+ logical lines of code (non-empty, non-comment).
Idempotent: skips files that already exist.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_ROOT = ROOT_DIR / "src" / "enterprise_platform"
TARGET_LOC = 50_000
LINES_PER_MODULE = 250

DOMAINS = [
    "catalog", "inventory", "orders", "billing", "shipping", "customers",
    "auth", "analytics", "notifications", "reporting", "pricing",
    "promotions", "warehouse", "suppliers", "returns", "support",
    "audit", "scheduling", "config", "compliance",
]

LAYERS = ["models", "repositories", "services", "validators"]


def count_loc(directory: Path) -> int:
    """Count non-empty, non-comment logical lines."""
    total = 0
    for py_file in directory.rglob("*.py"):
        for line in py_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                total += 1
    return total


def _entity_name(domain: str, index: int) -> str:
    parts = domain.split("_")
    base = "".join(p.capitalize() for p in parts)
    return f"{base}Entity{index:02d}"


def _snake(domain: str, layer: str, index: int) -> str:
    return f"{domain}_{layer}_{index:02d}"


def _model_lines(domain: str, index: int) -> list[str]:
    entity = _entity_name(domain, index)
    lines = [
        f'"""{entity} model for the {domain} domain."""',
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass, field",
        "from datetime import datetime",
        "from typing import Any",
        "",
        "",
        "@dataclass(slots=True)",
        f"class {entity}:",
        f'    """Data model representing a {domain} record."""',
        "    entity_id: str",
        "    name: str",
        '    status: str = "active"',
        "    created_at: datetime = field(default_factory=datetime.utcnow)",
        "    updated_at: datetime = field(default_factory=datetime.utcnow)",
        "    metadata: dict[str, Any] = field(default_factory=dict)",
        "",
    ]
    for method_idx in range(1, 16):
        lines.extend([
            f"    def describe_{method_idx}(self) -> str:",
            f'        """Return a human-readable description for variant {method_idx}."""',
            "        parts = [self.entity_id, self.name, self.status]",
            f"        parts.append(str({method_idx}))",
            '        return " | ".join(parts)',
            "",
            f"    def is_active_{method_idx}(self) -> bool:",
            f'        """Check whether the entity is active for rule {method_idx}."""',
            '        if self.status == "active":',
            "            return True",
            '        if self.status == "pending":',
            f"            return {method_idx % 2} == 0",
            "        return False",
            "",
            f"    def with_status_{method_idx}(self, status: str) -> {entity}:",
            f'        """Return a copy with updated status for scenario {method_idx}."""',
            "        return type(self)(",
            "            entity_id=self.entity_id,",
            "            name=self.name,",
            "            status=status,",
            "            created_at=self.created_at,",
            "            updated_at=datetime.utcnow(),",
            "            metadata=dict(self.metadata),",
            "        )",
            "",
        ])
    return lines


def _repository_lines(domain: str, index: int) -> list[str]:
    entity = _entity_name(domain, index)
    repo = f"{entity}Repository"
    store = f"_{domain}_store_{index}"
    lines = [
        f'"""Repository for {entity} persistence."""',
        "from __future__ import annotations",
        "",
        f"from enterprise_platform.{domain}.models.{_snake(domain, 'models', index)} import {entity}",
        "",
        "",
        f"class {repo}:",
        f'    """In-memory repository for {entity} records."""',
        "",
        "    def __init__(self) -> None:",
        f"        self.{store}: dict[str, {entity}] = {{}}",
        "",
        f"    def get(self, entity_id: str) -> {entity} | None:",
        '        """Fetch a record by identifier."""',
        f"        return self.{store}.get(entity_id)",
        "",
        f"    def save(self, record: {entity}) -> None:",
        '        """Persist or update a record."""',
        f"        self.{store}[record.entity_id] = record",
        "",
        f"    def delete(self, entity_id: str) -> bool:",
        '        """Remove a record when present."""',
        f"        return self.{store}.pop(entity_id, None) is not None",
        "",
        f"    def list_all(self) -> list[{entity}]:",
        '        """Return all stored records."""',
        f"        return list(self.{store}.values())",
        "",
    ]
    for method_idx in range(1, 14):
        lines.extend([
            f"    def find_by_status_{method_idx}(self, status: str) -> list[{entity}]:",
            f'        """Filter records by status for query {method_idx}."""',
            "        results: list = []",
            f"        for record in self.{store}.values():",
            "            if record.status == status:",
            "                results.append(record)",
            '            elif status == "any" and record.is_active_{0}():'.format(method_idx),
            "                results.append(record)",
            "        return results",
            "",
            f"    def count_by_name_{method_idx}(self, prefix: str) -> int:",
            f'        """Count records whose name starts with prefix ({method_idx})."""',
            "        total = 0",
            f"        for record in self.{store}.values():",
            "            if record.name.startswith(prefix):",
            "                total += 1",
            "        return total",
            "",
        ])
    return lines


def _service_lines(domain: str, index: int) -> list[str]:
    entity = _entity_name(domain, index)
    repo = f"{entity}Repository"
    service = f"{entity}Service"
    mod = _snake(domain, "models", index)
    repo_mod = _snake(domain, "repositories", index)
    model_import = (
        f"from enterprise_platform.{domain}.models.{mod} "
        f"import {entity}"
    )
    repo_import = (
        f"from enterprise_platform.{domain}.repositories.{repo_mod} "
        f"import {repo}"
    )
    lines = [
        f'"""Service layer for {entity} operations."""',
        "from __future__ import annotations",
        "",
        model_import,
        repo_import,
        "",
        "",
        f"class {service}:",
        f'    """Business service coordinating {entity} workflows."""',
        "",
        f"    def __init__(self, repository: {repo} | None = None) -> None:",
        f"        self._repository = repository or {repo}()",
        "",
        f"    def register(self, entity_id: str, name: str) -> {entity}:",
        '        """Create and store a new entity."""',
        f"        record = {entity}(entity_id=entity_id, name=name)",
        "        self._repository.save(record)",
        "        return record",
        "",
        f"    def fetch(self, entity_id: str) -> {entity} | None:",
        '        """Retrieve an entity by id."""',
        "        return self._repository.get(entity_id)",
        "",
    ]
    for method_idx in range(1, 15):
        lines.extend([
            f"    def activate_{method_idx}(self, entity_id: str) -> {entity} | None:",
            f'        """Activate an entity using workflow step {method_idx}."""',
            "        record = self._repository.get(entity_id)",
            "        if record is None:",
            "            return None",
            f"        updated = record.with_status_{method_idx}(\"active\")",
            "        self._repository.save(updated)",
            "        return updated",
            "",
            f"    def summarize_{method_idx}(self) -> dict[str, int]:",
            f'        """Summarize repository contents for dashboard {method_idx}."""',
            '        summary = {"active": 0, "inactive": 0, "pending": 0}',
            "        for record in self._repository.list_all():",
            '            key = record.status if record.status in summary else "inactive"',
            "            summary[key] = summary.get(key, 0) + 1",
            '        summary["total"] = len(self._repository.list_all())',
            "        return summary",
            "",
        ])
    return lines


def _validator_lines(domain: str, index: int) -> list[str]:
    entity = _entity_name(domain, index)
    lines = [
        f'"""Validation helpers for {entity}."""',
        "from __future__ import annotations",
        "",
        f"from enterprise_platform.{domain}.models.{_snake(domain, 'models', index)} import {entity}",
        "",
        "",
        f"def validate_entity_id_{index}(entity_id: str) -> bool:",
        '    """Return True when the identifier is non-empty and well-formed."""',
        "    if not entity_id:",
        "        return False",
        "    if len(entity_id) < 3:",
        "        return False",
        '    return entity_id.isalnum() or "-" in entity_id',
        "",
        f"def validate_name_{index}(name: str) -> bool:",
        '    """Return True when the display name is acceptable."""',
        "    if not name.strip():",
        "        return False",
        "    if len(name) > 100:",
        "        return False",
        "    return True",
        "",
        f"def validate_record_{index}(record: {entity}) -> list[str]:",
        '    """Validate a full record and return error messages."""',
        "    errors: list[str] = []",
        f"    if not validate_entity_id_{index}(record.entity_id):",
        '        errors.append("invalid entity_id")',
        f"    if not validate_name_{index}(record.name):",
        '        errors.append("invalid name")',
        '    if record.status not in {"active", "inactive", "pending"}:',
        '        errors.append("invalid status")',
        "    return errors",
        "",
    ]
    for method_idx in range(1, 16):
        lines.extend([
            f"def validate_status_transition_{index}_{method_idx}(current: str, new: str) -> bool:",
            f'    """Validate status transition rule {method_idx}."""',
            "    allowed = {",
            '        "active": {"inactive", "pending"},',
            '        "pending": {"active", "inactive"},',
            '        "inactive": {"active"},',
            "    }",
            "    options = allowed.get(current, set())",
            "    return new in options",
            "",
            f"def normalize_name_{index}_{method_idx}(name: str) -> str:",
            f'    """Normalize a display name for comparison {method_idx}."""',
            '    cleaned = " ".join(name.split())',
            "    return cleaned.lower()",
            "",
        ])
    return lines


def _pad_module(lines: list[str], target: int) -> list[str]:
    """Pad a module with lightweight helper functions until target LOC is met."""
    current = sum(
        1 for line in lines if line.strip() and not line.strip().startswith("#")
    )
    helper_idx = 0
    while current < target:
        helper_idx += 1
        lines.extend([
            "",
            f"def helper_padding_{helper_idx}() -> int:",
            f'    """Padding helper {helper_idx} to reach module line target."""',
            "    values = [1, 2, 3, 4, 5]",
            "    total = 0",
            "    for value in values:",
            f"        total += value + {helper_idx}",
            "    return total",
        ])
        current = sum(
            1 for line in lines if line.strip() and not line.strip().startswith("#")
        )
    return lines


def _write_module(path: Path, lines: list[str], target: int, force: bool = False) -> None:
    """Write module if missing or when force is True."""
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    padded = _pad_module(lines, target)
    content = "\n".join(padded)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


def _ensure_init(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('"""Package module."""\n', encoding="utf-8")


def generate_modules(target_loc: int = TARGET_LOC, force: bool = False) -> int:
    """Generate modules until target LOC is reached."""
    if force and SRC_ROOT.exists():
        shutil.rmtree(SRC_ROOT)

    src_init = ROOT_DIR / "src" / "__init__.py"
    SRC_ROOT.mkdir(parents=True, exist_ok=True)
    if not src_init.exists():
        src_init.write_text('"""Application source root."""\n', encoding="utf-8")

    init = SRC_ROOT / "__init__.py"
    if not init.exists():
        init.write_text('"""Enterprise platform application package."""\n', encoding="utf-8")

    existing = count_loc(SRC_ROOT)
    if existing >= target_loc and not force:
        print(f"Already at {existing} LOC (target {target_loc}). Skipping generation.")
        return existing

    index = 1
    while count_loc(SRC_ROOT) < target_loc:
        for domain in DOMAINS:
            if count_loc(SRC_ROOT) >= target_loc:
                break
            _ensure_init(SRC_ROOT / domain / "__init__.py")
            for layer in LAYERS:
                if count_loc(SRC_ROOT) >= target_loc:
                    break
                _ensure_init(SRC_ROOT / domain / layer / "__init__.py")
                fname = f"{_snake(domain, layer, index)}.py"
                path = SRC_ROOT / domain / layer / fname
                if layer == "models":
                    lines = _model_lines(domain, index)
                elif layer == "repositories":
                    lines = _repository_lines(domain, index)
                elif layer == "services":
                    lines = _service_lines(domain, index)
                else:
                    lines = _validator_lines(domain, index)
                _write_module(path, lines, LINES_PER_MODULE, force=force)
        index += 1

    total = count_loc(SRC_ROOT)
    print(f"Generated codebase: {total} LOC in {SRC_ROOT}")
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate enterprise_platform source code.")
    parser.add_argument("--target", type=int, default=TARGET_LOC, help="Target LOC")
    parser.add_argument("--force", action="store_true", help="Regenerate all modules")
    args = parser.parse_args()
    total = generate_modules(args.target, force=args.force)
    if total < args.target:
        raise SystemExit(f"Failed to reach target LOC: {total} < {args.target}")


if __name__ == "__main__":
    main()
