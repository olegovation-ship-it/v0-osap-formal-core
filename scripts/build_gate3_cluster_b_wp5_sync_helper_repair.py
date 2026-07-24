#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt"
INPUTS = ['release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/synchronize_v1_4_0_development_wp5.sh', '.github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml', 'docs/gate3/cluster_b/WP5_DEVELOPMENT_SYNCHRONIZATION_HELPER_GENERALIZATION_AND_REPLAY_REPAIR.md', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/00_identical_0_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/01_main_ahead_1_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/02_main_ahead_2_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/03_development_ahead_0_1_rejected.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/04_diverged_1_1_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_acceptance_gates.schema.json', 'scripts/classify_v1_4_0_development_sync_relation_wp5.py', 'scripts/replay_gate3_cluster_b_wp5_sync_helper_repair.py', 'scripts/build_gate3_cluster_b_wp5_sync_helper_repair.py', 'scripts/verify_gate3_cluster_b_wp5_sync_helper_repair.py', 'tests/test_gate3_cluster_b_wp5_sync_helper_repair.py']

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_json(path: Path) -> bool:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return path.read_text(encoding="utf-8") == json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

def expected() -> str:
    missing = [rel for rel in INPUTS if not (ROOT / rel).is_file()]
    if missing:
        raise SystemExit("missing WP5 synchronization repair inputs: " + ", ".join(missing))
    bad = [rel for rel in INPUTS if rel.endswith(".json") and not canonical_json(ROOT / rel)]
    if bad:
        raise SystemExit("non-canonical repair JSON: " + ", ".join(bad))
    return "".join(f"{digest(ROOT / rel)}  {rel}\n" for rel in sorted(INPUTS))

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    content = expected()
    if a.check:
        if not LEDGER.is_file() or LEDGER.read_text(encoding="utf-8") != content:
            raise SystemExit("WP5 synchronization repair SHA-256 ledger mismatch")
        print(f"WP5 SYNC HELPER REPAIR BUILD CHECK: PASS ({len(INPUTS)} hashed files)")
    else:
        LEDGER.write_text(content, encoding="utf-8", newline="\n")
        print(f"WP5 SYNC HELPER REPAIR LEDGER WRITTEN: {len(INPUTS)} files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
