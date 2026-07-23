#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = "c90041d3da5b680b574b910de50d8769d32fbfa9"
ACCEPTED = "633c01e33271ffb17c045f69aa266a595ebc7e74"
MERGE = "cdae3ea4e50f6222182f2398c350476fbe820f92"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
DEV = "v1.4.0-development"
CONTROLLED = ['release/v1.4.0/tools/patch_wp4_allowlist.py', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4.py']
NEW = ['.github/workflows/gate3-cluster-b-wp4-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp4_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp4_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp4_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp4_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp4.sh', 'scripts/verify_gate3_cluster_b_wp4_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp4_post_merge_closeout.py']
EXPECTED = set(CONTROLLED) | set(NEW)

def run(*args: str, check: bool = True, text: bool = True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=text, check=False)
    if check and cp.returncode:
        stderr = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise SystemExit(f"command failed: {' '.join(args)}\n{stderr}")
    return cp

def lines(*args: str) -> list[str]:
    return [row for row in run("git", *args).stdout.splitlines() if row]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_identity() -> None:
    for commit in (BASELINE, ACCEPTED, MERGE):
        run("git", "cat-file", "-e", commit + "^{commit}")
    parents = run("git", "show", "-s", "--format=%P", MERGE).stdout.strip().split()
    if parents != [BASELINE, ACCEPTED]:
        raise SystemExit("WP4 merge parent identity mismatch")
    if run("git", "rev-parse", MERGE + "^{tree}").stdout.strip() != run(
        "git", "rev-parse", ACCEPTED + "^{tree}"
    ).stdout.strip():
        raise SystemExit("WP4 merge and accepted-head trees differ")
    if run("git", "merge-base", "--is-ancestor", ACCEPTED, "HEAD", check=False).returncode:
        raise SystemExit("HEAD does not contain accepted WP4 head")

def verify_delta() -> None:
    changed = set(lines("diff", "--name-only", MERGE, "--"))
    changed.update(lines("ls-files", "--others", "--exclude-standard"))
    changed.discard("")
    if changed != EXPECTED:
        raise SystemExit(
            "FAIL_WP4_POST_MERGE_ALLOWLIST missing="
            + repr(sorted(EXPECTED - changed))
            + ", extra="
            + repr(sorted(changed - EXPECTED))
        )

    statuses: dict[str, str] = {}
    for row in lines("diff", "--name-status", MERGE, "--"):
        code, rel = row.split("\t", 1)
        statuses[rel] = code
    for rel in lines("ls-files", "--others", "--exclude-standard"):
        statuses[rel] = "A"
    for rel in CONTROLLED:
        if statuses.get(rel) != "M":
            raise SystemExit("controlled successor path status mismatch: " + rel)
    for rel in NEW:
        if statuses.get(rel) != "A":
            raise SystemExit("additive closeout path status mismatch: " + rel)

    for rel in lines("ls-tree", "-r", "--name-only", MERGE):
        current = ROOT / rel
        if not current.is_file():
            raise SystemExit("merge-baseline path missing: " + rel)
        if rel in CONTROLLED:
            continue
        historical = run("git", "show", f"{MERGE}:{rel}", text=False).stdout
        if current.read_bytes() != historical:
            raise SystemExit("frozen merge-baseline path modified: " + rel)

    immutable_prefixes = (
        "release/v1.4.0/GATE3_CLUSTER_B_WP0_",
        "release/v1.4.0/GATE3_CLUSTER_B_WP1_",
        "release/v1.4.0/GATE3_CLUSTER_B_WP2_",
        "release/v1.4.0/GATE3_CLUSTER_B_WP3_",
    )
    if any(rel.startswith(immutable_prefixes) for rel in changed):
        raise SystemExit("frozen WP0-WP3 release path changed")
    canonical_wp4 = {
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_ACCEPTANCE_GATES.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_BASELINE_LOCK.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_PRESERVATION_FIREWALL.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_SCHEMA_BUNDLE_MANIFEST.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json",
    }
    if changed & canonical_wp4:
        raise SystemExit("canonical WP4 record or ledger changed: " + repr(sorted(changed & canonical_wp4)))

def main() -> int:
    verify_identity()
    verify_delta()
    tag = run("git", "rev-parse", "refs/tags/v1.3.0^{}").stdout.strip()
    if tag != TAG_TARGET:
        raise SystemExit("stable v1.3.0 tag target changed")
    print("WP4 POST-MERGE EXACT CHANGED-PATH ALLOWLIST: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
