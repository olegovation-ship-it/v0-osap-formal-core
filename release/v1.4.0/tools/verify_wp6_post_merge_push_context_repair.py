#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASELINE = "ba32d8e855a79461fdcda14740acab86aafcb17a"
CANONICAL_MAIN = "47614ce7891f4895e003cb85e7651b7d043a963d"
FROZEN_LEDGER_ANCHOR = "ba32d8e855a79461fdcda14740acab86aafcb17a"
WP5_HISTORICAL_REPLAY_ANCHOR = "e5724fc394b2fbb26d8926b5670b8fd41a62a71c"
WP6_CANONICAL_LEDGER_ANCHOR = "8a692859b2e02a8c9fccc008f76bb24218716f40"
POST_MERGE_ORIGIN_MAIN = "47614ce7891f4895e003cb85e7651b7d043a963d"
POST_MERGE_ORIGIN_DEVELOPMENT = "ba32d8e855a79461fdcda14740acab86aafcb17a"

OLD = (
    "${{ github.event_name != 'pull_request' || "
    "github.event.pull_request.number != 33 }}"
)
NEW = (
    "${{ "
    "(github.event_name != 'pull_request' || "
    "github.event.pull_request.base.ref != 'main' || "
    "github.event.pull_request.head.ref != 'v1.4.0-development' || "
    "github.event.pull_request.head.repo.full_name != github.repository) "
    "&& "
    "(github.event_name != 'push' || "
    "github.ref != 'refs/heads/main') "
    "}}"
)

COUNTS = {
    ".github/workflows/gate3-cluster-b-wp6.yml": 10,
    ".github/workflows/python-checker.yml": 1,
    ".github/workflows/rc1-gate-audit.yml": 1,
    ".github/workflows/rc1-release-closure.yml": 3,
    ".github/workflows/rc1-release-evidence-closure.yml": 3,
    ".github/workflows/rc1-tag-authorization.yml": 3,
    ".github/workflows/release-readiness.yml": 2,
    ".github/workflows/v1-3-0-final-release-authorization.yml": 1,
    ".github/workflows/v1-3-0-final-release-evidence-closure.yml": 1,
    ".github/workflows/v1-3-0-post-merge-archival-closeout.yml": 1,
    ".github/workflows/v1-3-0-post-merge-legacy-lifecycle-compatibility.yml": 1,
    ".github/workflows/v1-3-0-post-merge-publication-lifecycle-replay-compatibility.yml": 1,
    ".github/workflows/v1-3-0-post-zenodo-historical-replay.yml": 1,
    ".github/workflows/v1-3-0-zenodo-publication-evidence-closure.yml": 1,
}

DEDICATED = (
    ".github/workflows/"
    "gate3-cluster-b-wp6-post-merge-closeout.yml"
)

LEGACY_BUILDER = (
    "scripts/build_gate3_cluster_b_wp6_post_merge_closeout.py"
)
LEGACY_VERIFIER = (
    "release/v1.4.0/tools/"
    "verify_wp6_post_merge_ci_context_repair.py"
)
LEGACY = sorted([
    LEGACY_BUILDER,
    LEGACY_VERIFIER,
])

SUCCESSOR_CONSUMERS = sorted([
    "scripts/build_gate3_cluster_b_wp2.py",
    "scripts/verify_gate3_cluster_b_wp2.py",
    "scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py",
    "scripts/build_gate3_cluster_b_wp6.py",
    "scripts/verify_gate3_cluster_b_wp6.py",
    (
        "scripts/"
        "verify_v1_3_0_post_merge_legacy_lifecycle_compatibility.py"
    ),
])
STEM = (
    "GATE3_CLUSTER_B_WP6_POST_MERGE_PUSH_CONTEXT_COMPATIBILITY_"
    "AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR"
)
DOC = (
    "docs/gate3/cluster_b/"
    "WP6_POST_MERGE_PUSH_CONTEXT_COMPATIBILITY_"
    "AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR.md"
)
RECORD = f"release/v1.4.0/{STEM}_RECORD.json"
MANIFEST = f"release/v1.4.0/{STEM}_MANIFEST.json"
LEDGER = f"release/v1.4.0/{STEM}_SHA256SUMS.txt"
VERIFIER = (
    "release/v1.4.0/tools/"
    "verify_wp6_post_merge_push_context_repair.py"
)
TEST = (
    "tests/"
    "test_gate3_cluster_b_wp6_post_merge_push_context_repair.py"
)

CONTROLLED = sorted([
    *COUNTS,
    DEDICATED,
    *LEGACY,
    *SUCCESSOR_CONSUMERS,
])
ADDITIVE = sorted([DOC, RECORD, MANIFEST, LEDGER, VERIFIER, TEST])
ALL_PATHS = sorted(CONTROLLED + ADDITIVE)



SUCCESSOR_POST_MERGE_CONSUMERS = [
    "scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py",
    "scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp6_post_merge_closeout.py",
]

CONTROLLED = sorted(
    set(CONTROLLED)
    | set(SUCCESSOR_POST_MERGE_CONSUMERS)
)
ALL_PATHS = sorted([*CONTROLLED, *ADDITIVE])

def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def git_text(*args: str) -> str:
    cp = run("git", *args)
    if cp.returncode:
        raise RuntimeError(cp.stdout + cp.stderr)
    return cp.stdout


def sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def status_entries() -> dict[str, str]:
    rows = {}
    output = git_text(
        "status", "--porcelain=v1", "--untracked-files=all"
    )
    for line in output.splitlines():
        if len(line) < 4 or " -> " in line:
            raise RuntimeError("invalid status entry: " + repr(line))
        rows[line[3:]] = line[:2]
    return rows


def committed_entries() -> dict[str, str]:
    rows = {}
    output = git_text(
        "diff", "--name-status", "--no-renames",
        BASELINE + "..HEAD",
    )
    for line in output.splitlines():
        if not line.strip():
            continue
        code, path = line.split("\t", 1)
        rows[path] = code
    return rows


def expected_dedicated() -> str:
    text = git_text("show", BASELINE + ":" + DEDICATED)

    a = text.index("  pull_request:\n")
    b = text.index("  workflow_dispatch:\n")
    pull = text[a:b]
    push = pull.replace("  pull_request:\n", "  push:\n", 1)
    text = text[:b] + push + text[b:]

    old_filter = (
        "      - 'release/v1.4.0/tools/"
        "verify_wp6_post_merge_ci_context_repair.py'\n"
    )
    text = text.replace(
        old_filter,
        old_filter
        + "      - 'release/v1.4.0/tools/"
        "verify_wp6_post_merge_push_context_repair.py'\n",
    )

    old_test = (
        "tests/test_gate3_cluster_b_wp6_post_merge_ci_context_repair.py"
    )
    text = text.replace(
        old_test,
        old_test + " "
        "tests/test_gate3_cluster_b_wp6_post_merge_"
        "push_context_repair.py",
        1,
    )

    old_step = (
        "verify_wp6_post_merge_ci_context_repair.py --ci"
    )
    text = text.replace(
        old_step,
        old_step + "\n"
        "      - run: python release/v1.4.0/tools/"
        "verify_wp6_post_merge_push_context_repair.py "
        "--mode committed",
        1,
    )
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("auto", "working-tree", "committed"),
        default="auto",
    )
    args = parser.parse_args()
    errors: list[str] = []

    mode = args.mode
    if mode == "auto":
        mode = "working-tree" if status_entries() else "committed"

    try:
        entries = (
            status_entries()
            if mode == "working-tree"
            else committed_entries()
        )
        if sorted(entries) != ALL_PATHS:
            errors.append(
                "path inventory mismatch; "
                f"missing={sorted(set(ALL_PATHS)-set(entries))!r}; "
                f"extra={sorted(set(entries)-set(ALL_PATHS))!r}"
            )

        for path in CONTROLLED:
            expected = " M" if mode == "working-tree" else "M"
            if entries.get(path) != expected:
                errors.append(
                    f"controlled status mismatch: {path}"
                )

        for path in ADDITIVE:
            expected = "??" if mode == "working-tree" else "A"
            if entries.get(path) != expected:
                errors.append(
                    f"additive status mismatch: {path}"
                )
    except Exception as exc:
        errors.append("surface failure: " + str(exc))

    try:
        total = 0
        for path, count in COUNTS.items():
            baseline = git_text("show", BASELINE + ":" + path)
            current = (ROOT / path).read_text(encoding="utf-8")
            if current != baseline.replace(OLD, NEW):
                errors.append("non-exact workflow mutation: " + path)
            if current.count(OLD) != 0:
                errors.append("old guard remains: " + path)
            if current.count(NEW) != count:
                errors.append("new guard count mismatch: " + path)
            total += current.count(NEW)

        if total != 30:
            errors.append(f"aggregate guard count mismatch: {total}")
    except Exception as exc:
        errors.append("guard validation failure: " + str(exc))

    try:
        current = (ROOT / DEDICATED).read_text(encoding="utf-8")
        if current != expected_dedicated():
            errors.append("dedicated workflow mutation is not exact")
        if "  push:\n    branches: [main]\n" not in current:
            errors.append("main push trigger missing")
        if "permissions:\n  contents: read\n" not in current:
            errors.append("read-only permissions changed")
    except Exception as exc:
        errors.append("dedicated workflow failure: " + str(exc))

    try:
        for path in SUCCESSOR_CONSUMERS:
            consumer_text = (
                ROOT / path
            ).read_text(encoding="utf-8")

            if FROZEN_LEDGER_ANCHOR not in consumer_text:
                errors.append(
                    "consumer frozen-ledger anchor missing: " + path
                )

            if "successor_overlay_attestation" not in consumer_text:
                errors.append(
                    "consumer repair-attestation helper missing: "
                    + path
                )
    except Exception as exc:
        errors.append(
            "successor consumer validation failure: " + str(exc)
        )

    try:
        record = json.loads((ROOT / RECORD).read_text())
        manifest = json.loads((ROOT / MANIFEST).read_text())
        if record.get("version") != "0.1":
            errors.append("record version mismatch")
        if record.get("status") != "PREPARED_UNCOMMITTED":
            errors.append("record status mismatch")
        if record.get("repair_policy", {}).get(
            "frozen_ledger_anchor_commit"
        ) != FROZEN_LEDGER_ANCHOR:
            errors.append("record frozen-ledger anchor mismatch")
        policy = record.get("repair_policy", {})
        if policy.get(
            "wp5_historical_replay_anchor_commit"
        ) != WP5_HISTORICAL_REPLAY_ANCHOR:
            errors.append("record WP5 historical anchor mismatch")
        if policy.get(
            "wp6_canonical_ledger_anchor_commit"
        ) != WP6_CANONICAL_LEDGER_ANCHOR:
            errors.append("record WP6 canonical anchor mismatch")
        if policy.get(
            "wp6_historical_allowlist_replay_anchor_commit"
        ) != WP6_CANONICAL_LEDGER_ANCHOR:
            errors.append(
                "record WP6 historical allowlist anchor mismatch"
            )
        if policy.get(
            "wp6_historical_allowlist_replay_mode"
        ) != "DETACHED_FROZEN_WORKTREE":
            errors.append(
                "record WP6 historical allowlist replay-mode mismatch"
            )
        boundary = policy.get(
            "post_merge_local_validation_boundary", {}
        )
        if boundary.get("origin_main") != POST_MERGE_ORIGIN_MAIN:
            errors.append("record post-merge main boundary mismatch")
        if boundary.get(
            "origin_development"
        ) != POST_MERGE_ORIGIN_DEVELOPMENT:
            errors.append(
                "record post-merge development boundary mismatch"
            )
        if boundary.get("main_ahead") != 2:
            errors.append("record main-ahead boundary mismatch")
        if boundary.get("development_ahead") != 0:
            errors.append("record development-ahead boundary mismatch")
        if record.get("controlled_modified_paths") != CONTROLLED:
            errors.append("record controlled-path mismatch")
        if record.get("additive_paths") != ADDITIVE:
            errors.append("record additive-path mismatch")
        if manifest.get("changed_path_count") != 34:
            errors.append("manifest path count mismatch")
        if manifest.get("ledger_entry_count") != 33:
            errors.append("manifest ledger count mismatch")
        if manifest.get(
            "frozen_ledger_anchor_commit"
        ) != FROZEN_LEDGER_ANCHOR:
            errors.append("manifest frozen-ledger anchor mismatch")
        if manifest.get(
            "wp5_historical_replay_anchor_commit"
        ) != WP5_HISTORICAL_REPLAY_ANCHOR:
            errors.append("manifest WP5 historical anchor mismatch")
        if manifest.get(
            "wp6_canonical_ledger_anchor_commit"
        ) != WP6_CANONICAL_LEDGER_ANCHOR:
            errors.append("manifest WP6 canonical anchor mismatch")
        if manifest.get(
            "wp6_historical_allowlist_replay_anchor_commit"
        ) != WP6_CANONICAL_LEDGER_ANCHOR:
            errors.append(
                "manifest WP6 historical allowlist anchor mismatch"
            )
        if manifest.get(
            "wp6_historical_allowlist_replay_mode"
        ) != "DETACHED_FROZEN_WORKTREE":
            errors.append(
                "manifest WP6 historical allowlist replay-mode mismatch"
            )
    except Exception as exc:
        errors.append("record/manifest failure: " + str(exc))

    if (ROOT / LEDGER).is_file():
        try:
            ledger = {}
            for line in (ROOT / LEDGER).read_text().splitlines():
                digest, path = line.split("  ", 1)
                ledger[path] = digest

            expected = sorted(p for p in ALL_PATHS if p != LEDGER)
            if sorted(ledger) != expected:
                errors.append("ledger inventory mismatch")
            for path in expected:
                if ledger.get(path) != sha256(path):
                    errors.append("SHA-256 mismatch: " + path)
        except Exception as exc:
            errors.append("ledger failure: " + str(exc))

    result = {
        "artifact": "WP6_POST_MERGE_PUSH_CONTEXT_REPAIR",
        "mode": mode,
        "baseline": BASELINE,
        "canonical_main": CANONICAL_MAIN,
        "changed_path_count": 34,
        "controlled_modified_path_count": 28,
        "additive_path_count": 6,
        "predecessor_workflow_count": 14,
        "predecessor_job_count": 30,
        "errors": errors,
        "commit_created": False,
        "push_performed": False,
        "synchronization_performed": False,
        "release_actions_performed": False,
        "status": "PASS" if not errors else "FAIL",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
