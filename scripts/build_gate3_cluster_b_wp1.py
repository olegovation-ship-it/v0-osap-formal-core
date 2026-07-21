#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_PATH = ROOT / "scripts/verify_gate3_cluster_b_wp1.py"

# WP1_POST_MERGE_BUILDER_COMPATIBILITY_V0_1_2
CANONICAL_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
SUCCESSOR_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"


def load_verifier():
    spec = importlib.util.spec_from_file_location("gate3_wp1_verify", VERIFY_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def dump(path: Path, value) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def wp1_paths() -> list[Path]:
    paths: list[Path] = []
    candidates = [
        ROOT / ".github/workflows/gate3-cluster-b-wp1.yml",
        ROOT / "docs/gate3/cluster_b/WP1_BUILD_SPECIFICATION.md",
        ROOT / "docs/gate3/cluster_b/WP1_CLUSTER_REGISTRY_STRONG_DLE_AND_ID_CLOSURE.md",
        ROOT / "scripts/verify_gate3_cluster_b_wp0.py",
        ROOT / "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
        ROOT / "tests/test_gate3_cluster_b_wp0.py",
        ROOT / "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
        ROOT / "scripts/build_gate3_cluster_b_wp1.py",
        ROOT / "scripts/verify_gate3_cluster_b_wp1.py",
        ROOT / "tests/test_gate3_cluster_b_wp1.py",
        ROOT / "release/v1.4.0/tools/patch_wp0_wp1_allowlist.py",
    ]
    paths.extend(p for p in candidates if p.is_file())
    paths.extend(sorted((ROOT / "release/v1.4.0").glob("GATE3_CLUSTER_B_WP1_*.json")))
    paths.extend(sorted((ROOT / "schemas/v1.4.0").glob("gate3_cluster_b_wp1_*.schema.json")))
    ledger = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
    return sorted({p.resolve() for p in paths if p.resolve() != ledger.resolve()}, key=lambda p: p.relative_to(ROOT).as_posix())



def _ledger_entries_from_text(value: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in value.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        digest, rel = line.split("  ", 1)
        entries[rel] = digest
    return entries


def ledger_compatibility_errors(expected_ledger: str) -> list[str]:
    if not CANONICAL_LEDGER.is_file():
        return ["missing canonical WP1 SHA256 ledger"]
    historical_text = CANONICAL_LEDGER.read_text(encoding="utf-8")
    if historical_text == expected_ledger:
        return []
    if not SUCCESSOR_LEDGER.is_file():
        return ["canonical WP1 ledger differs and successor ledger is missing"]

    historical = _ledger_entries_from_text(historical_text)
    current = _ledger_entries_from_text(expected_ledger)
    successor = _ledger_entries_from_text(
        SUCCESSOR_LEDGER.read_text(encoding="utf-8")
    )
    errors: list[str] = []

    for rel, old_digest in historical.items():
        current_digest = current.get(rel)
        if current_digest is None:
            errors.append(f"canonical WP1 path disappeared from builder surface: {rel}")
            continue
        if current_digest != old_digest and successor.get(rel) != current_digest:
            errors.append(f"successor ledger does not attest changed WP1 path: {rel}")

    for rel, current_digest in current.items():
        if rel not in historical and successor.get(rel) != current_digest:
            errors.append(f"successor ledger does not attest new WP1 namespace path: {rel}")

    return errors

def expected_outputs():
    verify = load_verifier()
    collision_path = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_ID_COLLISION_AUDIT.json"
    collision = json.loads(collision_path.read_text(encoding="utf-8"))
    collisions = verify.collision_scan(ROOT)
    collision["collisions"] = collisions
    collision["audit_status"] = "PASS" if not collisions else "FAIL"

    registry_path = ROOT / verify.REGISTRY_PATH
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for record in registry["records"]:
        record["statement_sha256"] = verify.statement_hash(record["formal_signature"])

    overrides = {
        collision_path.resolve(): dump(collision_path, collision),
        registry_path.resolve(): dump(registry_path, registry),
    }
    lines = []
    for path in wp1_paths():
        data = overrides.get(path.resolve(), path.read_text(encoding="utf-8"))
        digest = hashlib.sha256(data.encode("utf-8")).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    ledger = "\n".join(lines) + "\n"
    return overrides, ledger


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ns = ap.parse_args()
    overrides, ledger = expected_outputs()
    ledger_path = CANONICAL_LEDGER
    stale = []
    for path, expected in overrides.items():
        if path.read_text(encoding="utf-8") != expected: stale.append(path.relative_to(ROOT).as_posix())
    compatibility_errors = ledger_compatibility_errors(ledger)
    if compatibility_errors:
        stale.append(ledger_path.relative_to(ROOT).as_posix())
    if ns.check:
        result = {"status":"PASS" if not stale else "FAIL","stale":stale}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if not stale else 1
    for path, expected in overrides.items(): path.write_text(expected, encoding="utf-8")
    if not SUCCESSOR_LEDGER.is_file():
        ledger_path.write_text(ledger, encoding="utf-8")
    verify = load_verifier()
    errors = verify.validate_records(ROOT) + verify.ledger_errors(ROOT)
    result = {"status":"PASS" if not errors else "FAIL","decision":"READY_FOR_HOSTED_CI" if not errors else "HOLD_WITH_BLOCKERS","errors":errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
