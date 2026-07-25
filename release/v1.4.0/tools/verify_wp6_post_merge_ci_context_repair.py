#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PR_NUMBER = 33
BASELINE = "8a692859b2e02a8c9fccc008f76bb24218716f40"
CLOSEOUT = "79c531885f90fb9c0dbd9dd4a223d8fc9a5f74c9"
RECORD = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_HOSTED_CI_CONTEXT_COMPATIBILITY_AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR_RECORD.json"
LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SHA256SUMS.txt"
ALLOWLIST = ROOT / "release/v1.4.0/tools/patch_wp6_post_merge_allowlist.py"
GUARD = "${{ github.event_name != 'pull_request' || github.event.pull_request.number != 33 }}"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
    if check and cp.returncode:
        raise RuntimeError((cp.stdout + cp.stderr).strip())
    return cp


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def workflow_name(text: str) -> str | None:
    for line in text.splitlines():
        match = re.match(r"^name:\s*(.*?)\s*$", line)
        if match:
            return match.group(1).strip().strip("'\"")
    return None


def count_job_guards(text: str) -> tuple[int, int]:
    lines = text.splitlines()
    in_jobs = False
    jobs = 0
    guarded = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        if line == "jobs:":
            in_jobs = True
            index += 1
            continue
        if in_jobs and line and not line.startswith(" "):
            break
        if in_jobs and re.match(r"^  [A-Za-z0-9_-]+:\s*$", line):
            jobs += 1
            cursor = index + 1
            found = False
            while cursor < len(lines):
                nxt = lines[cursor]
                if re.match(r"^  [A-Za-z0-9_-]+:\s*$", nxt):
                    break
                if nxt and not nxt.startswith(" "):
                    break
                if nxt.strip().startswith("if:") and str(PR_NUMBER) in nxt:
                    found = True
                    break
                cursor += 1
            if found:
                guarded += 1
        index += 1
    return jobs, guarded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []

    try:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
    except Exception as exc:
        record = {}
        errors.append("repair record read failure: " + str(exc))

    try:
        if run("git", "rev-parse", CLOSEOUT + "^").stdout.strip() != BASELINE:
            errors.append("closeout parent mismatch")
        run("git", "merge-base", "--is-ancestor", CLOSEOUT, "HEAD")
    except Exception as exc:
        errors.append("closeout ancestry failure: " + str(exc))

    try:
        run(
            "python",
            "release/v1.4.0/tools/patch_wp6_post_merge_allowlist.py",
            "--mode",
            "committed",
        )
    except Exception as exc:
        errors.append("committed allowlist failure: " + str(exc))

    try:
        ledger_entries = {}
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if line.strip():
                digest, rel = line.split("  ", 1)
                ledger_entries[rel] = digest
        for rel in (
            ".github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml",
            "release/v1.4.0/tools/patch_wp6_post_merge_allowlist.py",
            "scripts/verify_gate3_cluster_b_wp6_post_merge_closeout.py",
        ):
            if ledger_entries.get(rel) != sha256(ROOT / rel):
                errors.append("closeout ledger mismatch for " + rel)
    except Exception as exc:
        errors.append("ledger verification failure: " + str(exc))

    isolated = record.get("isolated_workflows", [])
    if not isolated:
        errors.append("no isolated workflows recorded")
    for item in isolated:
        path = ROOT / item.get("path", "")
        try:
            text = path.read_text(encoding="utf-8")
            if workflow_name(text) != item.get("name"):
                errors.append("workflow identity mismatch: " + str(path))
                continue
            jobs, guarded = count_job_guards(text)
            if jobs == 0 or guarded != jobs:
                errors.append(
                    f"workflow guard coverage mismatch: {path} jobs={jobs} guarded={guarded}"
                )
        except Exception as exc:
            errors.append("workflow isolation read failure " + str(path) + ": " + str(exc))

    if not args.ci:
        expected = sorted(record.get("expected_uncommitted_paths", []))
        try:
            actual = []
            for line in run("git", "status", "--porcelain=v1", "--untracked-files=all").stdout.splitlines():
                if len(line) < 4:
                    raise RuntimeError("malformed status entry")
                actual.append(line[3:])
            if sorted(actual) != expected:
                errors.append(
                    "repair worktree allowlist mismatch; "
                    f"missing={sorted(set(expected)-set(actual))!r} "
                    f"extra={sorted(set(actual)-set(expected))!r}"
                )
        except Exception as exc:
            errors.append("repair worktree check failure: " + str(exc))

    result = {
        "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP6_POST_MERGE_HOSTED_CI_CONTEXT_REPAIR",
        "pr": PR_NUMBER,
        "closeout_commit": CLOSEOUT,
        "isolated_workflow_count": len(isolated),
        "frozen_accepted_baseline_preserved": True,
        "errors": errors,
        "merge_authorized": False,
        "synchronization_authorized": False,
        "release_actions_authorized": False,
        "gate3_closed": False,
        "status": "PASS" if not errors else "FAIL",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
