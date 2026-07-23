#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MERGE = "cdae3ea4e50f6222182f2398c350476fbe820f92"
CANONICAL_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt"
SUCCESSOR_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt"
CONTROLLED = ['release/v1.4.0/tools/patch_wp4_allowlist.py', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4.py']

SCHEMA_PAIRS = [
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_BASELINE_LOCK.json", "schemas/v1.4.0/gate3_cluster_b_wp4_baseline_lock.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_proof_manifest.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_parity_manifest.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_fixture_manifest.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_PRESERVATION_FIREWALL.json", "schemas/v1.4.0/gate3_cluster_b_wp4_preservation_firewall.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_ACCEPTANCE_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp4_acceptance_gates.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP4_SCHEMA_BUNDLE_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_schema_bundle_manifest.schema.json"),
]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def parse_ledger(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            value, rel = line.split("  ", 1)
            out[rel] = value
    return out

def validate(obj, schema_rel: str) -> None:
    errors = sorted(Draft202012Validator(load(schema_rel)).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"schema failure {schema_rel}: {errors[0].message}")

def git_bytes(*args: str) -> bytes:
    cp = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False)
    if cp.returncode:
        raise SystemExit(cp.stderr.decode("utf-8", errors="replace").strip())
    return cp.stdout

def verify_records() -> None:
    for record_rel, schema_rel in SCHEMA_PAIRS:
        validate(load(record_rel), schema_rel)

    wp1 = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json")
    proof = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json")
    parity = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json")
    wp1_index = {row["theorem_id"]: row for row in wp1["records"]}
    proof_index = {row["theorem_id"]: row for row in proof["theorems"]}
    parity_index = {row["theorem_id"]: row for row in parity["records"]}
    expected_ids = {f"T{i}" for i in range(157, 163)}
    if set(wp1_index) != expected_ids or set(proof_index) != expected_ids or set(parity_index) != expected_ids:
        raise SystemExit("WP4 theorem coverage mismatch")
    for theorem_id in sorted(expected_ids):
        inherited = wp1_index[theorem_id]
        current = proof_index[theorem_id]
        parity_row = parity_index[theorem_id]
        for key in ("canonical_name", "formal_signature", "statement_sha256", "requires", "conditional", "lean_symbol", "coq_symbol"):
            if current[key] != inherited[key]:
                raise SystemExit(f"WP4 theorem identity mutation: {theorem_id}:{key}")
        if parity_row["formal_signature"] != inherited["formal_signature"]:
            raise SystemExit("WP4 parity signature mutation: " + theorem_id)
        if parity_row["statement_sha256"] != inherited["statement_sha256"]:
            raise SystemExit("WP4 parity statement hash mutation: " + theorem_id)
        if parity_row["dependency_ids"] != inherited["requires"]:
            raise SystemExit("WP4 parity dependency mutation: " + theorem_id)
        if parity_row["conditional"] is not inherited["conditional"]:
            raise SystemExit("WP4 parity conditionality mutation: " + theorem_id)

    fixture_manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json")
    if len(fixture_manifest["fixtures"]) != 12:
        raise SystemExit("WP4 fixture count mutation")
    for item in fixture_manifest["fixtures"]:
        fixture = load(item["path"])
        validate(fixture, "schemas/v1.4.0/gate3_cluster_b_wp4_fixture.schema.json")

def verify_ledgers() -> None:
    if not CANONICAL_LEDGER.is_file() or not SUCCESSOR_LEDGER.is_file():
        raise SystemExit("missing canonical or successor WP4 ledger")
    canonical = parse_ledger(CANONICAL_LEDGER)
    successor = parse_ledger(SUCCESSOR_LEDGER)
    if set(canonical) & set(successor) != set(CONTROLLED):
        raise SystemExit("unexpected WP4 canonical/successor ledger overlap")

    historical_ledger = git_bytes("show", f"{MERGE}:release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt")
    if CANONICAL_LEDGER.read_bytes() != historical_ledger:
        raise SystemExit("canonical WP4 SHA-256 ledger was modified")

    for rel, old_hash in canonical.items():
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit("canonical WP4 path missing: " + rel)
        expected = successor.get(rel, old_hash)
        if digest(path) != expected:
            raise SystemExit("WP4 canonical/successor hash mismatch: " + rel)

    for rel, expected in successor.items():
        path = ROOT / rel
        if not path.is_file() or digest(path) != expected:
            raise SystemExit("WP4 successor hash mismatch: " + rel)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    verify_records()
    verify_ledgers()
    print("WP4 BUILD: PASS (post-merge successor compatible)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
