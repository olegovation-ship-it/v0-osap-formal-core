#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[3]
REPOSITORY = "olegovation-ship-it/v0-osap-formal-core"
BRANCH = "v1.4.0-development"
PREDECESSOR = "e1b3928c0759e2ed61624dabf4cbc505982c379f"
PREDECESSOR_PARENT = "be193bd3e3bf46b8235b2472f04a4aab41203493"
PREDECESSOR_TITLE = "repair(wp6): add successor attestation layer"
WORKFLOW = ".github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml"
MANIFEST = "release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_MANIFEST.json"
LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_SHA256SUMS.txt"
VERIFIER = "release/v1.4.0/tools/verify_wp6_successor_consumer_integration_corrective_layer.py"
TEST = "tests/test_gate3_cluster_b_wp6_successor_consumer_integration_corrective_layer.py"
ADDITIVE_PATHS = sorted([WORKFLOW, MANIFEST, LEDGER, VERIFIER, TEST])
ATTESTED_ADDITIVE_PATHS = sorted(path for path in ADDITIVE_PATHS if path != LEDGER)
PREDECESSOR_V02_VERIFIER = "release/v1.4.0/tools/verify_wp6_successor_attestation_layer.py"


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
    completed = run(*args, cwd=cwd, text=text, env=env)
    if completed.returncode:
        stdout = completed.stdout if text else completed.stdout.decode("utf-8", errors="replace")
        stderr = completed.stderr if text else completed.stderr.decode("utf-8", errors="replace")
        raise RuntimeError("$ " + " ".join(args) + "\n" + stdout + stderr)
    return completed


def git_text(*args: str, cwd: Path | None = None) -> str:
    return require_run("git", *args, cwd=cwd).stdout.rstrip("\n")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(relative: str, root: Path = ROOT) -> str:
    return sha256_bytes((root / relative).read_bytes())


def load_manifest(root: Path = ROOT) -> dict[str, Any]:
    data = (root / MANIFEST).read_bytes()
    if not data.endswith(b"\n"):
        raise RuntimeError("manifest lacks trailing LF")
    actual = json.loads(data.decode("utf-8"))
    canonical = (
        json.dumps(actual, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if data != canonical:
        raise RuntimeError("manifest is not canonical JSON")
    return actual


def parse_ledger(data: bytes, label: str) -> list[tuple[str, str]]:
    if not data.endswith(b"\n"):
        raise RuntimeError(label + " lacks trailing LF")
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for ordinal, line in enumerate(data.decode("utf-8").splitlines(), start=1):
        if not line or line.count("  ") != 1:
            raise RuntimeError(f"{label} row {ordinal} has invalid serialization")
        digest, relative = line.split("  ", 1)
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise RuntimeError(f"{label} row {ordinal} has invalid SHA-256")
        if not relative or relative in seen:
            raise RuntimeError(f"{label} row {ordinal} has empty or duplicate path")
        seen.add(relative)
        rows.append((digest, relative))
    return rows


def diff_entries(base: str, head: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in git_text("diff", "--name-status", "--no-renames", base, head).splitlines():
        if not line:
            continue
        code, relative = line.split("\t", 1)
        rows[relative] = code
    return rows


def expected_surface(manifest: dict[str, Any]) -> dict[str, str]:
    return {
        **{path: "M" for path in manifest["modified_paths"]},
        **{path: "A" for path in manifest["additive_paths"]},
    }


def candidate_heads() -> list[str]:
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
    return candidates


def resolve_surface_head(manifest: dict[str, Any]) -> str:
    expected = expected_surface(manifest)
    for candidate in candidate_heads():
        completed = run("git", "rev-list", "--parents", "-n", "1", candidate)
        if completed.returncode:
            continue
        fields = completed.stdout.split()
        if len(fields) != 2 or fields[1] != PREDECESSOR:
            continue
        try:
            if diff_entries(PREDECESSOR, candidate) == expected:
                return candidate
        except Exception:
            continue
    raise RuntimeError("unable to resolve exact successor-consumer integration layer head")


def verify_predecessor_identity() -> None:
    require_run("git", "cat-file", "-e", PREDECESSOR + "^{commit}")
    if git_text("rev-parse", PREDECESSOR + "^") != PREDECESSOR_PARENT:
        raise RuntimeError("predecessor parent mismatch")
    if git_text("show", "-s", "--format=%s", PREDECESSOR) != PREDECESSOR_TITLE:
        raise RuntimeError("predecessor title mismatch")
    if run("git", "merge-base", "--is-ancestor", PREDECESSOR, "HEAD").returncode:
        raise RuntimeError("predecessor is not an ancestor of HEAD")


def verify_manifest_contract(manifest: dict[str, Any]) -> None:
    if manifest.get("artifact_id") != (
        "V0_OSAP_GATE3_CLUSTER_B_WP6_"
        "SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER"
    ):
        raise RuntimeError("manifest artifact mismatch")
    if manifest.get("version") != "0.1":
        raise RuntimeError("manifest version mismatch")
    if manifest.get("branch") != BRANCH:
        raise RuntimeError("manifest branch mismatch")
    if manifest.get("predecessor") != {
        "commit": PREDECESSOR,
        "parent": PREDECESSOR_PARENT,
        "title": PREDECESSOR_TITLE,
    }:
        raise RuntimeError("manifest predecessor boundary mismatch")
    if manifest.get("modified_path_count") != 8:
        raise RuntimeError("manifest modified-path count mismatch")
    if manifest.get("additive_path_count") != 5:
        raise RuntimeError("manifest additive-path count mismatch")
    if manifest.get("surface_path_count") != 13:
        raise RuntimeError("manifest surface count mismatch")
    if manifest.get("ledger_entry_count") != 4:
        raise RuntimeError("manifest ledger count mismatch")
    if manifest.get("ledger_path") != LEDGER:
        raise RuntimeError("manifest ledger path mismatch")
    if manifest.get("ledger_self_excluded") is not True:
        raise RuntimeError("manifest ledger self-exclusion mismatch")
    if manifest.get("unresolved_dependency_count") != 0:
        raise RuntimeError("manifest unresolved dependency count is nonzero")
    if sorted(manifest.get("additive_paths", [])) != ADDITIVE_PATHS:
        raise RuntimeError("manifest additive inventory mismatch")
    transformations = manifest.get("transformations", [])
    if sorted(item.get("path") for item in transformations) != sorted(
        manifest.get("modified_paths", [])
    ):
        raise RuntimeError("manifest transformation inventory mismatch")


def apply_transform(source: bytes, item: dict[str, Any]) -> bytes:
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(item["path"] + " predecessor bytes are not UTF-8") from exc
    for ordinal, replacement in enumerate(item["replacements"], start=1):
        old = replacement["old"]
        new = replacement["new"]
        count = text.count(old)
        if count != 1:
            raise RuntimeError(
                f"{item['path']} replacement {ordinal} anchor count is {count}, expected 1"
            )
        text = text.replace(old, new, 1)
    result = text.encode("utf-8")
    if not result.endswith(b"\n"):
        raise RuntimeError(item["path"] + " hypothetical bytes lack trailing LF")
    return result


def verify_exact_transforms(manifest: dict[str, Any], surface_head: str) -> None:
    for item in manifest["transformations"]:
        path = item["path"]
        actual_blob = git_text("rev-parse", PREDECESSOR + ":" + path)
        if actual_blob != item["predecessor_blob_sha1"]:
            raise RuntimeError(path + " predecessor Git blob mismatch")
        source = require_run("git", "show", PREDECESSOR + ":" + path, text=False).stdout
        expected = apply_transform(source, item)
        actual = require_run("git", "show", surface_head + ":" + path, text=False).stdout
        if actual != expected:
            raise RuntimeError(path + " does not equal exact hypothetical bytes")
        if (ROOT / path).read_bytes() != expected:
            raise RuntimeError(path + " current checkout differs from exact layer head")
        fields = git_text("ls-tree", surface_head, "--", path).split()
        if not fields or fields[0] != "100644":
            raise RuntimeError(path + " mode mismatch")


def verify_additive_surface(manifest: dict[str, Any], surface_head: str) -> None:
    for path in ADDITIVE_PATHS:
        fields = git_text("ls-tree", surface_head, "--", path).split()
        if not fields or fields[0] != "100644":
            raise RuntimeError(path + " additive mode mismatch")
        current = require_run("git", "show", surface_head + ":" + path, text=False).stdout
        if current != (ROOT / path).read_bytes():
            raise RuntimeError(path + " current/surface-head byte mismatch")
        if not current.endswith(b"\n"):
            raise RuntimeError(path + " lacks trailing LF")


def verify_ledger() -> dict[str, Any]:
    data = (ROOT / LEDGER).read_bytes()
    rows = parse_ledger(data, LEDGER)
    paths = [path for _, path in rows]
    if paths != ATTESTED_ADDITIVE_PATHS:
        raise RuntimeError("corrective ledger inventory or order mismatch")
    for expected, path in rows:
        if sha256_path(path) != expected:
            raise RuntimeError("corrective ledger digest mismatch: " + path)
    return {
        "entry_count": len(rows),
        "ledger_sha256": sha256_bytes(data),
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
    temporary = Path(tempfile.mkdtemp(prefix="v0-osap-successor-consumer-"))
    worktree = temporary / "repository"
    added = False
    try:
        require_run("git", "cat-file", "-e", anchor + "^{commit}")
        require_run("git", "worktree", "add", "--detach", str(worktree), anchor)
        added = True
        yield worktree
    finally:
        if added:
            run("git", "worktree", "remove", "--force", str(worktree))
            run("git", "worktree", "prune")
        shutil.rmtree(temporary, ignore_errors=True)


def replay_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.update({
        "CI": "true",
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_HEAD_REF": BRANCH,
        "GITHUB_REF": "refs/heads/" + BRANCH,
        "GITHUB_REF_NAME": BRANCH,
        "GIT_OPTIONAL_LOCKS": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    return environment


def resolve_commands(manifest: dict[str, Any], workflow: str,
                     job: str | None) -> tuple[str, list[list[str]]]:
    groups = manifest["replay_groups"]
    if workflow not in groups:
        raise RuntimeError("unknown replay workflow: " + workflow)
    group = groups[workflow]
    if workflow == "wp5":
        if not job or job not in group["default_jobs"]:
            raise RuntimeError("WP5 replay requires an exact known job")
        if job == "python-semantics":
            commands = [["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]]
        else:
            commands = [["python", "scripts/verify_gate3_cluster_b_wp5.py", "--job", job]]
        return group["anchor"], commands
    if workflow == "wp6-post-merge":
        jobs = group["jobs"]
        if not job or job not in jobs:
            raise RuntimeError("WP6 post-merge replay requires an exact known job")
        return jobs[job]["anchor"], jobs[job]["commands"]
    if job is not None:
        raise RuntimeError(workflow + " does not accept --job")
    return group["anchor"], group["commands"]


def replay_workflow(manifest: dict[str, Any], workflow: str,
                    job: str | None = None) -> dict[str, Any]:
    verify_all(manifest, verify_predecessor_v02=False)
    before = repository_snapshot()
    anchor, commands = resolve_commands(manifest, workflow, job)
    results: list[dict[str, Any]] = []
    try:
        with detached_worktree(anchor) as worktree:
            environment = replay_environment()
            for command in commands:
                resolved = [str(item) for item in command]
                if resolved and resolved[0] == "python":
                    resolved[0] = sys.executable
                completed = run(*resolved, cwd=worktree, env=environment)
                result = {
                    "command": command,
                    "return_code": completed.returncode,
                    "status": "PASS" if completed.returncode == 0 else "FAIL",
                }
                results.append(result)
                if completed.returncode:
                    raise RuntimeError(
                        "historical replay failed: "
                        + json.dumps(result, sort_keys=True)
                        + "\n"
                        + completed.stdout
                        + completed.stderr
                    )
    finally:
        after = repository_snapshot()
        if after != before:
            raise RuntimeError("source repository changed during historical replay")
    return {
        "anchor": anchor,
        "command_count": len(commands),
        "job": job,
        "results": results,
        "status": "PASS",
        "workflow": workflow,
    }


def verify_predecessor_v02_layer() -> dict[str, Any]:
    before = repository_snapshot()
    try:
        with detached_worktree(PREDECESSOR) as worktree:
            completed = require_run(
                sys.executable,
                PREDECESSOR_V02_VERIFIER,
                "--mode",
                "committed",
                "--verify-replay-matrix",
                cwd=worktree,
                env=replay_environment(),
            )
            result = json.loads(completed.stdout)
            if result.get("status") != "PASS":
                raise RuntimeError("predecessor v0.2 verifier did not report PASS")
    finally:
        after = repository_snapshot()
        if after != before:
            raise RuntimeError("source repository changed during predecessor replay")
    return {
        "anchor": PREDECESSOR,
        "status": "PASS",
        "verifier": PREDECESSOR_V02_VERIFIER,
    }


def verify_all(manifest: dict[str, Any] | None = None,
               verify_predecessor_v02: bool = True) -> dict[str, Any]:
    actual_manifest = manifest or load_manifest()
    verify_predecessor_identity()
    verify_manifest_contract(actual_manifest)
    surface_head = resolve_surface_head(actual_manifest)
    if diff_entries(PREDECESSOR, surface_head) != expected_surface(actual_manifest):
        raise RuntimeError("exact corrective surface mismatch")
    verify_exact_transforms(actual_manifest, surface_head)
    verify_additive_surface(actual_manifest, surface_head)
    ledger = verify_ledger()
    predecessor = (
        verify_predecessor_v02_layer()
        if verify_predecessor_v02
        else {"anchor": PREDECESSOR, "status": "NOT_REPLAYED"}
    )
    status = git_text("status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise RuntimeError("source repository is not clean: " + repr(status))
    return {
        "additive_path_count": 5,
        "artifact": (
            "V0_OSAP_GATE3_CLUSTER_B_WP6_"
            "SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER"
        ),
        "ledger": ledger,
        "modified_path_count": 8,
        "predecessor_v02": predecessor,
        "status": "PASS",
        "surface_head": surface_head,
        "surface_path_count": 13,
        "unresolved_dependency_count": 0,
        "version": "0.1",
    }


def verify_eight_workflow_matrix(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = [
        ("wp2", None),
        ("wp2-post-merge", None),
        ("wp3", None),
        ("wp3-post-merge", None),
        ("wp5", "statement-parity"),
        ("wp5-post-merge", None),
        ("wp5-sync-helper", None),
        ("wp6-post-merge", "hosted-ci-context-repair"),
    ]
    results = [replay_workflow(manifest, workflow, job) for workflow, job in matrix]
    if len(results) != 8 or any(item["status"] != "PASS" for item in results):
        raise RuntimeError("eight-workflow replay matrix did not close")
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("committed",), default="committed")
    parser.add_argument("--replay-workflow")
    parser.add_argument("--job")
    parser.add_argument("--verify-eight-workflow-matrix", action="store_true")
    args = parser.parse_args()
    try:
        manifest = load_manifest()
        result = verify_all(manifest)
        if args.replay_workflow:
            result["replay"] = replay_workflow(manifest, args.replay_workflow, args.job)
        if args.verify_eight_workflow_matrix:
            result["workflow_matrix"] = verify_eight_workflow_matrix(manifest)
            result["workflow_matrix_count"] = 8
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({
            "artifact": (
                "V0_OSAP_GATE3_CLUSTER_B_WP6_"
                "SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER"
            ),
            "error": str(exc),
            "status": "FAIL",
            "version": "0.1",
        }, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
