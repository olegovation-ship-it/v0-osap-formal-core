from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .canonical import canonical_text
from .fixtures import replay_all
from .schema_validation import validate_file, validate_schema_bundle
from .semantic import check_registry


def _load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="v0-osap-fc1")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Schema-validate and semantically check a registry state")
    check.add_argument("file", type=Path)

    validate = sub.add_parser("validate", help="Validate a JSON instance against a named schema")
    validate.add_argument("file", type=Path)
    validate.add_argument("--schema", default="registry_state.schema.json")

    sub.add_parser("schema-bundle", help="Replay the canonical schema bundle")
    sub.add_parser("fixtures", help="Replay all fixture descriptors")

    canonical = sub.add_parser("canonicalize", help="Write canonical V0-OSAP-CJ-1 JSON")
    canonical.add_argument("file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "schema-bundle":
        errors = validate_schema_bundle()
        if errors:
            print(json.dumps({"status": "REJECT", "errors": errors}, indent=2))
            return 1
        print(json.dumps({"status": "PASS", "bundle": "schemas/v1.1"}, indent=2))
        return 0

    if args.command == "fixtures":
        results = replay_all()
        passed = all(item["passed"] for item in results)
        print(json.dumps({"status": "PASS" if passed else "REJECT", "fixtures": results}, indent=2))
        return 0 if passed else 1

    if args.command == "canonicalize":
        sys.stdout.write(canonical_text(_load(args.file)))
        return 0

    if args.command == "validate":
        errors = validate_file(args.file, args.schema)
        print(json.dumps({"status": "PASS" if not errors else "REJECT", "errors": errors}, indent=2))
        return 0 if not errors else 1

    if args.command == "check":
        errors = validate_file(args.file, "registry_state.schema.json")
        if errors:
            print(json.dumps({"status": "REJECT", "schema_errors": errors}, indent=2))
            return 1
        result = check_registry(_load(args.file))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1

    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
