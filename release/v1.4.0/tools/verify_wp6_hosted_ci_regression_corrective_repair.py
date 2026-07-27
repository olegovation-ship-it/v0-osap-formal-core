#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
BRANCH = "v1.4.0-development"
PRE_REPAIR_HEAD = "59fa5076fdabf74b832fb985947253eaaecca4ae"
PRE_REPAIR_PARENT = "33e292b6ae2e5f35135c9a8e35c9697901cae829"
PREVIOUS_REPAIR_HEAD = PRE_REPAIR_PARENT
PREVIOUS_REPAIR_PARENT = "ba32d8e855a79461fdcda14740acab86aafcb17a"
CANONICAL_WP6_HEAD = "8a692859b2e02a8c9fccc008f76bb24218716f40"

PREVIOUS_STEM = (
    "GATE3_CLUSTER_B_WP6_POST_MERGE_PUSH_CONTEXT_COMPATIBILITY_"
    "AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR"
)
POST_COMMIT_STEM = "GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR"
CURRENT_STEM = "GATE3_CLUSTER_B_WP6_HOSTED_CI_REGRESSION_CORRECTIVE_REPAIR"

PREVIOUS_MANIFEST = f"release/v1.4.0/{PREVIOUS_STEM}_MANIFEST.json"
PREVIOUS_LEDGER = f"release/v1.4.0/{PREVIOUS_STEM}_SHA256SUMS.txt"
POST_COMMIT_MANIFEST = f"release/v1.4.0/{POST_COMMIT_STEM}_MANIFEST.json"
POST_COMMIT_LEDGER = f"release/v1.4.0/{POST_COMMIT_STEM}_SHA256SUMS.txt"
CURRENT_MANIFEST = f"release/v1.4.0/{CURRENT_STEM}_MANIFEST.json"
CURRENT_RECORD = f"release/v1.4.0/{CURRENT_STEM}_RECORD.json"
CURRENT_LEDGER = f"release/v1.4.0/{CURRENT_STEM}_SHA256SUMS.txt"
CURRENT_DOC = "docs/gate3/cluster_b/WP6_HOSTED_CI_REGRESSION_CORRECTIVE_REPAIR.md"
CURRENT_VERIFIER = "release/v1.4.0/tools/verify_wp6_hosted_ci_regression_corrective_repair.py"
CURRENT_TEST = "tests/test_gate3_cluster_b_wp6_hosted_ci_regression_corrective_repair.py"

CONTROLLED = [
    'release/v1.4.0/tools/patch_wp6_allowlist.py',
    'release/v1.4.0/tools/verify_wp6_post_commit_regression_closure_repair.py',
    'release/v1.4.0/tools/verify_wp6_post_merge_push_context_repair.py',
    'scripts/build_gate3_cluster_b_wp2.py',
    'scripts/verify_gate3_cluster_b_wp2.py',
    'scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py',
    'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py',
    'scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py',
    'scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py',
    'scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py',
    'scripts/build_gate3_cluster_b_wp6.py',
    'scripts/verify_gate3_cluster_b_wp6.py',
    'scripts/verify_gate3_cluster_b_wp6_post_merge_closeout.py',
    'scripts/verify_v1_3_0_post_merge_legacy_lifecycle_compatibility.py',
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

FROZEN_PATHS = [
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SHA256SUMS.txt",
    PREVIOUS_LEDGER,
    POST_COMMIT_LEDGER,
]

EXPECTED_TITLES = {
    PREVIOUS_REPAIR_HEAD: (
        "repair(wp6): restore post-merge push-context compatibility "
        "and predecessor workflow isolation"
    ),
    PRE_REPAIR_HEAD: "repair(wp6): close post-commit regression failures",
}


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
        raise RuntimeError(
            (cp.stdout + cp.stderr).decode(errors="replace").strip()
        )
    return cp.stdout


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(relative: str) -> str:
    return sha256_bytes((ROOT / relative).read_bytes())


def blob(commit: str, relative: str) -> bytes:
    return git_bytes("show", f"{commit}:{relative}")


def blob_sha256(commit: str, relative: str) -> str:
    return sha256_bytes(blob(commit, relative))


def parse_ledger_bytes(value: bytes) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in value.decode("utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        if relative in entries:
            raise RuntimeError("duplicate ledger path: " + relative)
        entries[relative] = digest
    return entries


def parse_ledger_path(relative: str) -> dict[str, str]:
    return parse_ledger_bytes((ROOT / relative).read_bytes())


def status_entries() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in git_text(
        "status", "--porcelain=v1", "--untracked-files=all"
    ).splitlines():
        if len(line) < 4 or " -> " in line:
            raise RuntimeError("invalid status entry: " + repr(line))
        rows[line[3:]] = line[:2]
    return rows


def diff_entries(base: str, head: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in git_text(
        "diff", "--name-status", "--no-renames", base, head
    ).splitlines():
        if not line.strip():
            continue
        code, relative = line.split("\t", 1)
        rows[relative] = code
    return rows


def expected_codes(
    controlled: list[str], additive: list[str], mode: str
) -> dict[str, str]:
    if mode == "working-tree":
        return {
            **{path: " M" for path in controlled},
            **{path: "??" for path in additive},
        }
    return {
        **{path: "M" for path in controlled},
        **{path: "A" for path in additive},
    }


def require_exact_entries(
    actual: dict[str, str], expected: dict[str, str], label: str
) -> None:
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        wrong = sorted(
            path
            for path in set(actual) & set(expected)
            if actual[path] != expected[path]
        )
        raise RuntimeError(
            f"{label} mismatch; missing={missing!r}; extra={extra!r}; "
            f"wrong={[(p, actual[p], expected[p]) for p in wrong]!r}"
        )


def load_json_blob(commit: str, relative: str) -> dict:
    return json.loads(blob(commit, relative).decode("utf-8"))


def verify_commit_identity(
    commit: str, parent: str, expected_title: str
) -> None:
    if git_text("rev-parse", f"{commit}^") != parent:
        raise RuntimeError("commit parent mismatch: " + commit)
    if git_text("show", "-s", "--format=%s", commit) != expected_title:
        raise RuntimeError("commit title mismatch: " + commit)
    if git_text("rev-list", "--parents", "-n", "1", commit).count(" ") != 1:
        raise RuntimeError("commit is not an ordinary one-parent commit: " + commit)


def verify_fixed_layer(
    *,
    parent: str,
    head: str,
    manifest_path: str,
    ledger_path: str,
) -> dict[str, str]:
    manifest = load_json_blob(head, manifest_path)
    controlled = list(manifest.get("controlled_modified_paths", []))
    additive = list(manifest.get("additive_paths", []))
    surface = sorted(controlled + additive)
    if manifest.get("changed_path_count") != len(surface):
        raise RuntimeError("fixed-layer manifest path count mismatch")
    if manifest.get("ledger_path") != ledger_path:
        raise RuntimeError("fixed-layer ledger path mismatch")
    require_exact_entries(
        diff_entries(parent, head),
        expected_codes(controlled, additive, "committed"),
        "fixed-layer committed surface",
    )
    ledger = parse_ledger_bytes(blob(head, ledger_path))
    expected_ledger_paths = sorted(path for path in surface if path != ledger_path)
    if sorted(ledger) != expected_ledger_paths:
        raise RuntimeError("fixed-layer ledger inventory mismatch")
    for relative in expected_ledger_paths:
        if blob_sha256(head, relative) != ledger[relative]:
            raise RuntimeError("fixed-layer SHA-256 mismatch: " + relative)
    return ledger


def current_manifest() -> dict:
    return json.loads((ROOT / CURRENT_MANIFEST).read_text(encoding="utf-8"))


def verify_package_only() -> dict[str, str]:
    manifest = current_manifest()
    if manifest.get("version") != "0.3":
        raise RuntimeError("package version mismatch")
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
    if manifest.get("ledger_path") != CURRENT_LEDGER:
        raise RuntimeError("package ledger path mismatch")
    ledger = parse_ledger_path(CURRENT_LEDGER)
    expected = sorted(path for path in ALL_PATHS if path != CURRENT_LEDGER)
    if sorted(ledger) != expected:
        raise RuntimeError("package ledger inventory mismatch")
    for relative in expected:
        if not (ROOT / relative).is_file():
            raise RuntimeError("package file missing: " + relative)
        if sha256_path(relative) != ledger[relative]:
            raise RuntimeError("package SHA-256 mismatch: " + relative)
    outputs = manifest.get("controlled_output_sha256", {})
    if outputs != {path: ledger[path] for path in CONTROLLED}:
        raise RuntimeError("package controlled-output digest mismatch")
    return ledger


def detect_mode() -> str:
    return "working-tree" if status_entries() else "committed"


def verify_current_surface(mode: str) -> dict[str, str]:
    manifest = current_manifest()
    ledger = verify_package_only()
    inputs = manifest.get("controlled_input_sha256", {})
    if inputs != {
        path: blob_sha256(PRE_REPAIR_HEAD, path) for path in CONTROLLED
    }:
        raise RuntimeError("controlled-input digest mismatch")
    if mode == "working-tree":
        if git_text("rev-parse", "HEAD") != PRE_REPAIR_HEAD:
            raise RuntimeError("prepared repair HEAD mismatch")
        require_exact_entries(
            status_entries(),
            expected_codes(CONTROLLED, ADDITIVE, "working-tree"),
            "prepared repair surface",
        )
    elif mode == "committed":
        if status_entries():
            raise RuntimeError("committed repair working tree is not clean")
        if git_text("rev-parse", "HEAD^") != PRE_REPAIR_HEAD:
            raise RuntimeError("committed repair exact parent mismatch")
        require_exact_entries(
            diff_entries(PRE_REPAIR_HEAD, "HEAD"),
            expected_codes(CONTROLLED, ADDITIVE, "committed"),
            "committed repair surface",
        )
    else:
        raise RuntimeError("unsupported mode: " + mode)
    return ledger


def verify_frozen_paths_unchanged() -> None:
    for relative in FROZEN_PATHS:
        if sha256_path(relative) != blob_sha256(PRE_REPAIR_HEAD, relative):
            raise RuntimeError("frozen path changed: " + relative)


def successor_overlay_attestation(mode: str = "auto") -> dict[str, str] | None:
    try:
        if mode == "auto":
            mode = detect_mode()
        if mode == "package-only":
            return verify_package_only()
        verify_commit_identity(
            PREVIOUS_REPAIR_HEAD,
            PREVIOUS_REPAIR_PARENT,
            EXPECTED_TITLES[PREVIOUS_REPAIR_HEAD],
        )
        verify_commit_identity(
            PRE_REPAIR_HEAD,
            PRE_REPAIR_PARENT,
            EXPECTED_TITLES[PRE_REPAIR_HEAD],
        )
        previous = verify_fixed_layer(
            parent=PREVIOUS_REPAIR_PARENT,
            head=PREVIOUS_REPAIR_HEAD,
            manifest_path=PREVIOUS_MANIFEST,
            ledger_path=PREVIOUS_LEDGER,
        )
        post_commit = verify_fixed_layer(
            parent=PRE_REPAIR_PARENT,
            head=PRE_REPAIR_HEAD,
            manifest_path=POST_COMMIT_MANIFEST,
            ledger_path=POST_COMMIT_LEDGER,
        )
        current = verify_current_surface(mode)
        verify_frozen_paths_unchanged()
        combined = {**previous, **post_commit, **current}
        for relative, expected in combined.items():
            path = ROOT / relative
            if path.is_file() and sha256_path(relative) != expected:
                raise RuntimeError("layered overlay SHA-256 mismatch: " + relative)
        return combined
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("auto", "working-tree", "committed", "package-only"),
        default="auto",
    )
    parser.add_argument("--emit-overlay-json", action="store_true")
    args = parser.parse_args()
    mode = args.mode
    if mode == "auto":
        try:
            mode = detect_mode()
        except Exception:
            mode = "indeterminate"
    try:
        overlay = (
            verify_package_only()
            if mode == "package-only"
            else successor_overlay_attestation(mode)
        )
        if overlay is None:
            raise RuntimeError("hosted-CI corrective attestation failed")
        result = {
            "artifact": "WP6_HOSTED_CI_REGRESSION_CORRECTIVE_REPAIR",
            "repository": REPOSITORY,
            "branch": BRANCH,
            "mode": mode,
            "pre_repair_head": PRE_REPAIR_HEAD,
            "pre_repair_parent": PRE_REPAIR_PARENT,
            "changed_path_count": len(ALL_PATHS),
            "controlled_modified_path_count": len(CONTROLLED),
            "additive_path_count": len(ADDITIVE),
            "frozen_ledgers_rewritten": False,
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
        print(
            json.dumps(
                {
                    "artifact": "WP6_HOSTED_CI_REGRESSION_CORRECTIVE_REPAIR",
                    "mode": mode,
                    "error": str(exc),
                    "status": "FAIL",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
