#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = "7b497f197652874164e00fe9c0ef7f67e760c979"
ACCEPTED = "1c16ffb529b7e9a43c16739de26ad185c2f4b74c"
MERGE = "adda93cae34d6579e8b715d4107ff7f62a6f9c6b"
REPAIR_BASELINE = "e5724fc394b2fbb26d8926b5670b8fd41a62a71c"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
POST_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt"
REPAIR_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt"
CONTROLLED = ["release/v1.4.0/tools/patch_wp5_allowlist.py", "scripts/build_gate3_cluster_b_wp5.py", "scripts/verify_gate3_cluster_b_wp5.py"]
POST_NEW = ['.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp5_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp5.sh', 'scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp5_post_merge_closeout.py']
REPAIR_CONTROLLED = ['release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/synchronize_v1_4_0_development_wp5.sh']
REPAIR_NEW = ['.github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml', 'docs/gate3/cluster_b/WP5_DEVELOPMENT_SYNCHRONIZATION_HELPER_GENERALIZATION_AND_REPLAY_REPAIR.md', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/00_identical_0_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/01_main_ahead_1_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/02_main_ahead_2_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/03_development_ahead_0_1_rejected.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/04_diverged_1_1_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_acceptance_gates.schema.json', 'scripts/classify_v1_4_0_development_sync_relation_wp5.py', 'scripts/replay_gate3_cluster_b_wp5_sync_helper_repair.py', 'scripts/build_gate3_cluster_b_wp5_sync_helper_repair.py', 'scripts/verify_gate3_cluster_b_wp5_sync_helper_repair.py', 'tests/test_gate3_cluster_b_wp5_sync_helper_repair.py']
EXPECTED = set(CONTROLLED) | set(POST_NEW) | set(REPAIR_NEW)

def run(*args: str, check: bool = True, text: bool = True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=text, check=False)
    if check and cp.returncode:
        err = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise SystemExit("command failed: " + " ".join(args) + "\n" + err)
    return cp

def lines(*args: str) -> list[str]:
    return [line for line in run("git", *args).stdout.splitlines() if line]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ledger(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            sha256, rel = line.split("  ", 1)
            out[rel] = sha256
    return out

def main() -> int:
    for commit in (BASELINE, ACCEPTED, MERGE, REPAIR_BASELINE):
        run("git", "cat-file", "-e", commit + "^{commit}")
    if run("git", "show", "-s", "--format=%P", MERGE).stdout.strip().split() != [BASELINE, ACCEPTED]:
        raise SystemExit("WP5 merge parent identity mismatch")
    if run("git", "rev-parse", MERGE + "^{tree}").stdout.strip() != run("git", "rev-parse", ACCEPTED + "^{tree}").stdout.strip():
        raise SystemExit("WP5 merge and accepted-head trees differ")

    changed = set(lines("diff", "--name-only", MERGE, "--"))
    changed.update(lines("ls-files", "--others", "--exclude-standard"))
    if changed != EXPECTED:
        raise SystemExit("FAIL_WP5_POST_MERGE_ALLOWLIST missing=" + repr(sorted(EXPECTED - changed)) + ", extra=" + repr(sorted(changed - EXPECTED)))

    statuses = {}
    for row in lines("diff", "--name-status", MERGE, "--"):
        code, rel = row.split("\t", 1)
        statuses[rel] = code
    for rel in lines("ls-files", "--others", "--exclude-standard"):
        statuses[rel] = "A"
    for rel in CONTROLLED:
        if statuses.get(rel) != "M":
            raise SystemExit("controlled post-merge path status mismatch: " + rel)
    for rel in POST_NEW + REPAIR_NEW:
        if statuses.get(rel) != "A":
            raise SystemExit("additive post-merge/repair path status mismatch: " + rel)

    repair = ledger(REPAIR_LEDGER)
    if set(ledger(POST_LEDGER)) & set(repair) != set(REPAIR_CONTROLLED):
        raise SystemExit("unexpected repair ledger overlap")
    for rel, sha256 in repair.items():
        path = ROOT / rel
        if not path.is_file() or digest(path) != sha256:
            raise SystemExit("repair successor digest mismatch: " + rel)

    if run("git", "rev-parse", "refs/tags/v1.3.0^{}").stdout.strip() != TAG_TARGET:
        raise SystemExit("stable tag target changed")
    print("WP5 POST-MERGE EXACT CHANGED-PATH ALLOWLIST: PASS (repair-successor compatible)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
