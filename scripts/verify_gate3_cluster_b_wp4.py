#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    if check and cp.returncode:
        raise SystemExit(f"command failed: {' '.join(args)}\n{cp.stdout}{cp.stderr}")
    return cp

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def validate(obj, schema_rel: str) -> None:
    errors = sorted(Draft202012Validator(load(schema_rel)).iter_errors(obj), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f"schema failure {schema_rel}: {errors[0].message}")

def module():
    path = ROOT / "checker/v0_osap_fc1/cluster_b_wp4.py"
    spec = importlib.util.spec_from_file_location("cluster_b_wp4", path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load WP4 activation module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def apply_delta(manifest: dict, delta: dict) -> dict:
    out = copy.deepcopy(manifest)
    index = {row["theorem_id"]: row for row in out["theorems"]}
    for theorem_id, changes in delta.items():
        if theorem_id not in index:
            raise SystemExit("fixture delta theorem unknown")
        for key, value in changes.items():
            if isinstance(value, dict) and isinstance(index[theorem_id].get(key), dict):
                index[theorem_id][key].update(value)
            else:
                index[theorem_id][key] = value
    return out

def verify_source_symbols() -> None:
    registry = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json")
    lean = (ROOT / "lean/V0OSAP/ClusterB.lean").read_text(encoding="utf-8")
    coq = (ROOT / "coq/theories/ClusterB.v").read_text(encoding="utf-8")
    for row in registry["records"]:
        theorem_id = row["theorem_id"]
        lean_name = row["lean_symbol"].split(".")[-1]
        coq_name = row["coq_symbol"]
        if len(re.findall(r"\btheorem\s+" + re.escape(lean_name) + r"\b", lean)) != 1:
            raise SystemExit("Lean symbol coverage failure: " + theorem_id)
        if len(re.findall(r"\bTheorem\s+" + re.escape(coq_name) + r"\b", coq)) != 1:
            raise SystemExit("Coq symbol coverage failure: " + theorem_id)
    if re.search(r"\b(sorry|admit)\b", lean):
        raise SystemExit("Lean proof-hole marker detected")
    if re.search(r"\b(Admitted|admit)\b", coq):
        raise SystemExit("Coq proof-hole marker detected")

def verify_records() -> None:
    pairs = [
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_BASELINE_LOCK.json", "schemas/v1.4.0/gate3_cluster_b_wp4_baseline_lock.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_proof_manifest.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_parity_manifest.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_fixture_manifest.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_PRESERVATION_FIREWALL.json", "schemas/v1.4.0/gate3_cluster_b_wp4_preservation_firewall.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_ACCEPTANCE_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp4_acceptance_gates.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP4_SCHEMA_BUNDLE_MANIFEST.json", "schemas/v1.4.0/gate3_cluster_b_wp4_schema_bundle_manifest.schema.json"),
    ]
    for record_rel, schema_rel in pairs:
        validate(load(record_rel), schema_rel)

    wp1 = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json")
    proof = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json")
    parity = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json")
    inherited = {row["theorem_id"]: row for row in wp1["records"]}
    current = {row["theorem_id"]: row for row in proof["theorems"]}
    if set(inherited) != set(current) or set(current) != {f"T{i}" for i in range(157, 163)}:
        raise SystemExit("WP4 theorem identity coverage mismatch")
    for theorem_id in sorted(inherited):
        for key in ("canonical_name", "formal_signature", "statement_sha256", "requires", "conditional", "lean_symbol", "coq_symbol"):
            if current[theorem_id][key] != inherited[theorem_id][key]:
                raise SystemExit(f"WP1 theorem identity mutation: {theorem_id}:{key}")
    if parity["coverage_percent"] != 100 or any(row["parity_status"] != "PASS" for row in parity["records"]):
        raise SystemExit("statement parity incomplete")

def verify_fixtures() -> None:
    mod = module()
    proof_manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json")
    fixture_manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json")
    if len(fixture_manifest["fixtures"]) != 12:
        raise SystemExit("WP4 fixture count mismatch")
    for item in fixture_manifest["fixtures"]:
        fixture = load(item["path"])
        validate(fixture, "schemas/v1.4.0/gate3_cluster_b_wp4_fixture.schema.json")
        proof = apply_delta(proof_manifest, fixture["proof_manifest_delta"])
        first = mod.activate_wp3_binding(fixture["binding"], proof)
        second = mod.activate_wp3_binding(fixture["binding"], proof)
        if first != second:
            raise SystemExit("nondeterministic activation: " + fixture["fixture_id"])
        validate(first, "schemas/v1.4.0/gate3_cluster_b_wp4_activation_result.schema.json")
        for key, value in fixture["expected"].items():
            if first.get(key) != value:
                raise SystemExit(f"fixture {fixture['fixture_id']} mismatch {key}")
        if first["frozen_wp3_binding_modified"] or first["frozen_ipec_v0_1_modified"] or first["release_action_authorized"]:
            raise SystemExit("activation boundary violated")

def main() -> int:
    run(sys.executable, "release/v1.4.0/tools/patch_wp4_allowlist.py", "--check")
    verify_source_symbols()
    verify_records()
    verify_fixtures()
    cp = run(sys.executable, "scripts/build_gate3_cluster_b_wp4.py", "--check", check=False)
    if cp.returncode:
        raise SystemExit(cp.stdout + cp.stderr)
    print("WP4 VERIFICATION: PASS (post-merge successor compatible)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
