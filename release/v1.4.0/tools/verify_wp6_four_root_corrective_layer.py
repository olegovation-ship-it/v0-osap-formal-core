#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterator

ROOT = Path(__file__).resolve().parents[3]
PREDECESSOR = "96a6164fd4fe6b8a85992df746672e4261fed8d3"
BRANCH = "v1.4.0-development"
POST_MERGE = ".github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml"
SUCCESSOR_ATTESTATION = ".github/workflows/gate3-cluster-b-wp6-successor-attestation-layer.yml"
WP6_AUDIT = ".github/workflows/gate3-cluster-b-wp6.yml"
WORKFLOW = ".github/workflows/gate3-cluster-b-wp6-four-root-corrective-layer.yml"
MANIFEST = "release/v1.4.0/GATE3_CLUSTER_B_WP6_FOUR_ROOT_CORRECTIVE_LAYER_MANIFEST.json"
LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP6_FOUR_ROOT_CORRECTIVE_LAYER_SHA256SUMS.txt"
VERIFIER = "release/v1.4.0/tools/verify_wp6_four_root_corrective_layer.py"
TEST = "tests/test_gate3_cluster_b_wp6_four_root_corrective_layer.py"
MODIFIED_PATHS = sorted([POST_MERGE, SUCCESSOR_ATTESTATION, WP6_AUDIT])
ADDITIVE_PATHS = sorted([WORKFLOW, MANIFEST, LEDGER, VERIFIER, TEST])
ATTESTED_PATHS = sorted([WORKFLOW, MANIFEST, VERIFIER, TEST])
SURFACE_PATHS = sorted(MODIFIED_PATHS + ADDITIVE_PATHS)
EXPECTED_BLOBS = {".github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml": "4b953e258361f730b96953779ba639177ddc1cf5", ".github/workflows/gate3-cluster-b-wp6-successor-attestation-layer.yml": "952e01b88485c09b5529f1079cff3e2ae724dede", ".github/workflows/gate3-cluster-b-wp6.yml": "029b1c233868b6edc2529a9cded8da81188ecfdf"}
EXPECTED_IMMUTABLE_SHA256 = {".github/workflows/gate3-cluster-b-wp6-four-root-corrective-layer.yml": "6550757a8117f0113bea6a555d5b9cee1edf80225a161c9e7b1ef599984ef52e", ".github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml": "268b17a8f7ac20e65cd87a88785e856578cbd42a819fed905065bbe1f5bce190", ".github/workflows/gate3-cluster-b-wp6.yml": "833a9f7f8f75ae39e20b0eb7144f1954f3c075d22f421ce70a2e9ac9b005775d"}
EXPECTED_REPLAY_GROUPS = json.loads('{"successor-attestation":{"anchor":"e1b3928c0759e2ed61624dabf4cbc505982c379f","jobs":{"replay-matrix":{"cli_invocation":["--mode","committed","--replay-workflow","successor-attestation","--job","replay-matrix"],"commands":[["python","release/v1.4.0/tools/verify_wp6_successor_attestation_layer.py","--mode","committed","--verify-replay-matrix"]]}}},"wp6-audit":{"jobs":{"baseline-lock":{"anchor":"8a692859b2e02a8c9fccc008f76bb24218716f40","commands":[["python","scripts/verify_gate3_cluster_b_wp6.py","--job","baseline-lock"]]},"decision-firewall":{"anchor":"8a692859b2e02a8c9fccc008f76bb24218716f40","commands":[["python","release/v1.4.0/tools/patch_wp6_allowlist.py"],["python","scripts/verify_gate3_cluster_b_wp6.py","--job","decision-firewall"],["git","diff","--check","b3798367af960ff3b588778966c5e233d89e72ab","--"]]},"replay-claims":{"anchor":"8a692859b2e02a8c9fccc008f76bb24218716f40","commands":[["python","scripts/replay_gate3_cluster_b_wp6.py","--check"],["python","scripts/verify_gate3_cluster_b_wp6.py","--job","replay-claims"]]},"schemas-fixtures-python":{"anchor":"8a692859b2e02a8c9fccc008f76bb24218716f40","commands":[["python","-m","pytest","-q","-p","no:cacheprovider","--deselect","tests/test_gate3_cluster_b_wp5_post_merge_closeout.py::test_wp5_post_merge_closeout"]]}}},"wp6-post-merge":{"jobs":{"closeout-verifier":{"anchor":"8a692859b2e02a8c9fccc008f76bb24218716f40","commands":[["python","scripts/verify_gate3_cluster_b_wp6_post_merge_closeout.py","--package-only"]],"overlay_required":true},"dedicated-tests":{"phases":[{"anchor":"8a692859b2e02a8c9fccc008f76bb24218716f40","commands":[["python","-m","pytest","-q","-p","no:cacheprovider","tests/test_gate3_cluster_b_wp6_post_merge_closeout.py"]],"overlay_required":true},{"anchor":"33e292b6ae2e5f35135c9a8e35c9697901cae829","commands":[["python","-m","pytest","-q","-p","no:cacheprovider","tests/test_gate3_cluster_b_wp6_post_merge_ci_context_repair.py","tests/test_gate3_cluster_b_wp6_post_merge_push_context_repair.py"]],"overlay_required":false}]},"hosted-ci-context-repair":{"anchor":"33e292b6ae2e5f35135c9a8e35c9697901cae829","commands":[["python","release/v1.4.0/tools/verify_wp6_post_merge_ci_context_repair.py","--ci"],["python","release/v1.4.0/tools/verify_wp6_post_merge_push_context_repair.py","--mode","committed"]],"runtime_dependencies":["pytest","jsonschema"]}}}}')
EXPECTED_OVERLAY = {
    "application_environment": "DISPOSABLE_REPLAY_ONLY",
    "base": "8a692859b2e02a8c9fccc008f76bb24218716f40",
    "expected_path_count": 30,
    "pathset_sha256": "be83d9ad87a96584db78e7250f832400b0950a64bc11612e8cf1428465e25b33",
    "source": "79c531885f90fb9c0dbd9dd4a223d8fc9a5f74c9",
}
EXPECTED_TOP_LEVEL_FIELDS = sorted([
    "additive_path_count", "additive_paths", "artifact_id", "branch",
    "byte_contract", "historical_artifact_policy", "historical_overlay",
    "ledger_attested_path_count", "ledger_attested_paths", "ledger_path",
    "ledger_self_excluded", "modified_path_count", "modified_paths",
    "path_roles", "predecessor", "replacement_count", "replay_anchors",
    "replay_groups", "root_coverage", "total_path_count", "transformations",
    "unresolved_dependency_count", "version",
])


def run(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None,
        text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd or ROOT, capture_output=True, text=text,
                          check=False, env=env)


def require(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None,
            text: bool = True) -> subprocess.CompletedProcess:
    cp = run(*args, cwd=cwd, env=env, text=text)
    if cp.returncode:
        out = cp.stdout if text else cp.stdout.decode("utf-8", errors="replace")
        err = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise RuntimeError("$ " + " ".join(args) + "\n" + out + err)
    return cp


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def parse_ledger_bytes(data: bytes) -> list[tuple[str, str]]:
    if not data.endswith(b"\n") or b"\r" in data:
        raise RuntimeError("LEDGER_BYTE_CONTRACT_FAILURE")
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for ordinal, line in enumerate(data.decode("utf-8").splitlines(), 1):
        if line.count("  ") != 1:
            raise RuntimeError(f"LEDGER_SERIALIZATION_FAILURE:{ordinal}")
        digest, path = line.split("  ", 1)
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise RuntimeError(f"LEDGER_DIGEST_FAILURE:{ordinal}")
        if not path or path in seen:
            raise RuntimeError(f"LEDGER_PATH_FAILURE:{ordinal}")
        seen.add(path)
        rows.append((digest, path))
    return rows


def predecessor_provider_from_environment(root: Path = ROOT) -> Callable[[str], bytes]:
    snapshot = os.environ.get("V0_OSAP_PREDECESSOR_BLOB_DIR")
    if snapshot:
        base = Path(snapshot)
        return lambda relative: (base / relative).read_bytes()
    def provider(relative: str) -> bytes:
        cp = require("git", "cat-file", "blob", f"{PREDECESSOR}:{relative}", cwd=root, text=False)
        return cp.stdout
    return provider


def load_manifest(root: Path = ROOT) -> dict[str, Any]:
    raw = (root / MANIFEST).read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if raw != canonical_json(value):
        raise RuntimeError("MANIFEST_CANONICAL_JSON_FAILURE")
    return value


def validate_manifest(manifest: dict[str, Any]) -> None:
    if sorted(manifest) != EXPECTED_TOP_LEVEL_FIELDS:
        raise RuntimeError("MANIFEST_TOP_LEVEL_FIELD_FAILURE")
    scalar = {
        "additive_path_count": 5,
        "branch": BRANCH,
        "ledger_attested_path_count": 4,
        "ledger_path": LEDGER,
        "ledger_self_excluded": True,
        "modified_path_count": 3,
        "replacement_count": 8,
        "total_path_count": 8,
        "unresolved_dependency_count": 0,
        "version": "1.1",
    }
    for key, expected in scalar.items():
        if manifest.get(key) != expected:
            raise RuntimeError("MANIFEST_SCALAR_FAILURE:" + key)
    if manifest.get("artifact_id") != "V0_OSAP_GATE3_CLUSTER_B_WP6_FOUR_ROOT_CORRECTIVE_LAYER":
        raise RuntimeError("MANIFEST_ARTIFACT_ID_FAILURE")
    if manifest.get("modified_paths") != MODIFIED_PATHS:
        raise RuntimeError("MANIFEST_MODIFIED_PATH_FAILURE")
    if manifest.get("additive_paths") != ADDITIVE_PATHS:
        raise RuntimeError("MANIFEST_ADDITIVE_PATH_FAILURE")
    if manifest.get("ledger_attested_paths") != ATTESTED_PATHS:
        raise RuntimeError("MANIFEST_ATTESTED_PATH_FAILURE")
    if manifest.get("historical_overlay") != EXPECTED_OVERLAY:
        raise RuntimeError("MANIFEST_OVERLAY_FAILURE")
    if manifest.get("replay_groups") != EXPECTED_REPLAY_GROUPS:
        raise RuntimeError("MANIFEST_REPLAY_PERIMETER_FAILURE")
    roots = manifest.get("root_coverage")
    if not isinstance(roots, dict) or sorted(roots) != ["ROOT_1", "ROOT_2", "ROOT_3", "ROOT_4"]:
        raise RuntimeError("ROOT_COVERAGE_KEY_FAILURE")
    if any(value.get("status") != "COMPLETE" for value in roots.values()):
        raise RuntimeError("ROOT_COVERAGE_STATUS_FAILURE")
    transformations = manifest.get("transformations")
    if not isinstance(transformations, list) or len(transformations) != 3:
        raise RuntimeError("MANIFEST_TRANSFORMATION_COUNT_FAILURE")
    if [item.get("path") for item in transformations] != [POST_MERGE, SUCCESSOR_ATTESTATION, WP6_AUDIT]:
        raise RuntimeError("MANIFEST_TRANSFORMATION_ORDER_FAILURE")
    if sum(int(item.get("replacement_count", -1)) for item in transformations) != 8:
        raise RuntimeError("MANIFEST_REPLACEMENT_COUNT_FAILURE")


def transformed_modified_bytes(manifest: dict[str, Any],
                               provider: Callable[[str], bytes] | None = None) -> dict[str, bytes]:
    validate_manifest(manifest)
    provider = provider or predecessor_provider_from_environment()
    output: dict[str, bytes] = {}
    for transformation in manifest["transformations"]:
        path = transformation["path"]
        source = provider(path)
        if git_blob_sha1(source) != transformation.get("predecessor_blob_sha1"):
            raise RuntimeError("PREDECESSOR_BLOB_MISMATCH:" + path)
        if transformation.get("predecessor_blob_sha1") != EXPECTED_BLOBS[path]:
            raise RuntimeError("PREDECESSOR_BLOB_IDENTITY_FAILURE:" + path)
        text = source.decode("utf-8")
        replacements = transformation.get("replacements")
        if not isinstance(replacements, list) or len(replacements) != transformation.get("replacement_count"):
            raise RuntimeError("REPLACEMENT_LIST_FAILURE:" + path)
        for ordinal, item in enumerate(replacements, 1):
            if item.get("ordinal") != ordinal:
                raise RuntimeError("REPLACEMENT_ORDINAL_FAILURE")
            old = item.get("old")
            new = item.get("new")
            if not isinstance(old, str) or not isinstance(new, str):
                raise RuntimeError("REPLACEMENT_TYPE_FAILURE")
            count = text.count(old)
            if count != 1 or item.get("predecessor_anchor_count") != 1:
                raise RuntimeError(f"NON_UNIQUE_REPLACEMENT:{path}:{ordinal}")
            if item.get("old_sha256") != sha256_bytes(old.encode("utf-8")):
                raise RuntimeError(f"OLD_SHA256_FAILURE:{path}:{ordinal}")
            if item.get("new_sha256") != sha256_bytes(new.encode("utf-8")):
                raise RuntimeError(f"NEW_SHA256_FAILURE:{path}:{ordinal}")
            text = text.replace(old, new, 1)
        data = text.encode("utf-8")
        if not data.endswith(b"\n") or b"\r" in data:
            raise RuntimeError("MODIFIED_BYTE_CONTRACT_FAILURE:" + path)
        output[path] = data
    if sorted(output) != MODIFIED_PATHS:
        raise RuntimeError("MODIFIED_SURFACE_COVERAGE_FAILURE")
    return output


def validate_modified_surface(manifest: dict[str, Any], root: Path = ROOT,
                              provider: Callable[[str], bytes] | None = None) -> dict[str, bytes]:
    expected = transformed_modified_bytes(manifest, provider)
    for path, data in expected.items():
        if (root / path).read_bytes() != data:
            raise RuntimeError("MODIFIED_SURFACE_MISMATCH:" + path)
    for path, expected_digest in EXPECTED_IMMUTABLE_SHA256.items():
        if sha256_bytes((root / path).read_bytes()) != expected_digest:
            raise RuntimeError("IMMUTABLE_STREAM_IDENTITY_FAILURE:" + path)
    return expected


def validate_additive_predecessor_absence(provider: Callable[[str], bytes] | None = None) -> None:
    snapshot = os.environ.get("V0_OSAP_PREDECESSOR_BLOB_DIR")
    if snapshot:
        for path in ADDITIVE_PATHS:
            if (Path(snapshot) / path).exists():
                raise RuntimeError("ADDITIVE_PREDECESSOR_PRESENCE:" + path)
        return
    for path in ADDITIVE_PATHS:
        cp = run("git", "cat-file", "-e", f"{PREDECESSOR}:{path}")
        if cp.returncode == 0:
            raise RuntimeError("ADDITIVE_PREDECESSOR_PRESENCE:" + path)


def validate_ledger(root: Path = ROOT) -> list[tuple[str, str]]:
    rows = parse_ledger_bytes((root / LEDGER).read_bytes())
    if len(rows) != 4:
        raise RuntimeError("LEDGER_ENTRY_COUNT_FAILURE")
    paths = [path for _, path in rows]
    if paths != ATTESTED_PATHS or LEDGER in paths:
        raise RuntimeError("LEDGER_SELF_EXCLUSION_OR_ORDER_FAILURE")
    for digest, path in rows:
        if sha256_bytes((root / path).read_bytes()) != digest:
            raise RuntimeError("LEDGER_DIGEST_REPLAY_FAILURE:" + path)
    return rows


def validate_syntax(root: Path = ROOT) -> None:
    import yaml
    for path in [POST_MERGE, SUCCESSOR_ATTESTATION, WP6_AUDIT, WORKFLOW]:
        value = yaml.safe_load((root / path).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise RuntimeError("YAML_PARSE_FAILURE:" + path)
    for path in [VERIFIER, TEST]:
        text = (root / path).read_text(encoding="utf-8")
        ast.parse(text, filename=path)
        compile(text, path, "exec")


def overlay_paths() -> list[str]:
    base = EXPECTED_OVERLAY["base"]
    source = EXPECTED_OVERLAY["source"]
    cp = require("git", "diff", "--name-only", "--diff-filter=A", base, source, "--")
    paths = [line for line in cp.stdout.splitlines() if line]
    serialized = ("\n".join(sorted(paths)) + "\n").encode("utf-8")
    if len(paths) != EXPECTED_OVERLAY["expected_path_count"]:
        raise RuntimeError("HISTORICAL_OVERLAY_PATH_COUNT_FAILURE")
    if sha256_bytes(serialized) != EXPECTED_OVERLAY["pathset_sha256"]:
        raise RuntimeError("HISTORICAL_OVERLAY_PATHSET_FAILURE")
    return sorted(paths)


@contextlib.contextmanager
def detached_worktree(anchor: str) -> Iterator[Path]:
    temp_root = Path(tempfile.mkdtemp(prefix="v0-osap-four-root-replay-"))
    worktree = temp_root / "worktree"
    added = False
    cleanup_failure: str | None = None
    try:
        require("git", "cat-file", "-e", anchor + "^{commit}", cwd=ROOT)
        require("git", "worktree", "add", "--detach", str(worktree), anchor, cwd=ROOT)
        added = True
        yield worktree
    finally:
        active_exception = sys.exc_info()[0] is not None
        if added:
            cp = run("git", "worktree", "remove", "--force", str(worktree), cwd=ROOT)
            if cp.returncode:
                cleanup_failure = (
                    "DETACHED_WORKTREE_REMOVE_FAILURE:"
                    + str(worktree)
                    + "\n"
                    + cp.stdout
                    + cp.stderr
                )
        shutil.rmtree(temp_root, ignore_errors=True)
        if cleanup_failure is not None and not active_exception:
            raise RuntimeError(cleanup_failure)


def execute_phase(anchor: str, commands: list[list[str]], overlay_required: bool) -> list[dict[str, Any]]:
    with detached_worktree(anchor) as worktree:
        if overlay_required:
            for relative in overlay_paths():
                target = worktree / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(require("git", "show", f"{EXPECTED_OVERLAY['source']}:{relative}", text=False).stdout)
        env = os.environ.copy()
        env.update({
            "CI": "true", "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "push",
            "GITHUB_REF": "refs/heads/" + BRANCH, "GITHUB_REF_NAME": BRANCH,
            "GIT_OPTIONAL_LOCKS": "0", "PYTHONDONTWRITEBYTECODE": "1",
        })
        results = []
        for command in commands:
            resolved = list(command)
            if resolved and resolved[0] == "python":
                resolved[0] = sys.executable
            cp = run(*resolved, cwd=worktree, env=env)
            results.append({"command": command, "return_code": cp.returncode})
            if cp.returncode:
                raise RuntimeError("REPLAY_COMMAND_FAILURE:" + json.dumps(results[-1], sort_keys=True) + "\n" + cp.stdout + cp.stderr)
        return results


def normalize_job_phases(workflow: str, job: str) -> list[dict[str, Any]]:
    groups = EXPECTED_REPLAY_GROUPS
    if workflow not in groups or job not in groups[workflow].get("jobs", {}):
        raise RuntimeError("INVALID_WORKFLOW_JOB_COMBINATION")
    spec = groups[workflow]["jobs"][job]
    if "phases" in spec:
        return spec["phases"]
    return [{
        "anchor": spec.get("anchor", groups[workflow].get("anchor")),
        "commands": spec["commands"],
        "overlay_required": bool(spec.get("overlay_required", False)),
    }]


def replay_job(workflow: str, job: str, execute: bool | None = None) -> dict[str, Any]:
    phases = normalize_job_phases(workflow, job)
    if execute is None:
        execute = os.environ.get("V0_OSAP_PACKAGE_ONLY") != "1"
    results = []
    for phase in phases:
        commands = phase["commands"]
        if not commands or any(not command for command in commands):
            raise RuntimeError("REPLAY_COMMAND_OMISSION")
        record = {
            "anchor": phase["anchor"],
            "commands": commands,
            "overlay_required": bool(phase.get("overlay_required", False)),
        }
        if execute:
            record["execution"] = execute_phase(record["anchor"], commands, record["overlay_required"])
        else:
            record["execution"] = "PACKAGE_ONLY_CONTRACT_REPLAY"
        results.append(record)
    return {"job": job, "phases": results, "status": "PASS", "workflow": workflow}


def repository_snapshot(root: Path = ROOT) -> dict[str, str]:
    if os.environ.get("V0_OSAP_PACKAGE_ONLY") == "1":
        return {"mode": "PACKAGE_ONLY", "tree_sha256": tree_sha256(root)}
    return {
        "head": require("git", "rev-parse", "HEAD", cwd=root).stdout.strip(),
        "status": require("git", "status", "--porcelain=v1", "--untracked-files=all", cwd=root).stdout,
        "refs": require("git", "show-ref", "--head", cwd=root).stdout,
    }


def tree_sha256(root: Path = ROOT) -> str:
    h = hashlib.sha256()
    for relative in SURFACE_PATHS:
        data = (root / relative).read_bytes()
        h.update(relative.encode("utf-8") + b"\0" + data)
    return h.hexdigest()


def verify_four_root_matrix(root: Path = ROOT) -> dict[str, Any]:
    before = repository_snapshot(root)
    manifest = load_manifest(root)
    validate_manifest(manifest)
    validate_modified_surface(manifest, root)
    validate_additive_predecessor_absence()
    validate_ledger(root)
    validate_syntax(root)
    replay_results = []
    for workflow in sorted(EXPECTED_REPLAY_GROUPS):
        for job in sorted(EXPECTED_REPLAY_GROUPS[workflow]["jobs"]):
            replay_results.append(replay_job(workflow, job))
    after = repository_snapshot(root)
    if before != after:
        raise RuntimeError("IMMUTABLE_REPOSITORY_STATE_FAILURE")
    return {
        "additive_path_count": 5,
        "modified_path_count": 3,
        "replay_job_count": len(replay_results),
        "replacement_count": 8,
        "root_coverage": "COMPLETE",
        "status": "PASS",
        "total_path_count": 8,
        "transformation_count": 3,
        "unresolved_dependency_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("committed",), required=True)
    parser.add_argument("--verify-four-root-matrix", action="store_true")
    parser.add_argument("--replay-workflow", choices=tuple(sorted(EXPECTED_REPLAY_GROUPS)))
    parser.add_argument("--job")
    args = parser.parse_args()
    try:
        matrix = args.verify_four_root_matrix
        replay = args.replay_workflow is not None or args.job is not None
        if matrix == replay:
            raise RuntimeError("EXACTLY_ONE_OPERATION_REQUIRED")
        result = verify_four_root_matrix() if matrix else replay_job(str(args.replay_workflow), str(args.job))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "status": "FAIL"}, indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
