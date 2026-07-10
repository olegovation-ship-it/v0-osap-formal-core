from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import fixture_root
from .schema_validation import validate_instance
from .semantic import check_registry


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def discover_fixtures(root: Path | None = None) -> list[Path]:
    root = root or fixture_root()
    return sorted(root.glob("**/*.fixture.json"))


def replay_fixture(descriptor_path: Path) -> dict[str, Any]:
    descriptor = _load(descriptor_path)
    descriptor_errors = validate_instance(descriptor, "fixture.schema.json")
    if descriptor_errors:
        return {"fixture_id": descriptor.get("fixture_id"), "passed": False, "errors": descriptor_errors}

    input_path = (descriptor_path.parent / descriptor["input_file"]).resolve()
    registry = _load(input_path)
    schema_errors = validate_instance(registry, "registry_state.schema.json")
    if schema_errors:
        return {"fixture_id": descriptor["fixture_id"], "passed": False, "errors": schema_errors}

    result = check_registry(registry)
    actual_codes = [item["code"] for item in result["diagnostics"]]
    expected_codes = descriptor["expected_diagnostics"]
    passed = result["status"] == descriptor["expected_status"] and actual_codes == expected_codes
    return {
        "fixture_id": descriptor["fixture_id"],
        "passed": passed,
        "expected_status": descriptor["expected_status"],
        "actual_status": result["status"],
        "expected_diagnostics": expected_codes,
        "actual_diagnostics": actual_codes,
    }


def replay_all(root: Path | None = None) -> list[dict[str, Any]]:
    return [replay_fixture(path) for path in discover_fixtures(root)]
