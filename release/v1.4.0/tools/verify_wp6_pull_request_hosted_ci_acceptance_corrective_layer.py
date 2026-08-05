#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import base64
import contextlib
import hashlib
import importlib.util
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
PREDECESSOR = "e53713ed030fc1537726d8381079fecce6c57ac2"
PREDECESSOR_PARENT = "466f820a313366c5f0bd4b23afaea44fe6fdc3b3"
PREDECESSOR_TREE = "cdab3e97da3e7ab09ef985c3b283c86cef26d375"
BASE_SHA = "47614ce7891f4895e003cb85e7651b7d043a963d"
ARTIFACT_ID = "V0_OSAP_GATE3_CLUSTER_B_WP6_PULL_REQUEST_HOSTED_CI_ACCEPTANCE_CORRECTIVE_LAYER"
MANIFEST = "release/v1.4.0/GATE3_CLUSTER_B_WP6_PULL_REQUEST_HOSTED_CI_ACCEPTANCE_CORRECTIVE_LAYER_MANIFEST.json"
LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP6_PULL_REQUEST_HOSTED_CI_ACCEPTANCE_CORRECTIVE_LAYER_SHA256SUMS.txt"
VERIFIER = "release/v1.4.0/tools/verify_wp6_pull_request_hosted_ci_acceptance_corrective_layer.py"
TEST = "tests/test_gate3_cluster_b_wp6_pull_request_hosted_ci_acceptance_corrective_layer.py"
WORKFLOW = ".github/workflows/gate3-cluster-b-wp6-pull-request-hosted-ci-acceptance-corrective-layer.yml"
EXPECTED_MODIFIED = [
    ".github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml",
    ".github/workflows/gate3-cluster-b-wp2.yml",
    ".github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml",
    ".github/workflows/gate3-cluster-b-wp3.yml",
    ".github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml",
    ".github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml",
    ".github/workflows/gate3-cluster-b-wp5.yml",
    ".github/workflows/gate3-cluster-b-wp6-four-root-corrective-layer.yml",
    ".github/workflows/gate3-cluster-b-wp6-hosted-ci-predecessor-blob-fixture-closure.yml",
    ".github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml",
    ".github/workflows/gate3-cluster-b-wp6-successor-attestation-layer.yml",
    ".github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml",
]
EXPECTED_ADDITIVE = [WORKFLOW, MANIFEST, LEDGER, VERIFIER, TEST]
EXPECTED_ROOTS = {
    "ROOT_1": "HISTORICAL_LAYER_HEAD_RESOLUTION_ANCESTRY_SCOPE_DEFECT",
    "ROOT_2": "PULL_REQUEST_MERGE_REF_HEAD_BINDING_DEFECT",
    "ROOT_3": "RUNTIME_DEPENDENCY_OMISSION",
    "ROOT_4": "FROZEN_HISTORICAL_TEST_CURRENT_CHECKOUT_CONTEXT_MISBINDING",
}
EXPECTED_MODIFIED_ROOTS = {
    **{path: ["ROOT_1"] for path in EXPECTED_MODIFIED[:7]},
    EXPECTED_MODIFIED[7]: ["ROOT_3"],
    EXPECTED_MODIFIED[8]: ["ROOT_2"],
    EXPECTED_MODIFIED[9]: ["ROOT_2"],
    EXPECTED_MODIFIED[10]: ["ROOT_4"],
    EXPECTED_MODIFIED[11]: ["ROOT_2"],
}
EXPECTED_CONTEXT_KEYS = {
    "event_number", "event_title", "event_base_ref", "event_base_sha",
    "event_head_ref", "event_head_sha", "synthetic_merge_head", "merge_parents",
    "exact_branch_head", "manifest_historical_anchors", "bounded_ancestry",
    "zero_match", "multi_match",
}
PACKAGE_ARCHIVE_CONTEXT = "PACKAGE_ARCHIVE_CONTEXT"
FULL_REPOSITORY_CONTENT_CONTEXT = "FULL_REPOSITORY_CONTENT_CONTEXT"
REPOSITORY_APPLICATION_SURFACE_CONTEXT = "REPOSITORY_APPLICATION_SURFACE_CONTEXT"


def run(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None,
        text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd or ROOT, env=env, capture_output=True,
                          text=text, check=False)


def require(*args: str, cwd: Path | None = None,
            env: dict[str, str] | None = None,
            text: bool = True) -> subprocess.CompletedProcess:
    completed = run(*args, cwd=cwd, env=env, text=text)
    if completed.returncode:
        stdout = completed.stdout if text else completed.stdout.decode("utf-8", "replace")
        stderr = completed.stderr if text else completed.stderr.decode("utf-8", "replace")
        raise RuntimeError("$ " + " ".join(args) + "\n" + stdout + stderr)
    return completed


def git_text(*args: str, cwd: Path | None = None) -> str:
    return require("git", *args, cwd=cwd).stdout.rstrip("\n")


def git_bytes(*args: str, cwd: Path | None = None) -> bytes:
    return require("git", *args, cwd=cwd, text=False).stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def ensure_runtime_dependencies() -> None:
    missing = []
    for module in ("pytest", "jsonschema", "yaml"):
        if importlib.util.find_spec(module) is None:
            missing.append(module)
    if missing:
        raise RuntimeError("RUNTIME_DEPENDENCY_MISSING:" + ",".join(missing))


def load_manifest(root: Path = ROOT) -> dict[str, Any]:
    raw = (root / MANIFEST).read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise RuntimeError("MANIFEST_JSON_FAILURE") from exc
    if raw != canonical_json(value):
        raise RuntimeError("MANIFEST_CANONICAL_JSON_FAILURE")
    return value


def parse_ledger(data: bytes) -> list[tuple[str, str]]:
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


def apply_transform(transformation: dict[str, Any]) -> bytes:
    source = base64.b64decode(transformation["predecessor_bytes_base64"])
    path = transformation["path"]
    if sha256_bytes(source) != transformation["predecessor_sha256"]:
        raise RuntimeError("PREDECESSOR_SHA256_FAILURE:" + path)
    if git_blob_sha1(source) != transformation["predecessor_blob_sha1"]:
        raise RuntimeError("PREDECESSOR_BLOB_FAILURE:" + path)
    text = source.decode("utf-8")
    replacements = transformation.get("replacements")
    if not isinstance(replacements, list) or len(replacements) != transformation.get("replacement_count"):
        raise RuntimeError("REPLACEMENT_COUNT_FAILURE:" + path)
    for ordinal, replacement in enumerate(replacements, 1):
        if replacement.get("ordinal") != ordinal:
            raise RuntimeError("REPLACEMENT_ORDINAL_FAILURE:" + path)
        old = replacement.get("old")
        new = replacement.get("new")
        if not isinstance(old, str) or not isinstance(new, str):
            raise RuntimeError("REPLACEMENT_TYPE_FAILURE:" + path)
        if text.count(old) != 1 or replacement.get("predecessor_anchor_count") != 1:
            raise RuntimeError(f"REPLACEMENT_ANCHOR_FAILURE:{path}:{ordinal}")
        if sha256_bytes(old.encode()) != replacement.get("old_sha256"):
            raise RuntimeError(f"REPLACEMENT_OLD_DIGEST_FAILURE:{path}:{ordinal}")
        if sha256_bytes(new.encode()) != replacement.get("new_sha256"):
            raise RuntimeError(f"REPLACEMENT_NEW_DIGEST_FAILURE:{path}:{ordinal}")
        text = text.replace(old, new, 1)
    result = text.encode("utf-8")
    if not result.endswith(b"\n") or b"\r" in result:
        raise RuntimeError("RESULT_BYTE_CONTRACT_FAILURE:" + path)
    if sha256_bytes(result) != transformation["resulting_sha256"]:
        raise RuntimeError("RESULT_DIGEST_FAILURE:" + path)
    return result


def visible_package_files(root: Path) -> list[str]:
    files: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if "__pycache__" in rel.parts or ".pytest_cache" in rel.parts or path.suffix == ".pyc":
            continue
        files.append(rel.as_posix())
    return sorted(files)


def validate_manifest_contract(manifest: dict[str, Any]) -> None:
    if manifest.get("artifact_id") != ARTIFACT_ID or manifest.get("version") != "1.2":
        raise RuntimeError("MANIFEST_ARTIFACT_OR_VERSION_FAILURE")
    if manifest.get("repository") != REPOSITORY or manifest.get("branch") != BRANCH:
        raise RuntimeError("MANIFEST_REPOSITORY_BINDING_FAILURE")
    if manifest.get("predecessor") != {
        "commit": PREDECESSOR, "parent": PREDECESSOR_PARENT, "tree": PREDECESSOR_TREE
    }:
        raise RuntimeError("MANIFEST_PREDECESSOR_BINDING_FAILURE")
    if manifest.get("pull_request") != {
        "number": 34, "title": "WP6 successor-attestation layer",
        "base_branch": "main", "base_sha": BASE_SHA,
        "head_branch": BRANCH,
    }:
        raise RuntimeError("MANIFEST_PULL_REQUEST_BINDING_FAILURE")
    if manifest.get("modified_paths") != EXPECTED_MODIFIED or manifest.get("modified_path_count") != 12:
        raise RuntimeError("MANIFEST_MODIFIED_PATH_FAILURE")
    if manifest.get("additive_paths") != EXPECTED_ADDITIVE or manifest.get("additive_path_count") != 5:
        raise RuntimeError("MANIFEST_ADDITIVE_PATH_FAILURE")
    if manifest.get("total_path_count") != 17:
        raise RuntimeError("MANIFEST_TOTAL_PATH_FAILURE")
    if manifest.get("root_causes") != EXPECTED_ROOTS:
        raise RuntimeError("MANIFEST_ROOT_CAUSE_FAILURE")
    if manifest.get("runtime_dependencies") != ["pytest", "jsonschema", "pyyaml"]:
        raise RuntimeError("MANIFEST_RUNTIME_DEPENDENCY_FAILURE")
    if set(manifest.get("pull_request_context_matrix", {})) != EXPECTED_CONTEXT_KEYS:
        raise RuntimeError("MANIFEST_CONTEXT_MATRIX_FAILURE")
    contract = manifest.get("behavioral_contract", {})
    required_true = {
        "additive_predecessor_absence_required", "bounded_ancestry_traversal_required",
        "exact_predecessor_parent_match_required", "missing_historical_anchor_fail_closed",
        "frozen_tests_in_current_descendant_checkout_forbidden",
        "synthetic_merge_head_not_unique_authority",
        "event_pull_request_head_sha_required_when_available",
        "exact_one_parent_layer_commit_required",
        "live_pull_request_context_binding_required",
        "ambiguous_resolution_fail_closed", "repository_immutability_required",
        "unbound_paths_forbidden", "self_excluding_ledger_required",
        "package_archive_exact_inventory_required",
        "full_repository_unrelated_committed_files_allowed",
        "repository_application_exact_status_surface_required",
        "staged_paths_forbidden", "unrelated_changed_or_untracked_paths_forbidden",
    }
    if contract.get("failure_policy") != "FAIL_CLOSED":
        raise RuntimeError("MANIFEST_FAILURE_POLICY_FAILURE")
    if any(contract.get(key) is not True for key in required_true):
        raise RuntimeError("MANIFEST_BEHAVIORAL_CONTRACT_FAILURE")
    policy = manifest.get("historical_artifact_policy", {})
    forbidden = {
        "frozen_artifact_rewrite_authorized", "historical_ledger_expansion_authorized",
        "blanket_allowlist_expansion_authorized", "circular_self_trust_authorized",
    }
    if any(policy.get(key) is not False for key in forbidden):
        raise RuntimeError("MANIFEST_HISTORICAL_POLICY_FAILURE")
    if manifest.get("ledger_path") != LEDGER or manifest.get("ledger_self_excluded") is not True:
        raise RuntimeError("MANIFEST_LEDGER_CONTRACT_FAILURE")
    expected_audit_resolution = {
        "audit_report_version": "1.0",
        "corrected_findings": [
            {
                "defect_id": "PREAPP_DEFECT_1",
                "defect_class": "EXACT_ONE_PARENT_LAYER_COMMIT_ENFORCEMENT_GAP",
                "resolution": "REQUIRE_EXACTLY_ONE_PARENT_EQUAL_TO_EXACT_PREDECESSOR",
                "status": "RESOLVED",
            },
            {
                "defect_id": "PREAPP_DEFECT_2",
                "defect_class": "LIVE_PULL_REQUEST_CONTEXT_BINDING_GAP",
                "resolution": "REQUIRE_EXACT_LIVE_EVENT_BINDING_FOR_NUMBER_TITLE_BASE_REF_BASE_SHA_HEAD_REF_AND_HEAD_SHA",
                "status": "RESOLVED",
            },
        ],
        "predecessor_package_version": "1.0",
        "successor_package_version": "1.1",
        "status": "PASS",
    }
    if manifest.get("pre_application_audit_resolution") != expected_audit_resolution:
        raise RuntimeError("MANIFEST_PRE_APPLICATION_AUDIT_RESOLUTION_FAILURE")
    expected_post_application_resolution = {
        "audit_report_version": "1.1",
        "corrected_findings": [
            {
                "defect_id": "POSTAPP_DEFECT_1",
                "defect_class": "FULL_REPOSITORY_VALIDATE_PACKAGE_INVENTORY_SCOPE_MISBINDING",
                "resolution": "SPLIT_PACKAGE_ARCHIVE_FULL_REPOSITORY_CONTENT_AND_REPOSITORY_APPLICATION_SURFACE_CONTEXTS",
                "status": "RESOLVED",
            }
        ],
        "predecessor_package_version": "1.1",
        "successor_package_version": "1.2",
        "status": "PASS",
    }
    if manifest.get("post_application_audit_resolution") != expected_post_application_resolution:
        raise RuntimeError("MANIFEST_POST_APPLICATION_AUDIT_RESOLUTION_FAILURE")
    expected_validation_contexts = {
        FULL_REPOSITORY_CONTENT_CONTEXT: {
            "authorized_path_content_validation_required": True,
            "exact_authorized_path_count": 17,
            "unrelated_legitimate_committed_files_allowed": True,
            "unrelated_repository_files_treated_as_package_entries": False,
        },
        PACKAGE_ARCHIVE_CONTEXT: {
            "exact_authorized_path_count": 17,
            "exact_root_file_inventory_required": True,
            "unrelated_eighteenth_package_entry_allowed": False,
        },
        REPOSITORY_APPLICATION_SURFACE_CONTEXT: {
            "exact_additive_untracked_path_count": 5,
            "exact_modified_unstaged_path_count": 12,
            "staged_paths_allowed": False,
            "unrelated_changed_or_untracked_paths_allowed": False,
        },
    }
    if manifest.get("validation_contexts") != expected_validation_contexts:
        raise RuntimeError("MANIFEST_VALIDATION_CONTEXT_FAILURE")
    if manifest.get("ledger_entry_count") != 16 or manifest.get("unresolved_dependency_count") != 0:
        raise RuntimeError("MANIFEST_LEDGER_OR_DEPENDENCY_COUNT_FAILURE")
    transformations = manifest.get("transformations")
    if not isinstance(transformations, list) or [row.get("path") for row in transformations] != EXPECTED_MODIFIED:
        raise RuntimeError("MANIFEST_TRANSFORMATION_INVENTORY_FAILURE")
    roles = manifest.get("path_roles")
    if not isinstance(roles, list) or [row.get("path") for row in roles] != EXPECTED_MODIFIED + EXPECTED_ADDITIVE:
        raise RuntimeError("MANIFEST_PATH_ROLE_INVENTORY_FAILURE")
    for row in roles:
        roots = row.get("roots")
        if not roots or any(root not in EXPECTED_ROOTS for root in roots):
            raise RuntimeError("MANIFEST_UNBOUND_PATH_FAILURE:" + str(row.get("path")))
        if row["path"] in EXPECTED_MODIFIED and roots != EXPECTED_MODIFIED_ROOTS[row["path"]]:
            raise RuntimeError("MANIFEST_MODIFIED_ROOT_BINDING_FAILURE:" + row["path"])
        if row["path"] in EXPECTED_ADDITIVE and roots != list(EXPECTED_ROOTS):
            raise RuntimeError("MANIFEST_ADDITIVE_ROOT_BINDING_FAILURE:" + row["path"])
    matrix = manifest.get("replay_matrix", {})
    if set(matrix) != {
        "wp2-post-merge", "wp2", "wp3-post-merge", "wp3", "wp5-post-merge",
        "wp5-sync-helper", "wp5", "wp6-four-root", "wp6-hosted-fixture",
        "wp6-root-d", "wp6-successor-attestation", "wp6-successor-consumer",
    }:
        raise RuntimeError("MANIFEST_REPLAY_MATRIX_FAILURE")
    if matrix["wp5"].get("allowed_jobs") != [
        "baseline", "schemas", "id-audit", "role-coverage", "dependency-dag",
        "python-semantics", "positive-models", "negative-boundary",
        "statement-parity", "ipec-lineage", "deterministic-replay", "gate3-audit-inputs",
    ]:
        raise RuntimeError("MANIFEST_WP5_JOB_MATRIX_FAILURE")


def repository_toplevel(root: Path) -> Path | None:
    completed = run("git", "rev-parse", "--show-toplevel", cwd=root)
    if completed.returncode:
        return None
    try:
        return Path(completed.stdout.strip()).resolve()
    except Exception:
        return None


def validate_authorized_content(root: Path) -> dict[str, Any]:
    ensure_runtime_dependencies()
    manifest = load_manifest(root)
    validate_manifest_contract(manifest)
    expected_files = sorted(EXPECTED_MODIFIED + EXPECTED_ADDITIVE)
    for path in expected_files:
        target = root / path
        if not target.is_file() or target.is_symlink():
            raise RuntimeError("AUTHORIZED_PATH_MISSING_OR_NONREGULAR:" + path)
    for transformation in manifest["transformations"]:
        path = transformation["path"]
        if (root / path).read_bytes() != apply_transform(transformation):
            raise RuntimeError("MODIFIED_BYTES_FAILURE:" + path)
    rows = parse_ledger((root / LEDGER).read_bytes())
    expected_ledger_paths = sorted(path for path in expected_files if path != LEDGER)
    if [path for _, path in rows] != expected_ledger_paths:
        raise RuntimeError("LEDGER_INVENTORY_FAILURE")
    for digest, path in rows:
        if sha256_bytes((root / path).read_bytes()) != digest:
            raise RuntimeError("LEDGER_DIGEST_FAILURE:" + path)
    for path in expected_files:
        data = (root / path).read_bytes()
        if not data.endswith(b"\n") or b"\r" in data:
            raise RuntimeError("TEXT_BYTE_CONTRACT_FAILURE:" + path)
        if (root / path).stat().st_mode & 0o111:
            raise RuntimeError("FILE_MODE_EXECUTABLE_FAILURE:" + path)
    import yaml
    for path in EXPECTED_MODIFIED + [WORKFLOW]:
        if not isinstance(yaml.safe_load((root / path).read_text(encoding="utf-8")), dict):
            raise RuntimeError("YAML_FAILURE:" + path)
    for path in [VERIFIER, TEST]:
        text = (root / path).read_text(encoding="utf-8")
        ast.parse(text, filename=path)
        compile(text, path, "exec")
    for path in EXPECTED_MODIFIED:
        text = (root / path).read_text(encoding="utf-8")
        if VERIFIER not in text or "pytest jsonschema pyyaml" not in text:
            raise RuntimeError("WORKFLOW_SUCCESSOR_ROUTING_FAILURE:" + path)
    dedicated = (root / WORKFLOW).read_text(encoding="utf-8")
    for path in expected_files:
        if dedicated.count("      - '" + path + "'\n") != 2:
            raise RuntimeError("DEDICATED_WORKFLOW_TRIGGER_FAILURE:" + path)
    for marker in [VERIFIER, TEST, "--verify-all-replays", "pytest jsonschema pyyaml"]:
        if marker not in dedicated:
            raise RuntimeError("DEDICATED_WORKFLOW_MARKER_FAILURE:" + marker)
    return {
        "status": "PASS", "path_count": 17, "modified_path_count": 12,
        "additive_path_count": 5, "ledger_entry_count": 16,
        "unresolved_dependency_count": 0,
    }


def validate_package_archive(root: Path = ROOT) -> dict[str, Any]:
    expected_files = sorted(EXPECTED_MODIFIED + EXPECTED_ADDITIVE)
    if visible_package_files(root) != expected_files:
        raise RuntimeError("PACKAGE_EXACT_FILE_INVENTORY_FAILURE")
    result = validate_authorized_content(root)
    result["validation_context"] = PACKAGE_ARCHIVE_CONTEXT
    return result


def validate_full_repository_content(root: Path = ROOT) -> dict[str, Any]:
    if repository_toplevel(root) != root.resolve():
        raise RuntimeError("FULL_REPOSITORY_ROOT_FAILURE")
    result = validate_authorized_content(root)
    result["validation_context"] = FULL_REPOSITORY_CONTENT_CONTEXT
    return result


def porcelain_status_entries(repo: Path) -> dict[str, str]:
    raw = require(
        "git", "status", "--porcelain=v1", "-z", "--untracked-files=all", cwd=repo
    ).stdout
    entries: dict[str, str] = {}
    for record in raw.split("\0"):
        if not record:
            continue
        if len(record) < 4 or record[2] != " ":
            raise RuntimeError("REPOSITORY_STATUS_SERIALIZATION_FAILURE")
        status, path = record[:2], record[3:]
        if status[0] in {"R", "C"}:
            raise RuntimeError("REPOSITORY_RENAME_OR_COPY_FORBIDDEN:" + path)
        if path in entries:
            raise RuntimeError("REPOSITORY_DUPLICATE_STATUS_PATH:" + path)
        entries[path] = status
    return entries


def validate_repository_application_surface(root: Path = ROOT) -> dict[str, Any]:
    before = repository_snapshot(root)
    result = validate_full_repository_content(root)
    entries = porcelain_status_entries(root)
    staged = sorted(path for path, status in entries.items() if status != "??" and status[0] != " ")
    if staged:
        raise RuntimeError("STAGED_PATH_PRESENT:" + json.dumps(staged))
    expected = {path: " M" for path in EXPECTED_MODIFIED}
    expected.update({path: "??" for path in EXPECTED_ADDITIVE})
    if entries != expected:
        extra = sorted(set(entries) - set(expected))
        missing = sorted(set(expected) - set(entries))
        wrong = sorted(path for path in set(entries) & set(expected) if entries[path] != expected[path])
        raise RuntimeError(
            "REPOSITORY_APPLICATION_SURFACE_FAILURE:"
            + json.dumps({"extra": extra, "missing": missing, "wrong_status": wrong}, sort_keys=True)
        )
    after = repository_snapshot(root)
    if before != after:
        raise RuntimeError("REPOSITORY_STATE_MUTATION")
    result["validation_context"] = REPOSITORY_APPLICATION_SURFACE_CONTEXT
    result["unstaged_modified_path_count"] = 12
    result["untracked_additive_path_count"] = 5
    return result


def validate_package(root: Path = ROOT) -> dict[str, Any]:
    # Compatibility dispatch: isolated extraction roots retain exact archive
    # inventory enforcement; exact Git repository roots use content context.
    if repository_toplevel(root) == root.resolve():
        return validate_full_repository_content(root)
    return validate_package_archive(root)


def is_exact_sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value)
    )


def load_event_payload(event_path: str | None) -> dict[str, Any] | None:
    if not event_path:
        return None
    try:
        value = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def event_head(event_path: str | None) -> str:
    value = load_event_payload(event_path)
    if value is None:
        return ""
    pull_request = value.get("pull_request")
    if not isinstance(pull_request, dict):
        return ""
    head = pull_request.get("head")
    if not isinstance(head, dict):
        return ""
    sha = head.get("sha")
    return sha if is_exact_sha(sha) else ""


def validate_live_pull_request_context(
    manifest: dict[str, Any], event_path: str | None
) -> dict[str, Any]:
    value = load_event_payload(event_path)
    if value is None:
        raise RuntimeError("PULL_REQUEST_CONTEXT_MISSING_OR_INVALID")
    pull_request = value.get("pull_request")
    if not isinstance(pull_request, dict):
        raise RuntimeError("PULL_REQUEST_CONTEXT_MISSING_OR_INVALID")
    base = pull_request.get("base")
    head = pull_request.get("head")
    if not isinstance(base, dict) or not isinstance(head, dict):
        raise RuntimeError("PULL_REQUEST_CONTEXT_MISSING_OR_INVALID")
    expected = manifest.get("pull_request")
    if not isinstance(expected, dict):
        raise RuntimeError("PULL_REQUEST_CONTEXT_MISSING_OR_INVALID")
    observed = {
        "number": value.get("number"),
        "title": pull_request.get("title"),
        "base_ref": base.get("ref"),
        "base_sha": base.get("sha"),
        "head_ref": head.get("ref"),
        "head_sha": head.get("sha"),
    }
    expected_values = {
        "number": expected.get("number"),
        "title": expected.get("title"),
        "base_ref": expected.get("base_branch"),
        "base_sha": expected.get("base_sha"),
        "head_ref": expected.get("head_branch"),
    }
    for field, expected_value in expected_values.items():
        if observed[field] != expected_value:
            raise RuntimeError("PULL_REQUEST_CONTEXT_MISMATCH:" + field)
    if not is_exact_sha(observed["head_sha"]):
        raise RuntimeError("PULL_REQUEST_CONTEXT_MISSING_OR_INVALID")
    return observed


def candidate_heads(repo: Path, manifest: dict[str, Any], event_path: str | None = None,
                    max_depth: int = 64) -> list[str]:
    values: list[str] = []
    def add(value: str | None) -> None:
        candidate = (value or "").strip()
        if candidate and candidate not in values:
            values.append(candidate)
    add(event_head(event_path or os.environ.get("GITHUB_EVENT_PATH")))
    add(os.environ.get("V0_OSAP_EXACT_BRANCH_HEAD"))
    add(os.environ.get("GITHUB_SHA"))
    try:
        add(git_text("rev-parse", "HEAD", cwd=repo))
    except Exception:
        pass
    for ref in (
        "refs/heads/" + manifest["branch"],
        "refs/remotes/origin/" + manifest["branch"],
    ):
        completed = run("git", "rev-parse", "--verify", ref, cwd=repo)
        if completed.returncode == 0:
            add(completed.stdout.strip())
    for seed in list(values):
        completed = run("git", "rev-list", f"--max-count={max_depth}", seed, cwd=repo)
        if completed.returncode == 0:
            for commit in completed.stdout.split():
                add(commit)
    return values


def diff_surface(repo: Path, head: str, base: str) -> dict[str, str] | None:
    completed = run("git", "diff", "--name-status", "--no-renames", base, head, "--", cwd=repo)
    if completed.returncode:
        return None
    result: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        if line:
            status, path = line.split("\t", 1)
            result[path] = status
    return result


def resolve_layer_head(repo: Path, manifest: dict[str, Any], event_path: str | None = None,
                       max_depth: int = 64, event_name: str | None = None) -> str:
    name = event_name if event_name is not None else os.environ.get("GITHUB_EVENT_NAME", "")
    supplied_event_path = event_path or os.environ.get("GITHUB_EVENT_PATH")
    pr_head = event_head(supplied_event_path)
    if name.startswith("pull_request"):
        context = validate_live_pull_request_context(manifest, supplied_event_path)
        pr_head = context["head_sha"]
    expected = {path: "M" for path in manifest["modified_paths"]}
    expected.update({path: "A" for path in manifest["additive_paths"]})
    matches: list[str] = []
    predecessor = manifest["predecessor"]["commit"]
    for candidate in candidate_heads(repo, manifest, supplied_event_path, max_depth):
        if run("git", "cat-file", "-e", candidate + "^{commit}", cwd=repo).returncode:
            continue
        fields = git_text("rev-list", "--parents", "-n", "1", candidate, cwd=repo).split()
        if len(fields) != 2 or fields[1] != predecessor:
            continue
        if diff_surface(repo, candidate, predecessor) == expected:
            matches.append(candidate)
    matches = list(dict.fromkeys(matches))
    if len(matches) != 1:
        raise RuntimeError("LAYER_HEAD_RESOLUTION_FAILURE:" + json.dumps(matches))
    if name.startswith("pull_request") and matches[0] != pr_head:
        raise RuntimeError("PULL_REQUEST_HEAD_NOT_EXACT_LAYER:" + matches[0])
    return matches[0]


def validate_predecessor_identity(repo: Path, manifest: dict[str, Any]) -> None:
    predecessor = manifest["predecessor"]
    require("git", "cat-file", "-e", predecessor["commit"] + "^{commit}", cwd=repo)
    if git_text("rev-parse", predecessor["commit"] + "^", cwd=repo) != predecessor["parent"]:
        raise RuntimeError("PREDECESSOR_PARENT_FAILURE")
    if git_text("show", "-s", "--format=%T", predecessor["commit"], cwd=repo) != predecessor["tree"]:
        raise RuntimeError("PREDECESSOR_TREE_FAILURE")


def validate_historical_anchors(repo: Path, manifest: dict[str, Any]) -> None:
    for name, spec in manifest["replay_matrix"].items():
        anchor = spec["anchor"]
        if run("git", "cat-file", "-e", anchor + "^{commit}", cwd=repo).returncode:
            raise RuntimeError("MISSING_HISTORICAL_ANCHOR:" + name + ":" + anchor)
        commands = spec.get("commands") or spec.get("commands_template")
        for command in commands:
            if len(command) > 1 and command[0] == "python" and not command[1].startswith("-"):
                if run("git", "cat-file", "-e", anchor + ":" + command[1], cwd=repo).returncode:
                    raise RuntimeError("MISSING_HISTORICAL_COMMAND_PATH:" + name + ":" + command[1])


def validate_additive_absence(repo: Path, predecessor: str,
                              additive_paths: list[str]) -> None:
    for path in additive_paths:
        if run("git", "cat-file", "-e", predecessor + ":" + path, cwd=repo).returncode == 0:
            raise RuntimeError("ADDITIVE_PREDECESSOR_PRESENCE:" + path)


def validate_committed_surface(repo: Path, layer_head: str,
                               manifest: dict[str, Any]) -> None:
    expected = {path: "M" for path in EXPECTED_MODIFIED}
    expected.update({path: "A" for path in EXPECTED_ADDITIVE})
    if diff_surface(repo, layer_head, PREDECESSOR) != expected:
        raise RuntimeError("COMMITTED_EXACT_SURFACE_FAILURE")
    validate_additive_absence(repo, PREDECESSOR, EXPECTED_ADDITIVE)
    by_path = {row["path"]: row for row in manifest["transformations"]}
    for path in EXPECTED_MODIFIED:
        predecessor_bytes = git_bytes("show", PREDECESSOR + ":" + path, cwd=repo)
        if predecessor_bytes != base64.b64decode(by_path[path]["predecessor_bytes_base64"]):
            raise RuntimeError("LIVE_PREDECESSOR_BYTES_FAILURE:" + path)
        layer_bytes = git_bytes("show", layer_head + ":" + path, cwd=repo)
        if layer_bytes != apply_transform(by_path[path]):
            raise RuntimeError("COMMITTED_MODIFIED_BYTES_FAILURE:" + path)
        if (repo / path).read_bytes() != layer_bytes:
            raise RuntimeError("CURRENT_CHECKOUT_MODIFIED_BYTES_FAILURE:" + path)
    for path in EXPECTED_ADDITIVE:
        layer_bytes = git_bytes("show", layer_head + ":" + path, cwd=repo)
        if (repo / path).read_bytes() != layer_bytes:
            raise RuntimeError("CURRENT_CHECKOUT_ADDITIVE_BYTES_FAILURE:" + path)
    for path in EXPECTED_MODIFIED + EXPECTED_ADDITIVE:
        fields = git_text("ls-tree", layer_head, "--", path, cwd=repo).split()
        if not fields or fields[0] != "100644":
            raise RuntimeError("COMMITTED_FILE_MODE_FAILURE:" + path)
    ledger_bytes = git_bytes("show", layer_head + ":" + LEDGER, cwd=repo)
    if ledger_bytes != (repo / LEDGER).read_bytes():
        raise RuntimeError("COMMITTED_LEDGER_BYTES_FAILURE")
    for digest, path in parse_ledger(ledger_bytes):
        if sha256_bytes(git_bytes("show", layer_head + ":" + path, cwd=repo)) != digest:
            raise RuntimeError("COMMITTED_LEDGER_DIGEST_FAILURE:" + path)


def index_sha256(repo: Path) -> str:
    path = Path(git_text("rev-parse", "--git-path", "index", cwd=repo))
    if not path.is_absolute():
        path = repo / path
    return sha256_bytes(path.read_bytes()) if path.is_file() else "ABSENT"


def repository_snapshot(repo: Path) -> dict[str, str]:
    return {
        "head": git_text("rev-parse", "HEAD", cwd=repo),
        "index_sha256": index_sha256(repo),
        "status": git_text("status", "--porcelain=v1", "--untracked-files=all", cwd=repo),
        "refs_sha256": sha256_bytes(require("git", "show-ref", "--head", cwd=repo).stdout.encode()),
        "worktrees_sha256": sha256_bytes(require("git", "worktree", "list", "--porcelain", cwd=repo).stdout.encode()),
    }


def verify_committed(repo: Path = ROOT, event_path: str | None = None,
                     event_name: str | None = None) -> dict[str, Any]:
    before = repository_snapshot(repo)
    manifest = load_manifest(repo)
    validate_manifest_contract(manifest)
    ensure_runtime_dependencies()
    validate_predecessor_identity(repo, manifest)
    validate_historical_anchors(repo, manifest)
    layer_head = resolve_layer_head(repo, manifest, event_path, event_name=event_name)
    validate_full_repository_content(repo)
    validate_committed_surface(repo, layer_head, manifest)
    after = repository_snapshot(repo)
    if before != after:
        raise RuntimeError("REPOSITORY_STATE_MUTATION")
    return {"status": "PASS", "layer_head": layer_head, "path_count": 17}


@contextlib.contextmanager
def detached_worktree(repo: Path, anchor: str) -> Iterator[Path]:
    temporary = Path(tempfile.mkdtemp(prefix="v0-osap-pr-ci-replay-"))
    worktree = temporary / "repository"
    added = False
    try:
        require("git", "worktree", "add", "--detach", str(worktree), anchor, cwd=repo)
        added = True
        yield worktree
    finally:
        if added:
            completed = run("git", "worktree", "remove", "--force", str(worktree), cwd=repo)
            if completed.returncode:
                shutil.rmtree(worktree, ignore_errors=True)
                run("git", "worktree", "remove", "--force", str(worktree), cwd=repo)
        shutil.rmtree(temporary, ignore_errors=True)


def validate_exact_historical_context(worktree: Path, anchor: str) -> None:
    if git_text("rev-parse", "HEAD", cwd=worktree) != anchor:
        raise RuntimeError("FROZEN_EXECUTION_CONTEXT_FAILURE:" + anchor)
    if git_text("status", "--porcelain=v1", "--untracked-files=all", cwd=worktree):
        raise RuntimeError("FROZEN_EXECUTION_DIRTY_BEFORE_REPLAY:" + anchor)


def resolved_commands(spec: dict[str, Any], job: str | None) -> list[list[str]]:
    if "allowed_jobs" in spec:
        if not job or job not in spec["allowed_jobs"]:
            raise RuntimeError("INVALID_OR_MISSING_REPLAY_JOB")
        return [[str(part).replace("{job}", job) for part in command]
                for command in spec["commands_template"]]
    if job is not None:
        raise RuntimeError("UNEXPECTED_REPLAY_JOB")
    return spec["commands"]


def replay(workflow: str, job: str | None = None, repo: Path = ROOT,
           verify_current: bool = True) -> dict[str, Any]:
    if verify_current:
        verify_committed(repo)
    manifest = load_manifest(repo)
    if workflow not in manifest["replay_matrix"]:
        raise RuntimeError("UNKNOWN_REPLAY_WORKFLOW:" + workflow)
    spec = manifest["replay_matrix"][workflow]
    commands = resolved_commands(spec, job)
    before = repository_snapshot(repo)
    with detached_worktree(repo, spec["anchor"]) as worktree:
        validate_exact_historical_context(worktree, spec["anchor"])
        environment = os.environ.copy()
        environment.update({
            "CI": "true", "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "push", "GITHUB_REF": "refs/heads/" + BRANCH,
            "GITHUB_REF_NAME": BRANCH, "GIT_OPTIONAL_LOCKS": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        for command in commands:
            resolved = list(command)
            if resolved and resolved[0] == "python":
                resolved[0] = sys.executable
            require(*resolved, cwd=worktree, env=environment)
        if git_text("status", "--porcelain=v1", "--untracked-files=all", cwd=worktree):
            raise RuntimeError("FROZEN_EXECUTION_DIRTY_AFTER_REPLAY:" + spec["anchor"])
    if repository_snapshot(repo) != before:
        raise RuntimeError("REPOSITORY_STATE_MUTATION")
    return {"status": "PASS", "workflow": workflow, "job": job, "anchor": spec["anchor"]}


def verify_all_replays(repo: Path = ROOT) -> dict[str, Any]:
    current = verify_committed(repo)
    manifest = load_manifest(repo)
    results = []
    for workflow in sorted(manifest["replay_matrix"]):
        spec = manifest["replay_matrix"][workflow]
        jobs = spec.get("allowed_jobs", [None])
        for job in jobs:
            results.append(replay(workflow, job, repo, verify_current=False))
    return {
        "status": "PASS", "layer_head": current["layer_head"],
        "replay_count": len(results), "root_coverage": "COMPLETE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("package-only", "full-repository-content", "repository-application", "committed"),
        required=True,
    )
    parser.add_argument("--root")
    parser.add_argument("--replay-workflow")
    parser.add_argument("--job")
    parser.add_argument("--verify-all-replays", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else ROOT
    try:
        if args.mode in {"package-only", "full-repository-content", "repository-application"}:
            if args.replay_workflow or args.job or args.verify_all_replays:
                raise RuntimeError("CONTENT_CONTEXT_REPLAY_FORBIDDEN")
            if args.mode == "package-only":
                result = validate_package(root)
            elif args.mode == "full-repository-content":
                result = validate_full_repository_content(root)
            else:
                result = validate_repository_application_surface(root)
        elif args.verify_all_replays:
            if args.replay_workflow or args.job:
                raise RuntimeError("AMBIGUOUS_OPERATION")
            result = verify_all_replays(root)
        elif args.replay_workflow:
            result = replay(args.replay_workflow, args.job, root)
        elif args.job:
            raise RuntimeError("JOB_WITHOUT_REPLAY_WORKFLOW")
        else:
            result = verify_committed(root)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
