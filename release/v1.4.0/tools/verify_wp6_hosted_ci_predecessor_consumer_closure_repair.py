#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
BRANCH = "v1.4.0-development"
PRE_REPAIR_HEAD = "3bbe861153cca8123fc9d528921ebc9dc2bb41e5"
PRE_REPAIR_PARENT = "59fa5076fdabf74b832fb985947253eaaecca4ae"
PRE_REPAIR_TITLE = "repair(wp6): close hosted CI regression compatibility gaps"
CURRENT_STEM = "GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR"
CURRENT_MANIFEST = f"release/v1.4.0/{CURRENT_STEM}_MANIFEST.json"
CURRENT_RECORD = f"release/v1.4.0/{CURRENT_STEM}_RECORD.json"
CURRENT_LEDGER = f"release/v1.4.0/{CURRENT_STEM}_SHA256SUMS.txt"
CURRENT_DOC = "docs/gate3/cluster_b/WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR.md"
CURRENT_VERIFIER = "release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py"
CURRENT_TEST = "tests/test_gate3_cluster_b_wp6_hosted_ci_predecessor_consumer_closure_repair.py"
V03_VERIFIER = "release/v1.4.0/tools/verify_wp6_hosted_ci_regression_corrective_repair.py"

CONTROLLED = [
    ".github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml",
    "release/v1.4.0/tools/patch_wp5_allowlist.py",
    "release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py",
    "release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py",
    "release/v1.4.0/tools/verify_wp6_hosted_ci_regression_corrective_repair.py",
    "scripts/verify_gate3_cluster_b_wp2.py",
    "scripts/verify_gate3_cluster_b_wp3.py",
]
ADDITIVE = [
    CURRENT_DOC,
    CURRENT_MANIFEST,
    CURRENT_RECORD,
    CURRENT_LEDGER,
    CURRENT_VERIFIER,
    CURRENT_TEST,
]
ALL_PATHS = sorted(CONTROLLED + ADDITIVE)

INPUT_GIT_BLOBS = {
    ".github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml": "080e3efaa75a2b17240f5057130397c0ae93795c",
    "release/v1.4.0/tools/patch_wp5_allowlist.py": "b38b9dacf928a93c9da91f2261684b48dbe2451b",
    "release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py": "37ce7389cbc98e566105f98c7952fbdc8a49ba0f",
    "release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py": "eea356a18b1a93b44fd3ce8a6129b6bb33493d69",
    "release/v1.4.0/tools/verify_wp6_hosted_ci_regression_corrective_repair.py": "624ceaf2ea1035c873e49f6da27290270a652dbb",
    "scripts/verify_gate3_cluster_b_wp2.py": "9629412c468397f19c164a2aeb31a7bac744e365",
    "scripts/verify_gate3_cluster_b_wp3.py": "a657d1b2c706a90ce9f7278dc42661811dbe6729",
}

FROZEN_PATHS = [
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_REGRESSION_CORRECTIVE_REPAIR_SHA256SUMS.txt",
]

CONSUMERS: dict[str, tuple[str, str]] = {
    "wp5-canonical-allowlist": (
        "14e761e7a34889eebc3c4ef7df17fc56c9267af9",
        "release/v1.4.0/tools/patch_wp5_allowlist.py",
    ),
    "wp5-post-merge-allowlist": (
        "14e761e7a34889eebc3c4ef7df17fc56c9267af9",
        "release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py",
    ),
    "wp5-sync-helper-allowlist": (
        "14e761e7a34889eebc3c4ef7df17fc56c9267af9",
        "release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py",
    ),
    "wp2-verifier": (
        "c90041d3da5b680b574b910de50d8769d32fbfa9",
        "scripts/verify_gate3_cluster_b_wp2.py",
    ),
    "wp3-post-merge-allowlist": (
        "c90041d3da5b680b574b910de50d8769d32fbfa9",
        "release/v1.4.0/tools/patch_wp3_post_merge_allowlist.py",
    ),
    "wp3-canonical-verifier": (
        "c90041d3da5b680b574b910de50d8769d32fbfa9",
        "scripts/verify_gate3_cluster_b_wp3.py",
    ),
}

FAILED_WORKFLOW_MATRIX: list[dict[str, Any]] = [
    {
        "ordinal": 1,
        "run_id": 30247954889,
        "workflow": "V0 OSAP Gate 3 Cluster B WP5 Post-Merge Closeout",
        "workflow_file": ".github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml",
        "failure_class": "WP5_POST_MERGE_CUMULATIVE_ALLOWLIST",
        "command": ["python", CURRENT_VERIFIER, "--replay-consumer", "wp5-post-merge-allowlist", "--consumer-arg=--check"],
    },
    {
        "ordinal": 2,
        "run_id": 30247954915,
        "workflow": "V0 OSAP Gate 3 Cluster B WP5 Synchronization Helper Repair",
        "workflow_file": ".github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml",
        "failure_class": "WP5_SYNC_HELPER_CUMULATIVE_ALLOWLIST",
        "command": ["python", CURRENT_VERIFIER, "--replay-consumer", "wp5-sync-helper-allowlist", "--consumer-arg=--check"],
    },
    {
        "ordinal": 3,
        "run_id": 30247954930,
        "workflow": "V0 OSAP Gate 3 Cluster B WP3",
        "workflow_file": ".github/workflows/gate3-cluster-b-wp3.yml",
        "failure_class": "WP3_CANONICAL_PRESERVATION_FIREWALL_STALE_BOUNDARY",
        "command": ["python", "scripts/verify_gate3_cluster_b_wp3.py"],
    },
    {
        "ordinal": 4,
        "run_id": 30247954944,
        "workflow": "V0 OSAP Gate 3 Cluster B WP2 Post-Merge Closeout",
        "workflow_file": ".github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml",
        "failure_class": "WP2_PUSH_CONTEXT_STALE_BOUNDARY",
        "command": ["python", "scripts/verify_gate3_cluster_b_wp2.py"],
    },
    {
        "ordinal": 5,
        "run_id": 30247954960,
        "workflow": "V0 OSAP Gate 3 Cluster B WP3 Post-Merge Closeout",
        "workflow_file": ".github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml",
        "failure_class": "WP3_POST_MERGE_FIXED_DIGEST_CONSUMER",
        "command": ["python", CURRENT_VERIFIER, "--replay-consumer", "wp3-post-merge-allowlist", "--consumer-arg=--check"],
    },
    {
        "ordinal": 6,
        "run_id": 30247954972,
        "workflow": "V0 OSAP Gate 3 Cluster B WP5",
        "workflow_file": ".github/workflows/gate3-cluster-b-wp5.yml",
        "failure_class": "WP5_SHARED_CANONICAL_CUMULATIVE_ALLOWLIST",
        "command": ["python", CURRENT_VERIFIER, "--replay-consumer", "wp5-canonical-allowlist", "--consumer-arg=--check"],
    },
    {
        "ordinal": 7,
        "run_id": 30247954989,
        "workflow": "V0 OSAP Gate 3 Cluster B WP2",
        "workflow_file": ".github/workflows/gate3-cluster-b-wp2.yml",
        "failure_class": "WP2_CANONICAL_STALE_REPOSITORY_BOUNDARY",
        "command": ["python", "scripts/verify_gate3_cluster_b_wp2.py"],
    },
]


def run(*args: str, cwd: Path | None = None, text: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=cwd or ROOT,
        capture_output=True,
        text=text,
        check=False,
        env=env,
    )


def git_text(*args: str, cwd: Path | None = None) -> str:
    cp = run("git", *args, cwd=cwd)
    if cp.returncode:
        raise RuntimeError((cp.stdout + cp.stderr).strip())
    return cp.stdout.rstrip("\n")


def sha256_path(relative: str, root: Path = ROOT) -> str:
    return hashlib.sha256((root / relative).read_bytes()).hexdigest()


def parse_ledger(relative: str, root: Path = ROOT) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in (root / relative).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, path = line.split("  ", 1)
        if path in result:
            raise RuntimeError("duplicate ledger path: " + path)
        result[path] = digest
    return result


def load_manifest(root: Path = ROOT) -> dict[str, Any]:
    return json.loads((root / CURRENT_MANIFEST).read_text(encoding="utf-8"))


def status_entries() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in git_text("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if not line:
            continue
        if len(line) < 4 or " -> " in line:
            raise RuntimeError("invalid status row: " + repr(line))
        entries[line[3:]] = line[:2]
    return entries


def diff_entries(base: str, head: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in git_text("diff", "--name-status", "--no-renames", base, head).splitlines():
        if not line:
            continue
        code, path = line.split("\t", 1)
        entries[path] = code
    return entries


def expected_codes(mode: str) -> dict[str, str]:
    if mode == "working-tree":
        return {
            **{path: " M" for path in CONTROLLED},
            **{path: "??" for path in ADDITIVE},
        }
    return {
        **{path: "M" for path in CONTROLLED},
        **{path: "A" for path in ADDITIVE},
    }


def require_exact(actual: dict[str, str], expected: dict[str, str], label: str) -> None:
    if actual == expected:
        return
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    wrong = sorted(
        (path, actual[path], expected[path])
        for path in set(actual) & set(expected)
        if actual[path] != expected[path]
    )
    raise RuntimeError(f"{label} mismatch; missing={missing!r}; extra={extra!r}; wrong={wrong!r}")


def verify_working_tree_surface_entries(actual: dict[str, str]) -> list[str]:
    """Validate the exact package surface while allowing unrelated untracked artifacts.

    The 13 package paths remain exact. Entries outside that surface are permitted
    only when their porcelain status is ``??``. Any staged, tracked, unmerged,
    deleted, renamed, or otherwise structural extra remains a hard failure.
    """
    expected = expected_codes("working-tree")
    package_actual = {path: actual[path] for path in ALL_PATHS if path in actual}
    require_exact(package_actual, expected, "prepared v0.9 package surface")

    unrelated_untracked = sorted(
        path for path, code in actual.items() if path not in ALL_PATHS and code == "??"
    )
    forbidden_extra = sorted(
        (path, code)
        for path, code in actual.items()
        if path not in ALL_PATHS and code != "??"
    )
    if forbidden_extra:
        raise RuntimeError(
            "unrelated tracked/staged/structural repository changes; "
            f"entries={forbidden_extra!r}"
        )
    return unrelated_untracked


def verify_committed_worktree_entries(actual: dict[str, str]) -> list[str]:
    package_entries = sorted((path, actual[path]) for path in ALL_PATHS if path in actual)
    if package_entries:
        raise RuntimeError(
            "committed v0.9 package paths are not clean; "
            f"entries={package_entries!r}"
        )
    unrelated_untracked = sorted(path for path, code in actual.items() if code == "??")
    forbidden_extra = sorted((path, code) for path, code in actual.items() if code != "??")
    if forbidden_extra:
        raise RuntimeError(
            "committed v0.9 working tree has tracked/staged/structural changes; "
            f"entries={forbidden_extra!r}"
        )
    return unrelated_untracked


def verify_no_mode_or_structural_diff() -> None:
    unstaged_summary = git_text("diff", "--summary", "--no-renames")
    staged_summary = git_text("diff", "--cached", "--summary", "--no-renames")
    if unstaged_summary or staged_summary:
        raise RuntimeError(
            "mode or structural diff detected; "
            f"unstaged={unstaged_summary!r}; staged={staged_summary!r}"
        )
    if git_text("ls-files", "-u"):
        raise RuntimeError("unmerged paths detected")


def verify_package_only(root: Path = ROOT) -> dict[str, str]:
    manifest = load_manifest(root)
    if manifest.get("version") != "0.9":
        raise RuntimeError("package version mismatch")
    if manifest.get("repository") != REPOSITORY or manifest.get("branch") != BRANCH:
        raise RuntimeError("package repository identity mismatch")
    if manifest.get("pre_repair_head") != PRE_REPAIR_HEAD:
        raise RuntimeError("package predecessor mismatch")
    if manifest.get("pre_repair_parent") != PRE_REPAIR_PARENT:
        raise RuntimeError("package predecessor-parent mismatch")
    if manifest.get("controlled_modified_paths") != CONTROLLED:
        raise RuntimeError("package controlled-path mismatch")
    if manifest.get("additive_paths") != ADDITIVE:
        raise RuntimeError("package additive-path mismatch")
    if manifest.get("changed_path_count") != len(ALL_PATHS):
        raise RuntimeError("package path count mismatch")
    if manifest.get("controlled_input_git_blob_sha1") != INPUT_GIT_BLOBS:
        raise RuntimeError("package controlled-input blob map mismatch")
    if manifest.get("ledger_path") != CURRENT_LEDGER:
        raise RuntimeError("package ledger path mismatch")
    if manifest.get("frozen_ledgers_rewritten") is not False:
        raise RuntimeError("frozen-ledger rewrite flag mismatch")
    if manifest.get("historical_records_rewritten") is not False:
        raise RuntimeError("historical-record rewrite flag mismatch")
    if manifest.get("unrelated_untracked_artifacts_allowed") is not True:
        raise RuntimeError("unrelated-untracked policy mismatch")
    if manifest.get("unrelated_tracked_changes_allowed") is not False:
        raise RuntimeError("unrelated-tracked policy mismatch")
    if manifest.get("working_tree_surface_policy") != (
        "EXACT_13_PACKAGE_STATUSES_PLUS_UNRELATED_UNTRACKED_ARTIFACTS"
    ):
        raise RuntimeError("working-tree surface policy mismatch")

    forbidden_fragments = (
        "/schemas/", "/fixtures/", "/lean/", "/coq/",
    )
    for path in ALL_PATHS:
        wrapped = "/" + path
        if any(fragment in wrapped for fragment in forbidden_fragments):
            raise RuntimeError("forbidden package path: " + path)
        if path.endswith("_SHA256SUMS.txt") and path != CURRENT_LEDGER:
            raise RuntimeError("frozen ledger included in package: " + path)

    ledger = parse_ledger(CURRENT_LEDGER, root)
    expected_ledger_paths = sorted(path for path in ALL_PATHS if path != CURRENT_LEDGER)
    if sorted(ledger) != expected_ledger_paths:
        raise RuntimeError("package ledger inventory mismatch")
    for path in expected_ledger_paths:
        if not (root / path).is_file():
            raise RuntimeError("package file missing: " + path)
        if sha256_path(path, root) != ledger[path]:
            raise RuntimeError("package SHA-256 mismatch: " + path)
    outputs = manifest.get("controlled_output_sha256", {})
    if outputs != {path: ledger[path] for path in CONTROLLED}:
        raise RuntimeError("controlled output digest map mismatch")

    record = json.loads((root / CURRENT_RECORD).read_text(encoding="utf-8"))
    if record.get("version") != "0.9":
        raise RuntimeError("record version mismatch")
    if record.get("failed_workflow_matrix") != FAILED_WORKFLOW_MATRIX:
        raise RuntimeError("failed workflow matrix mismatch")
    expected_failed_runs = [
        {
            "failure_class": entry["failure_class"],
            "run_id": entry["run_id"],
            "workflow": entry["workflow"],
        }
        for entry in FAILED_WORKFLOW_MATRIX
    ]
    if record.get("failed_runs") != expected_failed_runs:
        raise RuntimeError("failed-runs summary mismatch")
    workflows = [entry["workflow"] for entry in FAILED_WORKFLOW_MATRIX]
    run_ids = [entry["run_id"] for entry in FAILED_WORKFLOW_MATRIX]
    ordinals = [entry["ordinal"] for entry in FAILED_WORKFLOW_MATRIX]
    if len(workflows) != len(set(workflows)) or len(run_ids) != len(set(run_ids)):
        raise RuntimeError("failure matrix is not one-to-one")
    if ordinals != list(range(1, 8)):
        raise RuntimeError("failure matrix ordinal mismatch")
    wp3 = next(entry for entry in FAILED_WORKFLOW_MATRIX if entry["workflow"] == "V0 OSAP Gate 3 Cluster B WP3")
    if wp3["command"] != ["python", "scripts/verify_gate3_cluster_b_wp3.py"]:
        raise RuntimeError("WP3 canonical failure matrix command mismatch")
    return ledger


def detect_mode() -> str:
    entries = status_entries()
    return "working-tree" if any(path in entries for path in ALL_PATHS) else "committed"


def resolve_committed_surface_head() -> str:
    candidates: list[str] = []

    def add(value: str) -> None:
        if value and value not in candidates:
            candidates.append(value)

    add(git_text("rev-parse", "HEAD"))
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if event_path:
        try:
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            add(str(event.get("pull_request", {}).get("head", {}).get("sha", "")))
        except Exception:
            pass
    try:
        row = git_text("rev-list", "--parents", "-n", "1", "HEAD").split()
        for parent in row[1:]:
            add(parent)
    except Exception:
        pass

    expected = expected_codes("committed")
    for candidate in candidates:
        cp = run("git", "rev-list", "--parents", "-n", "1", candidate)
        if cp.returncode:
            continue
        fields = cp.stdout.split()
        if len(fields) != 2 or fields[1] != PRE_REPAIR_HEAD:
            continue
        try:
            if diff_entries(PRE_REPAIR_HEAD, candidate) == expected:
                return candidate
        except Exception:
            continue
    raise RuntimeError("unable to resolve exact v0.9 committed head")


def verify_repository_surface(mode: str) -> dict[str, str]:
    ledger = verify_package_only()
    if git_text("rev-parse", "HEAD") == PRE_REPAIR_HEAD:
        for path, expected_blob in INPUT_GIT_BLOBS.items():
            if git_text("rev-parse", f"{PRE_REPAIR_HEAD}:{path}") != expected_blob:
                raise RuntimeError("controlled input Git blob mismatch: " + path)
    else:
        for path, expected_blob in INPUT_GIT_BLOBS.items():
            if git_text("rev-parse", f"{PRE_REPAIR_HEAD}:{path}") != expected_blob:
                raise RuntimeError("controlled input Git blob mismatch: " + path)

    entries = status_entries()
    verify_no_mode_or_structural_diff()
    if mode == "working-tree":
        if git_text("rev-parse", "HEAD") != PRE_REPAIR_HEAD:
            raise RuntimeError("prepared repair HEAD mismatch")
        verify_working_tree_surface_entries(entries)
    elif mode == "committed":
        verify_committed_worktree_entries(entries)
        surface_head = resolve_committed_surface_head()
        require_exact(
            diff_entries(PRE_REPAIR_HEAD, surface_head),
            expected_codes(mode),
            "committed v0.9 surface",
        )
    else:
        raise RuntimeError("unsupported repository mode: " + mode)

    for path in FROZEN_PATHS:
        if sha256_path(path) != hashlib.sha256(
            run("git", "show", f"{PRE_REPAIR_HEAD}:{path}", text=False).stdout
        ).hexdigest():
            raise RuntimeError("frozen path changed: " + path)
    return ledger


def temporary_worktree(commit: str):
    class Worktree:
        def __init__(self, target: str):
            self.target = target
            self.tmp = Path(tempfile.mkdtemp(prefix="v0-osap-v09-"))
            self.path = self.tmp / "repository"

        def __enter__(self) -> Path:
            cp = run("git", "worktree", "add", "--detach", str(self.path), self.target)
            if cp.returncode:
                shutil.rmtree(self.tmp, ignore_errors=True)
                raise RuntimeError((cp.stdout + cp.stderr).strip())
            return self.path

        def __exit__(self, exc_type, exc, tb) -> None:
            run("git", "worktree", "remove", "--force", str(self.path))
            run("git", "worktree", "prune")
            shutil.rmtree(self.tmp, ignore_errors=True)

    return Worktree(commit)


def historical_v03_overlay() -> dict[str, str]:
    with temporary_worktree(PRE_REPAIR_HEAD) as worktree:
        verifier = worktree / V03_VERIFIER
        cp = run(
            sys.executable,
            str(verifier),
            "--mode",
            "committed",
            "--emit-overlay-json",
            cwd=worktree,
        )
        if cp.returncode:
            raise RuntimeError("historical v0.3 attestation failed: " + (cp.stdout + cp.stderr).strip())
        result = json.loads(cp.stdout)
        overlay = result.get("overlay")
        if result.get("status") != "PASS" or not isinstance(overlay, dict):
            raise RuntimeError("historical v0.3 overlay is unavailable")
        return {str(path): str(digest) for path, digest in overlay.items()}


def successor_overlay_attestation(mode: str = "auto") -> dict[str, str] | None:
    try:
        if mode == "auto":
            mode = detect_mode()
        if mode == "package-only":
            return verify_package_only()
        current = verify_repository_surface(mode)
        previous = historical_v03_overlay()
        combined = {**previous, **current}
        for path, expected in combined.items():
            target = ROOT / path
            if target.is_file() and sha256_path(path) != expected:
                raise RuntimeError("layered overlay SHA-256 mismatch: " + path)
        return combined
    except Exception:
        return None


def replay_consumer(name: str, consumer_args: list[str] | None = None) -> int:
    if name not in CONSUMERS:
        print(json.dumps({"artifact": CURRENT_STEM, "error": "unknown consumer: " + name, "status": "FAIL"}, indent=2, sort_keys=True))
        return 2
    overlay = successor_overlay_attestation("auto")
    if overlay is None:
        print(json.dumps({"artifact": CURRENT_STEM, "consumer": name, "error": "v0.9 successor attestation failed", "status": "FAIL"}, indent=2, sort_keys=True))
        return 1

    before = git_text("status", "--porcelain=v1", "--untracked-files=all")
    anchor, relative = CONSUMERS[name]
    args = list(consumer_args or [])
    with temporary_worktree(anchor) as worktree:
        script = worktree / relative
        if not script.is_file():
            print(json.dumps({"artifact": CURRENT_STEM, "consumer": name, "error": "historical consumer missing", "status": "FAIL"}, indent=2, sort_keys=True))
            return 1
        env = os.environ.copy()
        env.setdefault("GITHUB_REF_NAME", BRANCH)
        env.setdefault("GITHUB_HEAD_REF", BRANCH)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        cp = run(sys.executable, str(script), *args, cwd=worktree, env=env)
        if cp.stdout:
            print(cp.stdout, end="" if cp.stdout.endswith("\n") else "\n")
        if cp.stderr:
            print(cp.stderr, file=sys.stderr, end="" if cp.stderr.endswith("\n") else "\n")
        if cp.returncode:
            print(json.dumps({"artifact": CURRENT_STEM, "anchor": anchor, "consumer": name, "historical_return_code": cp.returncode, "status": "FAIL"}, indent=2, sort_keys=True))
            return cp.returncode

    after = git_text("status", "--porcelain=v1", "--untracked-files=all")
    if after != before:
        print(json.dumps({"artifact": CURRENT_STEM, "consumer": name, "error": "source repository status changed during replay", "status": "FAIL"}, indent=2, sort_keys=True))
        return 1
    print(json.dumps({"artifact": CURRENT_STEM, "anchor": anchor, "consumer": name, "frozen_surface_replayed": True, "successor_overlay_attested": True, "status": "PASS"}, indent=2, sort_keys=True))
    return 0



def verify_failure_matrix() -> int:
    if successor_overlay_attestation("auto") is None:
        print(json.dumps({"artifact": CURRENT_STEM, "error": "v0.9 successor attestation failed", "status": "FAIL"}, indent=2, sort_keys=True))
        return 1
    before = git_text("status", "--porcelain=v1", "--untracked-files=all")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("CI", "true")
    env.setdefault("GITHUB_ACTIONS", "true")
    env.setdefault("GITHUB_EVENT_NAME", "push")
    env.setdefault("GITHUB_REF", "refs/heads/" + BRANCH)
    env.setdefault("GITHUB_REF_NAME", BRANCH)
    env.setdefault("GITHUB_HEAD_REF", "")
    env.setdefault("GITHUB_SHA", git_text("rev-parse", "HEAD"))
    results: list[dict[str, Any]] = []
    for entry in FAILED_WORKFLOW_MATRIX:
        command = list(entry["command"])
        if command and command[0] == "python":
            command[0] = sys.executable
        cp = run(*command, env=env)
        result = {
            "ordinal": entry["ordinal"],
            "run_id": entry["run_id"],
            "workflow": entry["workflow"],
            "workflow_file": entry["workflow_file"],
            "failure_class": entry["failure_class"],
            "return_code": cp.returncode,
            "status": "PASS" if cp.returncode == 0 else "FAIL",
        }
        results.append(result)
        if cp.returncode:
            if cp.stdout:
                print(cp.stdout, end="" if cp.stdout.endswith("\\n") else "\\n")
            if cp.stderr:
                print(cp.stderr, file=sys.stderr, end="" if cp.stderr.endswith("\\n") else "\\n")
            print(json.dumps({"artifact": CURRENT_STEM, "failed_workflow": result, "matrix": results, "status": "FAIL"}, indent=2, sort_keys=True))
            return cp.returncode
    after = git_text("status", "--porcelain=v1", "--untracked-files=all")
    if after != before:
        print(json.dumps({"artifact": CURRENT_STEM, "error": "source status changed during failure-matrix replay", "status": "FAIL"}, indent=2, sort_keys=True))
        return 1
    print(json.dumps({"artifact": CURRENT_STEM, "failed_workflow_count": 7, "matrix": results, "one_to_one": True, "status": "PASS"}, indent=2, sort_keys=True))
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("auto", "working-tree", "committed", "package-only"), default="auto")
    parser.add_argument("--emit-overlay-json", action="store_true")
    parser.add_argument("--replay-consumer", choices=tuple(sorted(CONSUMERS)))
    parser.add_argument("--consumer-arg", action="append", default=[])
    parser.add_argument("--verify-failure-matrix", action="store_true")
    args = parser.parse_args()

    if args.verify_failure_matrix:
        return verify_failure_matrix()

    if args.replay_consumer:
        return replay_consumer(args.replay_consumer, args.consumer_arg)

    mode = args.mode
    if mode == "auto":
        try:
            mode = detect_mode()
        except Exception:
            mode = "indeterminate"
    try:
        overlay = verify_package_only() if mode == "package-only" else successor_overlay_attestation(mode)
        if overlay is None:
            raise RuntimeError("predecessor-consumer closure attestation failed")
        result: dict[str, Any] = {
            "artifact": CURRENT_STEM,
            "repository": REPOSITORY,
            "branch": BRANCH,
            "mode": mode,
            "pre_repair_head": PRE_REPAIR_HEAD,
            "pre_repair_parent": PRE_REPAIR_PARENT,
            "changed_path_count": len(ALL_PATHS),
            "controlled_modified_path_count": len(CONTROLLED),
            "additive_path_count": len(ADDITIVE),
            "historical_consumer_count": len(CONSUMERS),
            "frozen_ledgers_rewritten": False,
            "historical_records_rewritten": False,
            "proof_sources_rewritten": False,
            "schemas_or_fixtures_rewritten": False,
            "history_rewritten": False,
            "commit_performed": False,
            "push_performed": False,
            "release_actions_performed": False,
            "status": "PASS",
        }
        if args.emit_overlay_json:
            result["overlay"] = overlay
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"artifact": CURRENT_STEM, "mode": mode, "error": str(exc), "status": "FAIL"}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
