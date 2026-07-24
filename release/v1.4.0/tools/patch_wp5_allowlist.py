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
CANONICAL_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt"
POST_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt"
REPAIR_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt"
CANONICAL_PATHS = ['.github/workflows/gate3-cluster-b-wp5.yml', 'docs/gate3/cluster_b/WP5_BUILD_SPECIFICATION.md', 'docs/gate3/cluster_b/WP5_CI_INTEGRATION_AND_DETERMINISTIC_EVIDENCE_MANIFESTS.md', 'fixtures/gate3/cluster_b/wp5/01_valid_canonical_evidence.json', 'fixtures/gate3/cluster_b/wp5/02_unordered_evidence_paths_rejected.json', 'fixtures/gate3/cluster_b/wp5/03_duplicate_evidence_path_rejected.json', 'fixtures/gate3/cluster_b/wp5/04_sha256_mismatch_rejected.json', 'fixtures/gate3/cluster_b/wp5/05_predecessor_chain_break_rejected.json', 'fixtures/gate3/cluster_b/wp5/06_release_action_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_build_spec_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_acceptance_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_baseline_lock.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_ci_job_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_input_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_preservation_firewall.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_replay_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/replay_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5_build_spec.py', 'tests/test_gate3_cluster_b_wp5.py', 'tests/test_gate3_cluster_b_wp5_build_spec.py']
POST_MERGE_NEW = ['.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp5_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp5.sh', 'scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp5_post_merge_closeout.py']
REPAIR_CONTROLLED = ['release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/synchronize_v1_4_0_development_wp5.sh']
REPAIR_NEW = ['.github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml', 'docs/gate3/cluster_b/WP5_DEVELOPMENT_SYNCHRONIZATION_HELPER_GENERALIZATION_AND_REPLAY_REPAIR.md', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/00_identical_0_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/01_main_ahead_1_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/02_main_ahead_2_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/03_development_ahead_0_1_rejected.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/04_diverged_1_1_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_acceptance_gates.schema.json', 'scripts/classify_v1_4_0_development_sync_relation_wp5.py', 'scripts/replay_gate3_cluster_b_wp5_sync_helper_repair.py', 'scripts/build_gate3_cluster_b_wp5_sync_helper_repair.py', 'scripts/verify_gate3_cluster_b_wp5_sync_helper_repair.py', 'tests/test_gate3_cluster_b_wp5_sync_helper_repair.py']

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
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            sha256, rel = line.split("  ", 1)
            result[rel] = sha256
    return result

def main() -> int:
    for commit in (BASELINE, ACCEPTED, MERGE, REPAIR_BASELINE):
        run("git", "cat-file", "-e", commit + "^{commit}")
    if run("git", "show", "-s", "--format=%P", MERGE).stdout.strip().split() != [BASELINE, ACCEPTED]:
        raise SystemExit("WP5 merge parent identity mismatch")
    if run("git", "rev-parse", MERGE + "^{tree}").stdout.strip() != run("git", "rev-parse", ACCEPTED + "^{tree}").stdout.strip():
        raise SystemExit("WP5 merge tree differs from accepted head tree")

    expected = set(CANONICAL_PATHS) | set(POST_MERGE_NEW) | set(REPAIR_NEW)
    changed = set(lines("diff", "--name-only", BASELINE, "--"))
    changed.update(lines("ls-files", "--others", "--exclude-standard"))
    if changed != expected:
        raise SystemExit("FAIL_WP5_ALLOWLIST missing=" + repr(sorted(expected - changed)) + ", extra=" + repr(sorted(changed - expected)))

    canonical_rel = str(CANONICAL_LEDGER.relative_to(ROOT))
    post_rel = str(POST_LEDGER.relative_to(ROOT))
    if CANONICAL_LEDGER.read_bytes() != run("git", "show", MERGE + ":" + canonical_rel, text=False).stdout:
        raise SystemExit("canonical WP5 ledger modified")
    if POST_LEDGER.read_bytes() != run("git", "show", REPAIR_BASELINE + ":" + post_rel, text=False).stdout:
        raise SystemExit("frozen WP5 post-merge ledger modified")

    canonical = ledger(CANONICAL_LEDGER)
    post = ledger(POST_LEDGER)
    repair = ledger(REPAIR_LEDGER)
    if set(post) & set(repair) != set(REPAIR_CONTROLLED):
        raise SystemExit("unexpected WP5 repair overlap with post-merge ledger")

    effective = dict(canonical)
    effective.update(post)
    effective.update(repair)
    for rel, sha256 in effective.items():
        path = ROOT / rel
        if not path.is_file() or digest(path) != sha256:
            raise SystemExit("WP5 effective successor digest mismatch: " + rel)

    if run("git", "rev-parse", "refs/tags/v1.3.0^{}").stdout.strip() != TAG_TARGET:
        raise SystemExit("stable v1.3.0 tag target changed")
    print("WP5 EXACT CHANGED-PATH ALLOWLIST: PASS (repair-successor compatible)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
