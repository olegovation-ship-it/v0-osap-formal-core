#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[3]
REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
BRANCH = "v1.4.0-development"
PREDECESSOR = "be193bd3e3bf46b8235b2472f04a4aab41203493"
PREDECESSOR_PARENT = "3bbe861153cca8123fc9d528921ebc9dc2bb41e5"
PREDECESSOR_TITLE = "repair(wp6): close hosted CI predecessor-consumer closure"
WORKFLOW = ".github/workflows/gate3-cluster-b-wp6-successor-attestation-layer.yml"
MANIFEST = "release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER_MANIFEST.json"
LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER_SHA256SUMS.txt"
VERIFIER = "release/v1.4.0/tools/verify_wp6_successor_attestation_layer.py"
TEST = "tests/test_gate3_cluster_b_wp6_successor_attestation_layer.py"
SUCCESSOR_PATHS = [WORKFLOW, MANIFEST, LEDGER, VERIFIER, TEST]
ATTESTED_SUCCESSOR_PATHS = sorted(path for path in SUCCESSOR_PATHS if path != LEDGER)
V09_LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR_SHA256SUMS.txt"
V09_LEDGER_SHA256 = "a311b72420ceae985f3365caa554a58095a558947a20afe2e147c63074f7a1d0"
V09_PACKAGE_SHA256 = "4402e2ac17eae377ca7d4dc1bc4b4d3789d5040020f43e0821153bb5fa045483"
PROVISIONAL_PATHS = ['.github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml', 'release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt']
V09_PATHS = ['.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR_RECORD.json', 'release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py', 'release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py', 'release/v1.4.0/tools/verify_wp6_hosted_ci_regression_corrective_repair.py', 'scripts/verify_gate3_cluster_b_wp2.py', 'scripts/verify_gate3_cluster_b_wp3.py', 'tests/test_gate3_cluster_b_wp6_hosted_ci_predecessor_consumer_closure_repair.py', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR_SHA256SUMS.txt']
FROZEN_BOUNDARY_PATHS = sorted(set(PROVISIONAL_PATHS + V09_PATHS))
WP3_LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt"
WP5_LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt"
WP3_REPLACEMENTS = ['.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml', 'scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py', 'scripts/verify_gate3_cluster_b_wp2.py', 'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py', 'scripts/verify_gate3_cluster_b_wp3.py', 'scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py']
WP5_REPLACEMENTS = ['release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py', 'release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py']
EXPECTED_MANIFEST = json.loads('{"additive_path_count":5,"additive_paths":[".github/workflows/gate3-cluster-b-wp6-successor-attestation-layer.yml","release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER_MANIFEST.json","release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER_SHA256SUMS.txt","release/v1.4.0/tools/verify_wp6_successor_attestation_layer.py","tests/test_gate3_cluster_b_wp6_successor_attestation_layer.py"],"artifact_id":"V0_OSAP_GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER","branch":"v1.4.0-development","corrective_reconstruction":{"executable_four_root_digest_derivation":true,"explicit_runtime_dependency_closure":{"pip_command":"python -m pip install --disable-pip-version-check pytest jsonschema","python_packages":["jsonschema","pytest"],"status":"CLOSED"},"supersedes_design_version":"0.1","version":"0.2"},"dependency_graph":{"first_stable_non_frozen_boundary":"release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER_SHA256SUMS.txt","higher_order_ledger_required":false,"shared_physical_transitive_path_count":0,"status":"CLOSED"},"four_roots":[{"derivation":"SHA256_OF_CURRENT_PREDECESSOR_BOUNDARY_FILE","expected_sha256":"4f586cbd6624ca12beeeb2724843d8ba0723d1edb5297c23dd5159adae1394c8","kind":"CURRENT_FILE","path":".github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml"},{"derivation":"SHA256_OF_CURRENT_PREDECESSOR_BOUNDARY_FILE","expected_sha256":"c434b920de60134ef492e89067da14812d4da21c9ca21d10a41dfe551d0a32eb","kind":"CURRENT_FILE","path":"release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py"},{"current_ledger_sha256":"f6af9e0941927e4753aa34584d241de12919bd57a4b940758cfef28302963ac2","derivation":"PARSE_CURRENT_LEDGER_REPLACE_EXACT_STALE_ENTRIES_WITH_CURRENT_FILE_SHA256_RESERIALIZE_PRESERVING_ORDER","expected_reconstructed_sha256":"161c2064d81774f9adcc947f9af5ed82273bec9ebd1922c5d997104686d59fc3","kind":"RECONSTRUCTED_LEDGER","path":"release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt","replacement_paths":[".github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml","scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py","scripts/verify_gate3_cluster_b_wp2.py","scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py","scripts/verify_gate3_cluster_b_wp3.py","scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py"]},{"current_ledger_sha256":"66ec9c669ff7fd6376cbffce3f96f65c41ea7a5b055c598fb28a9e14c8f98b34","derivation":"PARSE_CURRENT_LEDGER_REPLACE_EXACT_STALE_ENTRIES_WITH_CURRENT_FILE_SHA256_RESERIALIZE_PRESERVING_ORDER","expected_reconstructed_sha256":"2cafecf875967dc1586bf5a353d671e770d2bba81bd0c775bd06197dd34bef0c","kind":"RECONSTRUCTED_LEDGER","path":"release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt","replacement_paths":["release/v1.4.0/tools/patch_wp5_allowlist.py","release/v1.4.0/tools/patch_wp5_post_merge_allowlist.py","release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py"]}],"frozen_boundary":{"predecessor_v09_artifact_change_count":0,"provisional_paths":[".github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml","release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py","release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt","release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt","release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json","release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json","release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt","release/v1.4.0/GATE3_CLUSTER_B_WP6_EVIDENCE_INPUT_MANIFEST.json","release/v1.4.0/GATE3_CLUSTER_B_WP6_SHA256SUMS.txt"],"provisional_paths_modified":false,"status":"UNCHANGED"},"ledger_path":"release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER_SHA256SUMS.txt","ledger_self_excluded":true,"modified_path_count":0,"predecessor_attestation_boundary":{"commit":"be193bd3e3bf46b8235b2472f04a4aab41203493","parent":"3bbe861153cca8123fc9d528921ebc9dc2bb41e5","title":"repair(wp6): close hosted CI predecessor-consumer closure"},"predecessor_v09_binding":{"committed_ledger_path":"release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR_SHA256SUMS.txt","committed_ledger_sha256":"a311b72420ceae985f3365caa554a58095a558947a20afe2e147c63074f7a1d0","package_sha256":"4402e2ac17eae377ca7d4dc1bc4b4d3789d5040020f43e0821153bb5fa045483","package_sha256_binding_type":"EXTERNAL_IDENTITY_CONFIRMED_BY_FRESH_TERMINAL_EVIDENCE","surface_runtime_verification":"SELF_EXCLUDING_LEDGER_PLUS_PREDECESSOR_COMMIT_BYTES"},"replay_groups":[{"anchor":"c90041d3da5b680b574b910de50d8769d32fbfa9","command":["python","scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py"],"correlation_group":"WP2_POST_MERGE_STALE_SUCCESSOR_BOUNDARY","name":"wp2-post-merge"},{"anchor":"c90041d3da5b680b574b910de50d8769d32fbfa9","command":["python","scripts/verify_gate3_cluster_b_wp3.py"],"correlation_group":"WP3_CANONICAL_STALE_SUCCESSOR_LEDGER","name":"wp3"},{"anchor":"c90041d3da5b680b574b910de50d8769d32fbfa9","command":["python","scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py"],"correlation_group":"WP3_POST_MERGE_STALE_SUCCESSOR_LEDGER","name":"wp3-post-merge"},{"anchor":"14e761e7a34889eebc3c4ef7df17fc56c9267af9","command":["python","scripts/verify_gate3_cluster_b_wp5.py"],"correlation_group":"WP5_CANONICAL_STALE_SUCCESSOR_LEDGER","name":"wp5"},{"anchor":"dba0425c0f98950534bf5c6d407246da58eacd2f","command":["python","scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py","--package-only"],"correlation_group":"WP5_POST_MERGE_STALE_SUCCESSOR_LEDGER","name":"wp5-post-merge"},{"anchor":"14e761e7a34889eebc3c4ef7df17fc56c9267af9","command":["python","scripts/verify_gate3_cluster_b_wp5_sync_helper_repair.py"],"correlation_group":"WP5_SYNC_HELPER_STALE_SUCCESSOR_LEDGER","name":"wp5-sync-helper"}],"repository":"olegovation-ship-it/v0-osap-formal-core","successor_layer_total_path_count":5,"unresolved_dependency_count":0,"version":"0.2"}')
REPLAY_GROUPS = EXPECTED_MANIFEST["replay_groups"]
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def run(*args: str, cwd: Path | None = None, text: bool = True,
        env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=cwd or ROOT,
        capture_output=True,
        text=text,
        check=False,
        env=env,
    )


def require_run(*args: str, cwd: Path | None = None, text: bool = True,
                env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    cp = run(*args, cwd=cwd, text=text, env=env)
    if cp.returncode:
        stdout = cp.stdout if text else cp.stdout.decode("utf-8", errors="replace")
        stderr = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise RuntimeError("$ " + " ".join(args) + "\n" + stdout + stderr)
    return cp


def git_text(*args: str, cwd: Path | None = None) -> str:
    return require_run("git", *args, cwd=cwd).stdout.rstrip("\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(relative: str, root: Path = ROOT) -> str:
    return sha256_bytes((root / relative).read_bytes())


def parse_ledger_bytes(data: bytes, label: str) -> list[tuple[str, str]]:
    if not data.endswith(b"\n"):
        raise RuntimeError(label + " lacks trailing LF")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(label + " is not UTF-8") from exc
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for ordinal, line in enumerate(text.splitlines(), start=1):
        if not line:
            raise RuntimeError(f"{label} contains blank row {ordinal}")
        if line.count("  ") != 1:
            raise RuntimeError(f"{label} row {ordinal} lacks exact two-space separator")
        digest, path = line.split("  ", 1)
        if not HEX64.fullmatch(digest):
            raise RuntimeError(f"{label} row {ordinal} has invalid SHA-256")
        if not path or path in seen:
            raise RuntimeError(f"{label} row {ordinal} has empty or duplicate path")
        seen.add(path)
        rows.append((digest, path))
    return rows


def serialize_ledger(rows: list[tuple[str, str]]) -> bytes:
    return ("".join(f"{digest}  {path}\n" for digest, path in rows)).encode("utf-8")


def reconstruct_ledger(relative: str, replacement_paths: list[str],
                       expected_current_sha256: str,
                       expected_reconstructed_sha256: str) -> dict[str, Any]:
    source = (ROOT / relative).read_bytes()
    current_sha256 = sha256_bytes(source)
    if current_sha256 != expected_current_sha256:
        raise RuntimeError(relative + " current ledger SHA-256 mismatch")
    rows = parse_ledger_bytes(source, relative)
    inventory = [path for _, path in rows]
    if any(path not in inventory for path in replacement_paths):
        missing = sorted(set(replacement_paths) - set(inventory))
        raise RuntimeError(relative + " missing replacement paths: " + repr(missing))
    replacements = {path: sha256_path(path) for path in replacement_paths}
    reconstructed_rows = [
        (replacements.get(path, digest), path)
        for digest, path in rows
    ]
    reconstructed = serialize_ledger(reconstructed_rows)
    reconstructed_sha256 = sha256_bytes(reconstructed)
    if reconstructed_sha256 != expected_reconstructed_sha256:
        raise RuntimeError(
            relative + " reconstructed SHA-256 mismatch: "
            + reconstructed_sha256
        )
    return {
        "current_sha256": current_sha256,
        "path": relative,
        "reconstructed_sha256": reconstructed_sha256,
        "replacement_count": len(replacements),
        "replacement_sha256": replacements,
    }


def verify_manifest() -> None:
    actual_bytes = (ROOT / MANIFEST).read_bytes()
    actual = json.loads(actual_bytes.decode("utf-8"))
    if actual != EXPECTED_MANIFEST:
        raise RuntimeError("successor manifest object mismatch")
    canonical = (
        json.dumps(actual, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if actual_bytes != canonical:
        raise RuntimeError("successor manifest serialization mismatch")
    if actual["predecessor_v09_binding"]["package_sha256"] != V09_PACKAGE_SHA256:
        raise RuntimeError("v0.9 package identity binding mismatch")


def verify_predecessor_identity() -> None:
    require_run("git", "cat-file", "-e", PREDECESSOR + "^{commit}")
    if git_text("rev-parse", PREDECESSOR + "^") != PREDECESSOR_PARENT:
        raise RuntimeError("predecessor parent mismatch")
    if git_text("show", "-s", "--format=%s", PREDECESSOR) != PREDECESSOR_TITLE:
        raise RuntimeError("predecessor title mismatch")
    if run("git", "merge-base", "--is-ancestor", PREDECESSOR, "HEAD").returncode:
        raise RuntimeError("predecessor is not an ancestor of HEAD")


def verify_exact_additive_surface() -> None:
    rows: dict[str, str] = {}
    for line in git_text(
        "diff", "--name-status", "--no-renames", PREDECESSOR, "HEAD"
    ).splitlines():
        if not line:
            continue
        code, path = line.split("\t", 1)
        rows[path] = code
    expected = {path: "A" for path in SUCCESSOR_PATHS}
    if rows != expected:
        raise RuntimeError(
            "successor committed surface mismatch; actual=" + repr(rows)
        )
    for path in SUCCESSOR_PATHS:
        fields = git_text("ls-files", "-s", "--", path).split()
        if len(fields) < 4 or fields[0] != "100644":
            raise RuntimeError("successor file mode mismatch: " + path)
    status = git_text("status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise RuntimeError("repository is not clean: " + repr(status))


def git_show_bytes(commit: str, relative: str) -> bytes:
    cp = require_run("git", "show", commit + ":" + relative, text=False)
    return cp.stdout


def verify_frozen_boundary() -> None:
    for path in FROZEN_BOUNDARY_PATHS:
        current = (ROOT / path).read_bytes()
        predecessor = git_show_bytes(PREDECESSOR, path)
        if current != predecessor:
            raise RuntimeError("predecessor boundary changed: " + path)


def verify_v09_surface() -> dict[str, Any]:
    ledger_bytes = (ROOT / V09_LEDGER).read_bytes()
    if sha256_bytes(ledger_bytes) != V09_LEDGER_SHA256:
        raise RuntimeError("v0.9 self-excluding ledger SHA-256 mismatch")
    rows = parse_ledger_bytes(ledger_bytes, V09_LEDGER)
    if any(path == V09_LEDGER for _, path in rows):
        raise RuntimeError("v0.9 ledger is not self-excluding")
    for expected, path in rows:
        if sha256_path(path) != expected:
            raise RuntimeError("v0.9 artifact digest mismatch: " + path)
    return {
        "artifact_count": len(rows) + 1,
        "ledger_entry_count": len(rows),
        "ledger_sha256": V09_LEDGER_SHA256,
        "predecessor_artifact_change_count": 0,
    }


def verify_four_roots() -> list[dict[str, Any]]:
    direct_roots = [
        (
            ".github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml",
            "4f586cbd6624ca12beeeb2724843d8ba0723d1edb5297c23dd5159adae1394c8",
        ),
        (
            "release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py",
            "c434b920de60134ef492e89067da14812d4da21c9ca21d10a41dfe551d0a32eb",
        ),
    ]
    results: list[dict[str, Any]] = []
    for path, expected in direct_roots:
        actual = sha256_path(path)
        if actual != expected:
            raise RuntimeError("direct root digest mismatch: " + path)
        results.append({
            "derivation": "SHA256_OF_CURRENT_PREDECESSOR_BOUNDARY_FILE",
            "path": path,
            "sha256": actual,
            "status": "PASS",
        })
    results.append(reconstruct_ledger(
        WP3_LEDGER,
        WP3_REPLACEMENTS,
        "f6af9e0941927e4753aa34584d241de12919bd57a4b940758cfef28302963ac2",
        "161c2064d81774f9adcc947f9af5ed82273bec9ebd1922c5d997104686d59fc3",
    ))
    results.append(reconstruct_ledger(
        WP5_LEDGER,
        WP5_REPLACEMENTS,
        "66ec9c669ff7fd6376cbffce3f96f65c41ea7a5b055c598fb28a9e14c8f98b34",
        "2cafecf875967dc1586bf5a353d671e770d2bba81bd0c775bd06197dd34bef0c",
    ))
    if len(results) != 4:
        raise RuntimeError("four-root count mismatch")
    return results


def verify_successor_ledger() -> dict[str, Any]:
    ledger_bytes = (ROOT / LEDGER).read_bytes()
    rows = parse_ledger_bytes(ledger_bytes, LEDGER)
    paths = [path for _, path in rows]
    if paths != ATTESTED_SUCCESSOR_PATHS:
        raise RuntimeError("successor ledger inventory or order mismatch")
    if LEDGER in paths:
        raise RuntimeError("successor ledger is not self-excluding")
    for expected, path in rows:
        if sha256_path(path) != expected:
            raise RuntimeError("successor artifact digest mismatch: " + path)
    return {
        "entry_count": len(rows),
        "ledger_sha256": sha256_bytes(ledger_bytes),
        "self_excluded": True,
    }


def repository_snapshot() -> dict[str, str]:
    index = Path(git_text("rev-parse", "--git-path", "index"))
    if not index.is_absolute():
        index = ROOT / index
    return {
        "head": git_text("rev-parse", "HEAD"),
        "index_sha256": sha256_bytes(index.read_bytes()) if index.is_file() else "ABSENT",
        "refs": git_text("show-ref", "--head"),
        "status": git_text("status", "--porcelain=v1", "--untracked-files=all"),
        "worktrees": git_text("worktree", "list", "--porcelain"),
    }


@contextlib.contextmanager
def detached_worktree(anchor: str) -> Iterator[Path]:
    temp_root = Path(tempfile.mkdtemp(prefix="v0-osap-successor-v02-"))
    worktree = temp_root / "repository"
    added = False
    try:
        require_run("git", "worktree", "add", "--detach", str(worktree), anchor)
        added = True
        yield worktree
    finally:
        if added:
            cp = run("git", "worktree", "remove", "--force", str(worktree))
            if cp.returncode:
                shutil.rmtree(worktree, ignore_errors=True)
                run("git", "worktree", "remove", "--force", str(worktree))
        shutil.rmtree(temp_root, ignore_errors=True)


def replay_historical_groups() -> list[dict[str, Any]]:
    before = repository_snapshot()
    results: list[dict[str, Any]] = []
    environment = os.environ.copy()
    environment["CI"] = "true"
    environment["GITHUB_ACTIONS"] = "true"
    environment["GITHUB_EVENT_NAME"] = "push"
    environment["GITHUB_HEAD_REF"] = BRANCH
    environment["GITHUB_REF"] = "refs/heads/" + BRANCH
    environment["GITHUB_REF_NAME"] = BRANCH
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        for group in REPLAY_GROUPS:
            anchor = str(group["anchor"])
            command = [str(item) for item in group["command"]]
            require_run("git", "cat-file", "-e", anchor + "^{commit}")
            with detached_worktree(anchor) as worktree:
                resolved = list(command)
                if resolved[0] == "python":
                    resolved[0] = sys.executable
                cp = run(*resolved, cwd=worktree, env=environment)
                result = {
                    "anchor": anchor,
                    "command": command,
                    "correlation_group": group["correlation_group"],
                    "name": group["name"],
                    "return_code": cp.returncode,
                    "status": "PASS" if cp.returncode == 0 else "FAIL",
                }
                results.append(result)
                if cp.returncode:
                    raise RuntimeError(
                        "historical replay failed: "
                        + json.dumps(result, sort_keys=True)
                        + "\n"
                        + cp.stdout
                        + cp.stderr
                    )
    finally:
        after = repository_snapshot()
        if after != before:
            raise RuntimeError(
                "source repository changed during replay; before="
                + json.dumps(before, sort_keys=True)
                + "; after="
                + json.dumps(after, sort_keys=True)
            )
    return results


def verify_all(verify_replay_matrix: bool) -> dict[str, Any]:
    verify_predecessor_identity()
    verify_exact_additive_surface()
    verify_manifest()
    verify_frozen_boundary()
    v09 = verify_v09_surface()
    roots = verify_four_roots()
    successor_ledger = verify_successor_ledger()
    replay = replay_historical_groups() if verify_replay_matrix else []
    return {
        "additive_path_count": len(SUCCESSOR_PATHS),
        "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER",
        "branch": BRANCH,
        "dependency_graph_closed": True,
        "executable_four_root_derivation": True,
        "frozen_record_update_required_count": 0,
        "modified_path_count": 0,
        "predecessor": PREDECESSOR,
        "replay_group_count": len(REPLAY_GROUPS),
        "replay_groups": replay,
        "repository": REPOSITORY,
        "roots": roots,
        "runtime_dependencies": ["jsonschema", "pytest"],
        "status": "PASS",
        "successor_ledger": successor_ledger,
        "unresolved_dependency_count": 0,
        "v09": v09,
        "version": "0.2",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("committed",), default="committed")
    parser.add_argument("--verify-replay-matrix", action="store_true")
    args = parser.parse_args()
    try:
        result = verify_all(args.verify_replay_matrix)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({
            "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP6_SUCCESSOR_ATTESTATION_LAYER",
            "error": str(exc),
            "status": "FAIL",
            "version": "0.2",
        }, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
