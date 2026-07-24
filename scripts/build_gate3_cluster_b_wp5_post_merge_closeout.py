#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPAIR_BASELINE = "e5724fc394b2fbb26d8926b5670b8fd41a62a71c"
LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt"
REPAIR_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt"
REPAIR_CONTROLLED = ['release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/synchronize_v1_4_0_development_wp5.sh']
INPUTS = ['release/v1.4.0/tools/patch_wp5_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py', '.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp5_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp5.sh', 'scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp5_post_merge_closeout.py']

def run(*args: str, text: bool = True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=text, check=False)
    if cp.returncode:
        err = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise SystemExit(err)
    return cp

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ledger(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            sha256, rel = line.split("  ", 1)
            out[rel] = sha256
    return out

def canonical_json(path: Path) -> bool:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8") == json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

def check() -> None:
    ledger_rel = str(LEDGER.relative_to(ROOT))
    if LEDGER.read_bytes() != run("git", "show", REPAIR_BASELINE + ":" + ledger_rel, text=False).stdout:
        raise SystemExit("frozen WP5 post-merge SHA-256 ledger modified")
    post = ledger(LEDGER)
    repair = ledger(REPAIR_LEDGER)
    if set(post) & set(repair) != set(REPAIR_CONTROLLED):
        raise SystemExit("unexpected post-merge/repair overlap")
    for rel in INPUTS:
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit("missing WP5 post-merge closeout input: " + rel)
        if rel.endswith(".json") and not canonical_json(path):
            raise SystemExit("non-canonical JSON: " + rel)
        expected = repair.get(rel, post.get(rel))
        if expected is None or digest(path) != expected:
            raise SystemExit("WP5 post-merge effective digest mismatch: " + rel)
    for rel, sha256 in repair.items():
        path = ROOT / rel
        if not path.is_file() or digest(path) != sha256:
            raise SystemExit("WP5 repair successor digest mismatch: " + rel)

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    if not a.check:
        raise SystemExit("WP5 post-merge ledger is frozen; regeneration is disabled")
    check()
    print(f"WP5 POST-MERGE BUILD CHECK: PASS ({len(INPUTS)} frozen inputs, repair overlay active)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
