from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from .paths import schema_root


class SchemaValidationError(ValueError):
    pass


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_registry(root: Path | None = None) -> tuple[Registry, dict[str, dict[str, Any]]]:
    root = root or schema_root()
    registry: Registry = Registry()
    schemas: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("*.schema.json")):
        schema = _load_json(path)
        schema_id = schema.get("$id")
        if not schema_id:
            raise SchemaValidationError(f"Schema has no $id: {path}")
        registry = registry.with_resource(schema_id, Resource.from_contents(schema))
        schemas[path.name] = schema
    return registry, schemas


def validate_instance(instance: Any, schema_name: str, root: Path | None = None) -> list[str]:
    registry, schemas = build_registry(root)
    try:
        schema = schemas[schema_name]
    except KeyError as exc:
        raise SchemaValidationError(f"Unknown schema: {schema_name}") from exc
    validator = Draft202012Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    return [f"/{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in errors]


def validate_file(path: Path, schema_name: str, root: Path | None = None) -> list[str]:
    return validate_instance(_load_json(path), schema_name, root)


def validate_schema_bundle(root: Path | None = None) -> list[str]:
    root = root or schema_root()
    registry, schemas = build_registry(root)
    errors: list[str] = []
    for name, schema in sorted(schemas.items()):
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # pragma: no cover - defensive report path
            errors.append(f"{name}: invalid metaschema: {exc}")

    examples = {
        "canonical_example_registry.json": "registry_state.schema.json",
        "canonical_example_proof.json": "proof_object.schema.json",
    }
    for filename, schema_name in examples.items():
        path = root / filename
        if not path.exists():
            errors.append(f"Missing canonical example: {filename}")
            continue
        instance = _load_json(path)
        validator = Draft202012Validator(schemas[schema_name], registry=registry)
        for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
            errors.append(f"{filename}: {error.message}")
    return errors
