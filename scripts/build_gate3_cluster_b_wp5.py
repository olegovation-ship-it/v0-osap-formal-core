#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MERGE = "adda93cae34d6579e8b715d4107ff7f62a6f9c6b"
REPAIR_BASELINE = "e5724fc394b2fbb26d8926b5670b8fd41a62a71c"
CANONICAL = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt"
POST = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt"
REPAIR = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt"
REPAIR_CONTROLLED = ['release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/synchronize_v1_4_0_development_wp5.sh']
PAIRS = [
("release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json","schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json"),
("release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json","schemas/v1.4.0/gate3_cluster_b_wp5_baseline_lock.schema.json"),
("release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json","schemas/v1.4.0/gate3_cluster_b_wp5_ci_job_matrix.schema.json"),
("release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json","schemas/v1.4.0/gate3_cluster_b_wp5_evidence_input_manifest.schema.json"),
("release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json","schemas/v1.4.0/gate3_cluster_b_wp5_fixture_manifest.schema.json"),
("release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json","schemas/v1.4.0/gate3_cluster_b_wp5_preservation_firewall.schema.json"),
("release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json","schemas/v1.4.0/gate3_cluster_b_wp5_replay_record.schema.json"),
("release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json","schemas/v1.4.0/gate3_cluster_b_wp5_acceptance_gates.schema.json"),
("release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json","schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json")]

def run(*args: str, text: bool = True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=text, check=False)
    if cp.returncode:
        err = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise SystemExit(err)
    return cp

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ledger(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            sha256, rel = line.split("  ", 1)
            out[rel] = sha256
    return out

def check() -> None:
    canonical_rel = str(CANONICAL.relative_to(ROOT))
    post_rel = str(POST.relative_to(ROOT))
    if CANONICAL.read_bytes() != run("git", "show", MERGE + ":" + canonical_rel, text=False).stdout:
        raise SystemExit("canonical WP5 ledger modified")
    if POST.read_bytes() != run("git", "show", REPAIR_BASELINE + ":" + post_rel, text=False).stdout:
        raise SystemExit("frozen WP5 post-merge ledger modified")

    canonical = ledger(CANONICAL)
    post = ledger(POST)
    repair = ledger(REPAIR)
    if set(post) & set(repair) != set(REPAIR_CONTROLLED):
        raise SystemExit("unexpected canonical/post/repair successor overlap")
    effective = dict(canonical)
    effective.update(post)
    effective.update(repair)
    for rel, sha256 in effective.items():
        path = ROOT / rel
        if not path.is_file() or digest(path) != sha256:
            raise SystemExit("WP5 effective successor digest mismatch " + rel)

    for document, schema in PAIRS:
        errors = sorted(Draft202012Validator(load(schema)).iter_errors(load(document)), key=lambda e: list(e.path))
        if errors:
            raise SystemExit("schema failure " + document + ": " + errors[0].message)
    if load("release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json")["byte_identical"] is not True:
        raise SystemExit("WP5 deterministic replay record failure")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.parse_args()
    check()
    print("WP5 BUILD: PASS (repair-successor compatible)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
