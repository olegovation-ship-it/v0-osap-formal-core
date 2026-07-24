#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = "e5724fc394b2fbb26d8926b5670b8fd41a62a71c"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
CONTROLLED = ['release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py', 'scripts/synchronize_v1_4_0_development_wp5.sh']
ADDITIVE = ['.github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml', 'docs/gate3/cluster_b/WP5_DEVELOPMENT_SYNCHRONIZATION_HELPER_GENERALIZATION_AND_REPLAY_REPAIR.md', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/00_identical_0_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/01_main_ahead_1_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/02_main_ahead_2_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/03_development_ahead_0_1_rejected.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/04_diverged_1_1_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_acceptance_gates.schema.json', 'scripts/classify_v1_4_0_development_sync_relation_wp5.py', 'scripts/replay_gate3_cluster_b_wp5_sync_helper_repair.py', 'scripts/build_gate3_cluster_b_wp5_sync_helper_repair.py', 'scripts/verify_gate3_cluster_b_wp5_sync_helper_repair.py', 'tests/test_gate3_cluster_b_wp5_sync_helper_repair.py']
EXPECTED = set(CONTROLLED) | set(ADDITIVE)
FORBIDDEN_PREFIXES = ("checker/","lean/","coq/","release/v1.4.0/GATE3_CLUSTER_B_WP0_","release/v1.4.0/GATE3_CLUSTER_B_WP1_","release/v1.4.0/GATE3_CLUSTER_B_WP2_","release/v1.4.0/GATE3_CLUSTER_B_WP3_","release/v1.4.0/GATE3_CLUSTER_B_WP4_")

def run(*args: str, check: bool = True, text: bool = True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=text, check=False)
    if check and cp.returncode:
        err = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise SystemExit("command failed: " + " ".join(args) + "\n" + err)
    return cp

def lines(*args: str) -> list[str]:
    return [line for line in run("git", *args).stdout.splitlines() if line]

def main() -> int:
    run("git", "cat-file", "-e", BASELINE + "^{commit}")
    if run("git", "merge-base", "--is-ancestor", BASELINE, "HEAD", check=False).returncode:
        raise SystemExit("repair baseline is not an ancestor of HEAD")
    changed = set(lines("diff", "--name-only", BASELINE, "--"))
    changed.update(lines("ls-files", "--others", "--exclude-standard"))
    if changed != EXPECTED:
        raise SystemExit("WP5 SYNC HELPER REPAIR ALLOWLIST mismatch missing=" + repr(sorted(EXPECTED - changed)) + " extra=" + repr(sorted(changed - EXPECTED)))
    statuses = {}
    for row in lines("diff", "--name-status", BASELINE, "--"):
        code, rel = row.split("\t", 1)
        statuses[rel] = code
    for rel in lines("ls-files", "--others", "--exclude-standard"):
        statuses[rel] = "A"
    for rel in CONTROLLED:
        if statuses.get(rel) != "M":
            raise SystemExit("controlled repair path must be modified: " + rel)
    for rel in ADDITIVE:
        if statuses.get(rel) != "A":
            raise SystemExit("repair artifact path must be additive: " + rel)
    bad = [rel for rel in changed if rel.startswith(FORBIDDEN_PREFIXES)]
    if bad:
        raise SystemExit("frozen semantic/proof path changed: " + repr(sorted(bad)))
    for rel in lines("ls-tree", "-r", "--name-only", BASELINE):
        if rel in CONTROLLED:
            continue
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit("baseline path missing: " + rel)
        if path.read_bytes() != run("git", "show", BASELINE + ":" + rel, text=False).stdout:
            raise SystemExit("frozen baseline path modified: " + rel)
    helper = (ROOT / "scripts/synchronize_v1_4_0_development_wp5.sh").read_text(encoding="utf-8")
    for token in ("--force","force-with-lease","reset --hard","git rebase","branch -D","git tag","gh release","zenodo"):
        if token in helper:
            raise SystemExit("forbidden synchronization token: " + token)
    for token in ("git merge-base --is-ancestor","git merge --ff-only origin/main","git push origin v1.4.0-development","classify_v1_4_0_development_sync_relation_wp5.py"):
        if token not in helper:
            raise SystemExit("missing synchronization safety token: " + token)
    if run("git", "rev-parse", "refs/tags/v1.3.0^{}").stdout.strip() != TAG_TARGET:
        raise SystemExit("stable v1.3.0 tag target changed")
    print("WP5 SYNC HELPER REPAIR EXACT CHANGED-PATH ALLOWLIST: PASS (27 paths)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
