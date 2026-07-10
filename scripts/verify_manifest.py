from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "bootstrap_manifest.json"
SCHEMA = ROOT / "schemas" / "v1.1" / "release_manifest.schema.json"

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
errors = sorted(Draft202012Validator(schema).iter_errors(manifest), key=lambda e: list(e.absolute_path))
if errors:
    for error in errors:
        print(error.message)
    raise SystemExit(1)

failures = []
for item in manifest["files"]:
    path = ROOT / item["path"]
    if not path.is_file():
        failures.append(f"missing: {item['path']}")
        continue
    data = path.read_bytes()
    actual_hash = hashlib.sha256(data).hexdigest()
    if actual_hash != item["sha256"] or len(data) != item["bytes"]:
        failures.append(f"mismatch: {item['path']}")

if failures:
    print("\n".join(failures))
    raise SystemExit(1)
print(f"PASS: verified {len(manifest['files'])} manifest entries.")
