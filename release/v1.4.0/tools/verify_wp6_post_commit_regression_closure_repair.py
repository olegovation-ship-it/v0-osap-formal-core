#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
BRANCH = "v1.4.0-development"
PREDECESSOR_HEAD = "33e292b6ae2e5f35135c9a8e35c9697901cae829"
PREDECESSOR_PARENT = "ba32d8e855a79461fdcda14740acab86aafcb17a"
ORIGIN_MAIN_BEFORE_REPAIR = "47614ce7891f4895e003cb85e7651b7d043a963d"
ORIGIN_DEVELOPMENT_BEFORE_REPAIR = "ba32d8e855a79461fdcda14740acab86aafcb17a"
OLD_MANIFEST = "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_PUSH_CONTEXT_COMPATIBILITY_AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR_MANIFEST.json"
OLD_LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_PUSH_CONTEXT_COMPATIBILITY_AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR_SHA256SUMS.txt"
MANIFEST = "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_MANIFEST.json"
RECORD = "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_RECORD.json"
LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_SHA256SUMS.txt"
CONTROLLED = [
    "scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py",
    "scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp6.py",
    "scripts/verify_gate3_cluster_b_wp6_post_merge_closeout.py"
]
ADDITIVE = [
    "docs/gate3/cluster_b/WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR.md",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_MANIFEST.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_SHA256SUMS.txt",
    "release/v1.4.0/tools/verify_wp6_post_commit_regression_closure_repair.py",
    "tests/test_gate3_cluster_b_wp6_post_commit_regression_closure_repair.py"
]
ALL_PATHS = sorted(CONTROLLED + ADDITIVE)


def run(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=text,
        check=False,
    )


def git_text(*args: str) -> str:
    cp = run("git", *args)
    if cp.returncode:
        raise RuntimeError((cp.stdout + cp.stderr).strip())
    return cp.stdout.rstrip("\n")


def git_bytes(*args: str) -> bytes:
    cp = run("git", *args, text=False)
    if cp.returncode:
        raise RuntimeError((cp.stdout + cp.stderr).decode(errors="replace").strip())
    return cp.stdout


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(relative: str) -> str:
    return sha256_bytes((ROOT / relative).read_bytes())


def parse_ledger(relative: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in (ROOT / relative).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, path = line.split("  ", 1)
        if path in entries:
            raise RuntimeError("duplicate ledger path: " + path)
        entries[path] = digest
    return entries


def status_entries() -> dict[str, str]:
    rows: dict[str, str] = {}
    output = git_text("status", "--porcelain=v1", "--untracked-files=all")
    for line in output.splitlines():
        if len(line) < 4 or " -> " in line:
            raise RuntimeError("invalid status entry: " + repr(line))
        rows[line[3:]] = line[:2]
    return rows


def diff_entries(base: str, head: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    output = git_text(
        "diff", "--name-status", "--no-renames", base + ".." + head
    )
    for line in output.splitlines():
        if not line.strip():
            continue
        code, path = line.split("\t", 1)
        rows[path] = code
    return rows


def expected_codes(controlled: list[str], additive: list[str], mode: str) -> dict[str, str]:
    if mode == "working-tree":
        return {**{p: " M" for p in controlled}, **{p: "??" for p in additive}}
    return {**{p: "M" for p in controlled}, **{p: "A" for p in additive}}


def verify_exact_entries(actual: dict[str, str], expected: dict[str, str], label: str) -> None:
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        wrong = sorted(
            p for p in set(actual) & set(expected) if actual[p] != expected[p]
        )
        raise RuntimeError(
            f"{label} mismatch; missing={missing!r} extra={extra!r} wrong={wrong!r}"
        )


def previous_repair_entries() -> dict[str, str]:
    manifest = json.loads((ROOT / OLD_MANIFEST).read_text(encoding="utf-8"))
    if manifest.get("baseline_commit") != PREDECESSOR_PARENT:
        raise RuntimeError("previous repair baseline mismatch")
    if manifest.get("ledger_path") != OLD_LEDGER:
        raise RuntimeError("previous repair ledger path mismatch")
    controlled = sorted(manifest.get("controlled_modified_paths", []))
    additive = sorted(manifest.get("additive_paths", []))
    full_surface = sorted(controlled + additive)
    if manifest.get("changed_path_count") != len(full_surface):
        raise RuntimeError("previous repair path count mismatch")
    if git_text("rev-parse", PREDECESSOR_HEAD + "^") != PREDECESSOR_PARENT:
        raise RuntimeError("predecessor parent mismatch")
    verify_exact_entries(
        diff_entries(PREDECESSOR_PARENT, PREDECESSOR_HEAD),
        expected_codes(controlled, additive, "committed"),
        "previous repair committed surface",
    )
    current_ledger = (ROOT / OLD_LEDGER).read_bytes()
    frozen_ledger = git_bytes("show", PREDECESSOR_HEAD + ":" + OLD_LEDGER)
    if current_ledger != frozen_ledger:
        raise RuntimeError("previous repair ledger bytes changed")
    entries = parse_ledger(OLD_LEDGER)
    expected_inputs = set(full_surface) - {OLD_LEDGER}
    if set(entries) != expected_inputs:
        raise RuntimeError("previous repair ledger inventory mismatch")
    for path, digest in entries.items():
        if sha256_bytes(git_bytes("show", PREDECESSOR_HEAD + ":" + path)) != digest:
            raise RuntimeError("previous repair predecessor blob mismatch: " + path)
    return entries


def current_manifest_and_entries() -> tuple[dict, dict, dict[str, str]]:
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    record = json.loads((ROOT / RECORD).read_text(encoding="utf-8"))
    if manifest.get("pre_repair_head") != PREDECESSOR_HEAD:
        raise RuntimeError("manifest predecessor mismatch")
    if manifest.get("pre_repair_parent") != PREDECESSOR_PARENT:
        raise RuntimeError("manifest predecessor-parent mismatch")
    if manifest.get("controlled_modified_paths") != CONTROLLED:
        raise RuntimeError("manifest controlled-path mismatch")
    if manifest.get("additive_paths") != ADDITIVE:
        raise RuntimeError("manifest additive-path mismatch")
    outputs = manifest.get("controlled_output_sha256", {})
    if set(outputs) != set(CONTROLLED):
        raise RuntimeError("manifest controlled-output inventory mismatch")
    for path in CONTROLLED:
        if outputs.get(path) != sha256_path(path):
            raise RuntimeError("manifest controlled-output hash mismatch: " + path)
    if manifest.get("changed_path_count") != 12:
        raise RuntimeError("manifest changed-path count mismatch")
    if manifest.get("ledger_entry_count") != 11:
        raise RuntimeError("manifest ledger-entry count mismatch")
    if manifest.get("ledger_path") != LEDGER or not manifest.get("ledger_self_excluded"):
        raise RuntimeError("manifest ledger policy mismatch")
    if record.get("pre_repair_head") != PREDECESSOR_HEAD:
        raise RuntimeError("record predecessor mismatch")
    if record.get("controlled_modified_paths") != CONTROLLED:
        raise RuntimeError("record controlled-path mismatch")
    if record.get("additive_paths") != ADDITIVE:
        raise RuntimeError("record additive-path mismatch")
    if record.get("status") != "PREPARED_UNCOMMITTED":
        raise RuntimeError("record status mismatch")
    if any(record.get("authorization_firewall", {}).values()):
        raise RuntimeError("authorization firewall failure")
    entries = parse_ledger(LEDGER)
    if set(entries) != set(ALL_PATHS) - {LEDGER}:
        raise RuntimeError("current repair ledger inventory mismatch")
    for path, digest in entries.items():
        target = ROOT / path
        if not target.is_file() or sha256_path(path) != digest:
            raise RuntimeError("current repair SHA-256 mismatch: " + path)
    return manifest, record, entries


def detect_mode() -> str:
    entries = status_entries()
    if entries:
        return "working-tree"
    return "committed"


def current_repair_entries(mode: str = "auto") -> dict[str, str]:
    _, _, entries = current_manifest_and_entries()
    if mode == "package-only":
        return entries
    if mode == "auto":
        mode = detect_mode()
    if git_text("rev-parse", PREDECESSOR_HEAD + "^") != PREDECESSOR_PARENT:
        raise RuntimeError("predecessor parent identity mismatch")
    if mode == "working-tree":
        if git_text("rev-parse", "HEAD") != PREDECESSOR_HEAD:
            raise RuntimeError("prepared repair HEAD mismatch")
        verify_exact_entries(
            status_entries(),
            expected_codes(CONTROLLED, ADDITIVE, "working-tree"),
            "current working-tree surface",
        )
    elif mode == "committed":
        if status_entries():
            raise RuntimeError("committed repair working tree is not clean")
        if git_text("rev-parse", "HEAD^") != PREDECESSOR_HEAD:
            raise RuntimeError("committed repair exact parent mismatch")
        verify_exact_entries(
            diff_entries(PREDECESSOR_HEAD, "HEAD"),
            expected_codes(CONTROLLED, ADDITIVE, "committed"),
            "current committed surface",
        )
    else:
        raise RuntimeError("unsupported mode: " + mode)
    return entries


def attested_successor_hashes(mode: str = "auto") -> dict[str, str]:
    previous = previous_repair_entries()
    current = current_repair_entries(mode)
    return {**previous, **current}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("auto", "working-tree", "committed", "package-only"),
        default="auto",
    )
    args = parser.parse_args()
    errors: list[str] = []
    mode = args.mode
    try:
        if mode == "package-only":
            current_repair_entries(mode)
        else:
            attested_successor_hashes(mode)
            if os.environ.get("GITHUB_ACTIONS") != "true":
                branch = git_text("branch", "--show-current")
                if branch != BRANCH:
                    errors.append("branch mismatch")
                if mode in ("auto", "working-tree") and detect_mode() == "working-tree":
                    if git_text("rev-parse", "origin/main") != ORIGIN_MAIN_BEFORE_REPAIR:
                        errors.append("origin/main mismatch")
                    if git_text("rev-parse", "origin/" + BRANCH) != ORIGIN_DEVELOPMENT_BEFORE_REPAIR:
                        errors.append("origin/development mismatch")
    except Exception as exc:
        errors.append(str(exc))
    result = {
        "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR",
        "mode": mode,
        "pre_repair_head": PREDECESSOR_HEAD,
        "controlled_modified_path_count": 6,
        "additive_path_count": 6,
        "changed_path_count": 12,
        "ledger_entry_count": 11,
        "errors": errors,
        "staging_performed": False,
        "commit_performed": False,
        "push_performed": False,
        "release_actions_performed": False,
        "status": "PASS" if not errors else "FAIL",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
