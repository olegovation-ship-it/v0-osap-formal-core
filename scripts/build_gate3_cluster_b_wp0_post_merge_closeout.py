#!/usr/bin/env python3
"""Build WP0 post-merge closeout records and their SHA-256 ledger."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MERGE = "46c02d96c047e70fe0d54feb60a0aadce2de95c7"
DEV = "v1.4.0-development"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
R = ROOT / "release/v1.4.0"
EVIDENCE = R / "GATE3_CLUSTER_B_WP0_POST_MERGE_HOSTED_CI_EVIDENCE.json"
CLOSEOUT = R / "GATE3_CLUSTER_B_WP0_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json"
SYNC = R / "GATE3_CLUSTER_B_WP0_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json"
LEDGER = R / "GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt"

PATCH_FILES = [
    ".github/workflows/gate3-cluster-b-wp0-post-merge-closeout.yml",
    "docs/gate3/cluster_b/WP0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md",
    "release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP0_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_HOSTED_CI_EVIDENCE.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_CLOSEOUT_GATES.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json",
    "release/v1.4.0/tools/patch_wp0_post_merge_allowlist.py",
    "schemas/v1.4.0/gate3_cluster_b_wp0_post_merge_archival_closeout_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp0_development_branch_synchronization_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp0_post_merge_hosted_ci_evidence.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp0_post_merge_frozen_upstream_preservation_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp0_post_merge_closeout_gates.schema.json",
    "scripts/build_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/capture_gate3_cluster_b_wp0_post_merge_evidence.py",
    "scripts/synchronize_v1_4_0_development.sh",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0.py",
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_git(*args: str, allow_missing: bool = False) -> str | None:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True
    )
    if completed.returncode:
        if allow_missing:
            return None
        raise SystemExit(
            "ERROR: git command failed: git "
            + " ".join(args)
            + "\n"
            + completed.stderr
        )
    return completed.stdout.strip()


def is_ancestor(older: str, newer: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", older, newer],
        cwd=ROOT,
        capture_output=True,
    ).returncode == 0


def branch_relation(main_sha: str | None, dev_sha: str | None) -> str:
    if not main_sha or not dev_sha:
        return "PENDING_REF_CAPTURE"
    if main_sha == dev_sha:
        return "SYNCHRONIZED_TO_CURRENT_MAIN"
    if is_ancestor(main_sha, dev_sha):
        return "DEVELOPMENT_AHEAD_WITH_CLOSEOUT_PATCH"
    if is_ancestor(dev_sha, main_sha):
        return "FAST_FORWARD_AVAILABLE"
    return "DIVERGED"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def update_ledger() -> None:
    rows: list[str] = []
    for rel in PATCH_FILES:
        path = ROOT / rel
        if not path.is_file():
            raise SystemExit(f"ERROR: patch file missing: {rel}")
        rows.append(f"{sha256(path)}  {rel}")
    LEDGER.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    if not (ROOT / ".git").exists():
        raise SystemExit("ERROR: run inside the repository after applying the overlay")

    evidence = load(EVIDENCE)
    if evidence.get("evidence_state") != "AUTHENTIC_GITHUB_API_EVIDENCE_RECORDED":
        raise SystemExit("ERROR: hosted CI evidence is not authenticated")
    if evidence.get("merge_commit") != MERGE:
        raise SystemExit("ERROR: hosted CI evidence merge pin mismatch")

    head = run_git("rev-parse", "HEAD")
    assert isinstance(head, str)
    if not is_ancestor(MERGE, head):
        raise SystemExit("ERROR: current HEAD does not contain the WP0 merge commit")

    tag_target = run_git("rev-parse", "refs/tags/v1.3.0^{}")
    if tag_target != TAG_TARGET:
        raise SystemExit(f"ERROR: v1.3.0 tag target mismatch: {tag_target}")

    origin_main = run_git("rev-parse", "refs/remotes/origin/main", allow_missing=True)
    origin_dev = run_git(
        "rev-parse", f"refs/remotes/origin/{DEV}", allow_missing=True
    )
    relation = branch_relation(origin_main, origin_dev)
    if relation == "DIVERGED":
        raise SystemExit("ERROR: development branch diverged; force updates are prohibited")

    closeout = load(CLOSEOUT)
    closeout["observed_main_tip"] = origin_main or MERGE
    closeout["observed_development_tip"] = origin_dev or MERGE
    if relation != "PENDING_REF_CAPTURE":
        closeout["branch_relation_at_capture"] = relation
    closeout["status"] = "POST_MERGE_CLOSEOUT_READY_FOR_PR"
    closeout["decision"] = "OPEN_WP0_POST_MERGE_CLOSEOUT_PR"
    CLOSEOUT.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")

    sync = load(SYNC)
    sync["current_main_tip"] = origin_main or MERGE
    sync["current_development_tip"] = origin_dev or MERGE
    if relation != "PENDING_REF_CAPTURE":
        sync["relation"] = relation
    if relation == "SYNCHRONIZED_TO_CURRENT_MAIN":
        sync.update(
            {
                "compare_status": "identical",
                "ahead_by": 0,
                "behind_by": 0,
                "status": "BASELINE_SYNCHRONIZATION_CONFIRMED",
            }
        )
    elif relation == "DEVELOPMENT_AHEAD_WITH_CLOSEOUT_PATCH":
        sync.update(
            {"compare_status": "ahead", "status": "FINAL_FAST_FORWARD_REQUIRED"}
        )
    elif relation == "FAST_FORWARD_AVAILABLE":
        sync.update(
            {"compare_status": "behind", "status": "FINAL_FAST_FORWARD_REQUIRED"}
        )
    SYNC.write_text(json.dumps(sync, indent=2) + "\n", encoding="utf-8")

    update_ledger()
    print(
        json.dumps(
            {
                "status": "PASS",
                "decision": closeout["decision"],
                "branch_relation": relation,
                "post_merge_ci": closeout["post_merge_ci"],
                "release_actions_authorized": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
