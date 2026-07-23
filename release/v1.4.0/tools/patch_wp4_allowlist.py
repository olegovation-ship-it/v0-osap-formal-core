#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = "c90041d3da5b680b574b910de50d8769d32fbfa9"
ACCEPTED = "633c01e33271ffb17c045f69aa266a595ebc7e74"
MERGE = "cdae3ea4e50f6222182f2398c350476fbe820f92"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
CANONICAL_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt"
SUCCESSOR_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt"
CONTROLLED = ['release/v1.4.0/tools/patch_wp4_allowlist.py', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4.py']
POST_MERGE_NEW = ['.github/workflows/gate3-cluster-b-wp4-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp4_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp4_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp4_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp4_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp4.sh', 'scripts/verify_gate3_cluster_b_wp4_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp4_post_merge_closeout.py']
SUCCESSOR_ATTESTED = ['.github/workflows/gate3-cluster-b-wp4-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp4_allowlist.py', 'release/v1.4.0/tools/patch_wp4_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp4_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/build_gate3_cluster_b_wp4_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp4_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp4.sh', 'scripts/verify_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp4_post_merge_closeout.py']
CANONICAL_LEDGER_REL = "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt"

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

def parse_ledger(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            value, rel = line.split("  ", 1)
            out[rel] = value
    return out

def git_file_exists(commit: str, rel: str) -> bool:
    return run("git", "cat-file", "-e", f"{commit}:{rel}", check=False).returncode == 0

def verify_commit_identity() -> None:
    run("git", "cat-file", "-e", BASELINE + "^{commit}")
    run("git", "cat-file", "-e", ACCEPTED + "^{commit}")
    run("git", "cat-file", "-e", MERGE + "^{commit}")
    parents = run("git", "show", "-s", "--format=%P", MERGE).stdout.strip().split()
    if parents != [BASELINE, ACCEPTED]:
        raise SystemExit("WP4 merge parent identity mismatch: " + repr(parents))
    merge_tree = run("git", "rev-parse", MERGE + "^{tree}").stdout.strip()
    accepted_tree = run("git", "rev-parse", ACCEPTED + "^{tree}").stdout.strip()
    if merge_tree != accepted_tree:
        raise SystemExit("WP4 merge tree differs from accepted head tree")
    if run("git", "merge-base", "--is-ancestor", ACCEPTED, "HEAD", check=False).returncode:
        raise SystemExit("HEAD does not contain accepted WP4 head")

def verify_ledgers() -> tuple[dict[str, str], dict[str, str]]:
    if not CANONICAL_LEDGER.is_file() or not SUCCESSOR_LEDGER.is_file():
        raise SystemExit("missing WP4 canonical or successor ledger")
    canonical = parse_ledger(CANONICAL_LEDGER)
    successor = parse_ledger(SUCCESSOR_LEDGER)
    if set(successor) != set(SUCCESSOR_ATTESTED):
        raise SystemExit(
            "WP4 successor ledger path set mismatch: missing="
            + repr(sorted(set(SUCCESSOR_ATTESTED) - set(successor)))
            + ", extra="
            + repr(sorted(set(successor) - set(SUCCESSOR_ATTESTED)))
        )
    if set(canonical) & set(successor) != set(CONTROLLED):
        raise SystemExit("unexpected canonical/successor overlap")
    historical_ledger = run(
        "git", "show", f"{MERGE}:{CANONICAL_LEDGER_REL}", text=False
    ).stdout
    if CANONICAL_LEDGER.read_bytes() != historical_ledger:
        raise SystemExit("canonical WP4 ledger modified")
    for rel, historical_hash in canonical.items():
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit("missing canonical WP4 path: " + rel)
        expected_hash = successor.get(rel, historical_hash)
        if digest(path) != expected_hash:
            raise SystemExit("canonical/successor WP4 hash mismatch: " + rel)
    for rel, expected_hash in successor.items():
        path = ROOT / rel
        if not path.is_file() or digest(path) != expected_hash:
            raise SystemExit("WP4 successor hash mismatch: " + rel)
    return canonical, successor

def verify_delta(canonical: dict[str, str]) -> None:
    expected = set(canonical) | {CANONICAL_LEDGER_REL} | set(POST_MERGE_NEW)
    changed = set(lines("diff", "--name-only", BASELINE, "--"))
    changed.update(lines("ls-files", "--others", "--exclude-standard"))
    changed.discard("")
    if changed != expected:
        raise SystemExit(
            "FAIL_WP4_ALLOWLIST missing="
            + repr(sorted(expected - changed))
            + ", extra="
            + repr(sorted(changed - expected))
        )

    statuses: dict[str, str] = {}
    for row in lines("diff", "--name-status", BASELINE, "--"):
        code, rel = row.split("\t", 1)
        statuses[rel] = code
    for rel in lines("ls-files", "--others", "--exclude-standard"):
        statuses[rel] = "A"
    for rel in sorted(expected):
        expected_code = "M" if git_file_exists(BASELINE, rel) else "A"
        if statuses.get(rel) != expected_code:
            raise SystemExit(
                f"WP4 path status mismatch: {rel}: {statuses.get(rel)!r}; expected {expected_code}"
            )

    for rel in lines("ls-tree", "-r", "--name-only", BASELINE):
        current = ROOT / rel
        if not current.is_file():
            raise SystemExit("missing frozen baseline path: " + rel)
        historical = run("git", "show", f"{BASELINE}:{rel}", text=False).stdout
        if rel in canonical:
            if digest(current) != canonical.get(rel, ""):
                raise SystemExit("accepted WP4 replacement hash mismatch: " + rel)
        elif current.read_bytes() != historical:
            raise SystemExit("modified frozen baseline path: " + rel)

    forbidden_prefixes = (
        "release/v1.4.0/GATE3_CLUSTER_B_WP0_",
        "release/v1.4.0/GATE3_CLUSTER_B_WP1_",
        "release/v1.4.0/GATE3_CLUSTER_B_WP2_",
        "release/v1.4.0/GATE3_CLUSTER_B_WP3_",
        "docs/gate3/cluster_b/WP0_",
        "docs/gate3/cluster_b/WP1_",
        "docs/gate3/cluster_b/WP2_",
        "docs/gate3/cluster_b/WP3_",
    )
    if any(path.startswith(forbidden_prefixes) for path in changed):
        raise SystemExit("frozen WP0-WP3 path changed")

def main() -> int:
    verify_commit_identity()
    canonical, _ = verify_ledgers()
    verify_delta(canonical)
    tag = run("git", "rev-parse", "refs/tags/v1.3.0^{}").stdout.strip()
    if tag != TAG_TARGET:
        raise SystemExit("stable v1.3.0 tag target changed")
    print("WP4 EXACT CHANGED-PATH ALLOWLIST: PASS (post-merge successor compatible)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
