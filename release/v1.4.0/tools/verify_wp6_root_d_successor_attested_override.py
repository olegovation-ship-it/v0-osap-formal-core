#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[3]
BRANCH = "v1.4.0-development"
PREDECESSOR = "7aac3b8a992253666209cb9a2371eb00c0d749cd"
PREDECESSOR_PARENT = "96a6164fd4fe6b8a85992df746672e4261fed8d3"
PREDECESSOR_TITLE = "repair(wp6): integrate four-root replay-harness corrective layer"
HISTORICAL_LAYER_HEAD = "96a6164fd4fe6b8a85992df746672e4261fed8d3"
HISTORICAL_LAYER_PREDECESSOR = "e1b3928c0759e2ed61624dabf4cbc505982c379f"

SC_WORKFLOW = '.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml'
ROOT_D_WORKFLOW = '.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml'
ROOT_D_MANIFEST = 'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_MANIFEST.json'
ROOT_D_LEDGER = 'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_SHA256SUMS.txt'
ROOT_D_VERIFIER = 'release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py'
ROOT_D_TEST = 'tests/test_gate3_cluster_b_wp6_root_d_successor_attested_override.py'

HISTORICAL_MANIFEST = 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_MANIFEST.json'
HISTORICAL_LEDGER = 'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_SHA256SUMS.txt'
HISTORICAL_VERIFIER = 'release/v1.4.0/tools/verify_wp6_successor_consumer_integration_corrective_layer.py'
HISTORICAL_TEST = 'tests/test_gate3_cluster_b_wp6_successor_consumer_integration_corrective_layer.py'
FOUR_ROOT_MANIFEST = 'release/v1.4.0/GATE3_CLUSTER_B_WP6_FOUR_ROOT_CORRECTIVE_LAYER_MANIFEST.json'
FOUR_ROOT_LEDGER = 'release/v1.4.0/GATE3_CLUSTER_B_WP6_FOUR_ROOT_CORRECTIVE_LAYER_SHA256SUMS.txt'
FOUR_ROOT_VERIFIER = 'release/v1.4.0/tools/verify_wp6_four_root_corrective_layer.py'
FOUR_ROOT_TEST = 'tests/test_gate3_cluster_b_wp6_four_root_corrective_layer.py'
EXACT_OVERRIDE_PATH = '.github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml'

MODIFIED_PATHS = [SC_WORKFLOW]
ADDITIVE_PATHS = sorted([
    ROOT_D_WORKFLOW,
    ROOT_D_MANIFEST,
    ROOT_D_LEDGER,
    ROOT_D_VERIFIER,
    ROOT_D_TEST,
])
ATTESTED_PATHS = sorted([
    SC_WORKFLOW,
    ROOT_D_WORKFLOW,
    ROOT_D_MANIFEST,
    ROOT_D_VERIFIER,
    ROOT_D_TEST,
])
SURFACE_PATHS = sorted(MODIFIED_PATHS + ADDITIVE_PATHS)
EXPECTED_PREDECESSOR_WORKFLOW = 'name: V0 OSAP Gate 3 Cluster B WP6 Successor-Consumer Integration Corrective Layer\n\non:\n  pull_request:\n    branches: [main]\n    paths:\n      - \'.github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp2.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp3.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_MANIFEST.json\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_SHA256SUMS.txt\'\n      - \'release/v1.4.0/tools/verify_wp6_successor_consumer_integration_corrective_layer.py\'\n      - \'tests/test_gate3_cluster_b_wp6_successor_consumer_integration_corrective_layer.py\'\n  push:\n    branches: [v1.4.0-development, main]\n    paths:\n      - \'.github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp2.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp3.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_MANIFEST.json\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_SHA256SUMS.txt\'\n      - \'release/v1.4.0/tools/verify_wp6_successor_consumer_integration_corrective_layer.py\'\n      - \'tests/test_gate3_cluster_b_wp6_successor_consumer_integration_corrective_layer.py\'\n  workflow_dispatch:\n\npermissions:\n  contents: read\n\njobs:\n  successor-consumer-integration-corrective-layer:\n    runs-on: ubuntu-latest\n    env:\n      GIT_OPTIONAL_LOCKS: "0"\n      PYTHONDONTWRITEBYTECODE: "1"\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          fetch-depth: 0\n      - uses: actions/setup-python@v5\n        with:\n          python-version: "3.12"\n      - name: Install exact Python validation dependencies\n        run: python -m pip install --disable-pip-version-check pytest jsonschema\n      - name: Verify exact surface, predecessor v0.2, and eight-workflow replay matrix\n        run: >-\n          python release/v1.4.0/tools/verify_wp6_successor_consumer_integration_corrective_layer.py\n          --mode committed\n          --verify-eight-workflow-matrix\n      - name: Dedicated corrective-layer regression\n        run: >-\n          python -m pytest -q -p no:cacheprovider\n          tests/test_gate3_cluster_b_wp6_successor_consumer_integration_corrective_layer.py\n      - name: Whitespace and bounded corrective-surface integrity\n        run: git diff --check e1b3928c0759e2ed61624dabf4cbc505982c379f...HEAD\n'
EXPECTED_PREDECESSOR_WORKFLOW_SHA256 = "1aabe0b3d5bf4cb3e439c382b2394c8424b04ecca1f75f92dfd8bfcdc55bb8ce"
EXPECTED_PREDECESSOR_WORKFLOW_BLOB_SHA1 = "786d077571800232181aaf732f60ba9ff695560f"

EXPECTED_TOP_LEVEL_FIELDS = sorted([
    "additive_path_count",
    "additive_paths",
    "artifact_id",
    "branch",
    "byte_contract",
    "historical_artifact_policy",
    "historical_successor_consumer_layer",
    "ledger_attested_path_count",
    "ledger_attested_paths",
    "ledger_path",
    "ledger_self_excluded",
    "modified_path_count",
    "modified_paths",
    "override_contract",
    "path_roles",
    "predecessor",
    "replay_contract",
    "root_d",
    "successor_four_root_layer",
    "total_path_count",
    "transformations",
    "version",
])

EXPECTED_OVERRIDE_CLAUSES = {
    "authorized_override_set_is_exact_intersection": True,
    "chain_contiguity_required": True,
    "circular_self_trust_forbidden": True,
    "current_descendant_equals_historical_bytes_required": False,
    "current_difference_requires_successor_attestation": True,
    "detached_historical_test_replay_required": True,
    "detached_historical_verifier_replay_required": True,
    "historical_artifact_rewrite_forbidden": True,
    "historical_identity_verified_at_exact_layer_head": True,
    "successor_exact_transform_derivation_required": True,
    "successor_self_excluding_ledger_required": True,
    "unattested_override_is_failure": True,
}

ENV = os.environ.copy()
ENV.update({
    "GIT_OPTIONAL_LOCKS": "0",
    "PYTHONDONTWRITEBYTECODE": "1",
    "GIT_LFS_SKIP_SMUDGE": "1",
})


def run(
    *args: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    text: bool = True,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=cwd or ROOT,
        env=env or ENV,
        capture_output=True,
        text=text,
        check=False,
    )


def require(
    *args: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    text: bool = True,
) -> subprocess.CompletedProcess:
    cp = run(*args, cwd=cwd, env=env, text=text)
    if cp.returncode:
        stdout = cp.stdout if text else cp.stdout.decode("utf-8", "replace")
        stderr = cp.stderr if text else cp.stderr.decode("utf-8", "replace")
        raise RuntimeError("$ " + " ".join(args) + "\n" + stdout + stderr)
    return cp


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def load_manifest(root: Path = ROOT) -> dict[str, Any]:
    raw = (root / ROOT_D_MANIFEST).read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if raw != canonical_json(value):
        raise RuntimeError("ROOT_D_MANIFEST_CANONICAL_JSON_FAILURE")
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
        if len(digest) != 64 or any(
            ch not in "0123456789abcdef" for ch in digest
        ):
            raise RuntimeError(f"LEDGER_DIGEST_FAILURE:{ordinal}")
        if not path or path in seen:
            raise RuntimeError(f"LEDGER_PATH_FAILURE:{ordinal}")
        seen.add(path)
        rows.append((digest, path))
    return rows


def apply_transformations(source: bytes, transformation: dict[str, Any]) -> bytes:
    text = source.decode("utf-8")
    replacements = transformation.get("replacements")
    if not isinstance(replacements, list) or not replacements:
        raise RuntimeError("TRANSFORMATION_REPLACEMENT_LIST_FAILURE")
    if transformation.get("replacement_count") != len(replacements):
        raise RuntimeError("TRANSFORMATION_REPLACEMENT_COUNT_FAILURE")
    for ordinal, replacement in enumerate(replacements, 1):
        old = replacement.get("old")
        new = replacement.get("new")
        if not isinstance(old, str) or not isinstance(new, str):
            raise RuntimeError(f"TRANSFORMATION_REPLACEMENT_TYPE_FAILURE:{ordinal}")
        if replacement.get("old_sha256") != sha256_bytes(old.encode("utf-8")):
            raise RuntimeError(f"TRANSFORMATION_OLD_DIGEST_FAILURE:{ordinal}")
        if replacement.get("new_sha256") != sha256_bytes(new.encode("utf-8")):
            raise RuntimeError(f"TRANSFORMATION_NEW_DIGEST_FAILURE:{ordinal}")
        if text.count(old) != 1:
            raise RuntimeError(
                f"TRANSFORMATION_ANCHOR_COUNT_FAILURE:{ordinal}:"
                f"{text.count(old)}"
            )
        text = text.replace(old, new, 1)
    result = text.encode("utf-8")
    if not result.endswith(b"\n") or b"\r" in result:
        raise RuntimeError("TRANSFORMATION_BYTE_CONTRACT_FAILURE")
    return result


def transformation_record(manifest: dict[str, Any]) -> dict[str, Any]:
    transformations = manifest.get("transformations")
    if not isinstance(transformations, list) or len(transformations) != 1:
        raise RuntimeError("TRANSFORMATION_SURFACE_COUNT_FAILURE")
    item = transformations[0]
    if item.get("path") != SC_WORKFLOW:
        raise RuntimeError("TRANSFORMATION_PATH_FAILURE")
    return item


def expected_modified_workflow(manifest: dict[str, Any]) -> bytes:
    source = EXPECTED_PREDECESSOR_WORKFLOW.encode("utf-8")
    if sha256_bytes(source) != EXPECTED_PREDECESSOR_WORKFLOW_SHA256:
        raise RuntimeError("EMBEDDED_PREDECESSOR_WORKFLOW_SHA256_FAILURE")
    if git_blob_sha1(source) != EXPECTED_PREDECESSOR_WORKFLOW_BLOB_SHA1:
        raise RuntimeError("EMBEDDED_PREDECESSOR_WORKFLOW_BLOB_FAILURE")
    item = transformation_record(manifest)
    if item.get("predecessor_blob_sha1") != EXPECTED_PREDECESSOR_WORKFLOW_BLOB_SHA1:
        raise RuntimeError("MANIFEST_PREDECESSOR_BLOB_FAILURE")
    if item.get("predecessor_sha256") != EXPECTED_PREDECESSOR_WORKFLOW_SHA256:
        raise RuntimeError("MANIFEST_PREDECESSOR_SHA256_FAILURE")
    return apply_transformations(source, item)


def validate_manifest(manifest: dict[str, Any]) -> None:
    if sorted(manifest) != EXPECTED_TOP_LEVEL_FIELDS:
        raise RuntimeError("MANIFEST_TOP_LEVEL_FIELDS_FAILURE")
    expected_scalars = {
        "artifact_id":
            "V0_OSAP_GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE",
        "version": "1.0",
        "branch": BRANCH,
        "modified_path_count": 1,
        "additive_path_count": 5,
        "total_path_count": 6,
        "ledger_attested_path_count": 5,
        "ledger_path": ROOT_D_LEDGER,
        "ledger_self_excluded": True,
    }
    for key, expected in expected_scalars.items():
        if manifest.get(key) != expected:
            raise RuntimeError(f"MANIFEST_SCALAR_FAILURE:{key}")
    if manifest.get("modified_paths") != MODIFIED_PATHS:
        raise RuntimeError("MANIFEST_MODIFIED_PATHS_FAILURE")
    if manifest.get("additive_paths") != ADDITIVE_PATHS:
        raise RuntimeError("MANIFEST_ADDITIVE_PATHS_FAILURE")
    if manifest.get("ledger_attested_paths") != ATTESTED_PATHS:
        raise RuntimeError("MANIFEST_ATTESTED_PATHS_FAILURE")
    predecessor = manifest.get("predecessor") or {}
    if predecessor != {
        "commit": PREDECESSOR,
        "parent": PREDECESSOR_PARENT,
        "title": PREDECESSOR_TITLE,
    }:
        raise RuntimeError("MANIFEST_PREDECESSOR_FAILURE")
    root_d = manifest.get("root_d") or {}
    if root_d.get("code") != (
        "SUCCESSOR_CONSUMER_CURRENT_HEAD_EXACT_LAYER_BYTE_IDENTITY_ASSUMPTION"
    ):
        raise RuntimeError("MANIFEST_ROOT_D_CODE_FAILURE")
    if root_d.get("diagnostic_root_path") != HISTORICAL_VERIFIER:
        raise RuntimeError("MANIFEST_DIAGNOSTIC_ROOT_FAILURE")
    override = manifest.get("override_contract") or {}
    if override.get("clauses") != EXPECTED_OVERRIDE_CLAUSES:
        raise RuntimeError("MANIFEST_OVERRIDE_CLAUSES_FAILURE")
    if override.get("exact_authorized_override_set") != [EXACT_OVERRIDE_PATH]:
        raise RuntimeError("MANIFEST_OVERRIDE_SET_FAILURE")
    historical = manifest.get("historical_successor_consumer_layer") or {}
    if historical.get("exact_head") != HISTORICAL_LAYER_HEAD:
        raise RuntimeError("MANIFEST_HISTORICAL_HEAD_FAILURE")
    if historical.get("predecessor") != HISTORICAL_LAYER_PREDECESSOR:
        raise RuntimeError("MANIFEST_HISTORICAL_PREDECESSOR_FAILURE")
    if historical.get("rewrite_authorized") is not False:
        raise RuntimeError("MANIFEST_HISTORICAL_REWRITE_POLICY_FAILURE")
    successor = manifest.get("successor_four_root_layer") or {}
    if successor.get("exact_head") != PREDECESSOR:
        raise RuntimeError("MANIFEST_SUCCESSOR_HEAD_FAILURE")
    if successor.get("predecessor") != HISTORICAL_LAYER_HEAD:
        raise RuntimeError("MANIFEST_SUCCESSOR_PREDECESSOR_FAILURE")
    transformation_record(manifest)


def validate_text_file(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("PACKAGE_MEMBER_REGULAR_FILE_FAILURE:" + str(path))
    data = path.read_bytes()
    if not data.endswith(b"\n") or b"\r" in data:
        raise RuntimeError("PACKAGE_MEMBER_BYTE_CONTRACT_FAILURE:" + str(path))
    data.decode("utf-8")


def validate_workflow_semantics(root: Path = ROOT) -> None:
    sc = (root / SC_WORKFLOW).read_text(encoding="utf-8")
    root_d = (root / ROOT_D_WORKFLOW).read_text(encoding="utf-8")
    required_sc = [
        ROOT_D_WORKFLOW,
        ROOT_D_MANIFEST,
        ROOT_D_LEDGER,
        ROOT_D_VERIFIER,
        ROOT_D_TEST,
        "--verify-root-d-contract",
        "pytest jsonschema pyyaml",
        f"git diff --check {PREDECESSOR}...HEAD",
    ]
    for marker in required_sc:
        if marker not in sc:
            raise RuntimeError("MODIFIED_WORKFLOW_MARKER_MISSING:" + marker)
    forbidden_sc = [
        "verify_wp6_successor_consumer_integration_corrective_layer.py\n"
        "          --mode committed",
        "tests/test_gate3_cluster_b_wp6_successor_consumer_integration_corrective_layer.py\n"
        "      - name: Whitespace",
    ]
    for marker in forbidden_sc:
        if marker in sc:
            raise RuntimeError("MODIFIED_WORKFLOW_DIRECT_FROZEN_EXECUTION:" + marker)
    for path in SURFACE_PATHS:
        if path not in root_d:
            raise RuntimeError("ROOT_D_WORKFLOW_PATH_TRIGGER_MISSING:" + path)
    for marker in [
        ROOT_D_VERIFIER,
        ROOT_D_TEST,
        "--verify-root-d-contract",
        "pytest jsonschema pyyaml",
        f"git diff --check {PREDECESSOR}...HEAD",
    ]:
        if marker not in root_d:
            raise RuntimeError("ROOT_D_WORKFLOW_MARKER_MISSING:" + marker)
    if yaml is None:
        raise RuntimeError("PYYAML_UNAVAILABLE")
    for relative in [SC_WORKFLOW, ROOT_D_WORKFLOW]:
        parsed = yaml.safe_load((root / relative).read_text(encoding="utf-8"))
        if not isinstance(parsed, dict) or "jobs" not in parsed:
            raise RuntimeError("WORKFLOW_YAML_STRUCTURE_FAILURE:" + relative)


def validate_ledger(root: Path = ROOT) -> None:
    rows = parse_ledger((root / ROOT_D_LEDGER).read_bytes())
    if [path for _, path in rows] != ATTESTED_PATHS:
        raise RuntimeError("LEDGER_ATTESTED_PATH_SET_FAILURE")
    if ROOT_D_LEDGER in [path for _, path in rows]:
        raise RuntimeError("LEDGER_SELF_EXCLUSION_FAILURE")
    for digest, path in rows:
        actual = sha256_bytes((root / path).read_bytes())
        if actual != digest:
            raise RuntimeError("LEDGER_IDENTITY_FAILURE:" + path)


def verify_package(root: Path = ROOT) -> dict[str, Any]:
    for relative in SURFACE_PATHS:
        validate_text_file(root / relative)
    manifest = load_manifest(root)
    validate_manifest(manifest)
    expected_workflow = expected_modified_workflow(manifest)
    actual_workflow = (root / SC_WORKFLOW).read_bytes()
    if actual_workflow != expected_workflow:
        raise RuntimeError("MODIFIED_WORKFLOW_DERIVATION_FAILURE")
    validate_ledger(root)
    validate_workflow_semantics(root)
    for relative in [ROOT_D_VERIFIER, ROOT_D_TEST]:
        ast.parse((root / relative).read_text(encoding="utf-8"), filename=relative)
    return {
        "status": "PASS",
        "mode": "PACKAGE_ONLY",
        "modified_path_count": 1,
        "additive_path_count": 5,
        "total_path_count": 6,
        "ledger_attested_path_count": 5,
        "root_d": (
            "SUCCESSOR_CONSUMER_CURRENT_HEAD_"
            "EXACT_LAYER_BYTE_IDENTITY_ASSUMPTION"
        ),
    }


def git_text(*args: str, cwd: Path = ROOT) -> str:
    return require("git", *args, cwd=cwd).stdout.rstrip("\n")


def git_bytes(*args: str, cwd: Path = ROOT) -> bytes:
    return require("git", *args, cwd=cwd, text=False).stdout


def commit_exists(commit: str) -> bool:
    return run("git", "cat-file", "-e", commit + "^{commit}").returncode == 0


def commit_parent(commit: str) -> str:
    return git_text("rev-parse", commit + "^")


def diff_entries(base: str, head: str) -> dict[str, str]:
    output = git_text("diff", "--name-status", "--no-renames", base, head, "--")
    rows: dict[str, str] = {}
    for line in output.splitlines():
        if not line:
            continue
        code, path = line.split("\t", 1)
        rows[path] = code
    return rows


def candidate_layer_heads() -> list[str]:
    candidates: list[str] = []
    head = git_text("rev-parse", "HEAD")
    candidates.append(head)
    env_head = os.environ.get("GITHUB_HEAD_SHA", "").strip()
    if env_head:
        candidates.append(env_head)
    parents = git_text("rev-list", "--parents", "-n", "1", head).split()[1:]
    candidates.extend(parents)
    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def resolve_layer_head() -> str:
    expected = {SC_WORKFLOW: "M"}
    expected.update({path: "A" for path in ADDITIVE_PATHS})
    matches: list[str] = []
    for candidate in candidate_layer_heads():
        if not commit_exists(candidate):
            continue
        if commit_parent(candidate) != PREDECESSOR:
            continue
        if diff_entries(PREDECESSOR, candidate) == expected:
            matches.append(candidate)
    if len(matches) != 1:
        raise RuntimeError("ROOT_D_LAYER_HEAD_RESOLUTION_FAILURE:" + repr(matches))
    return matches[0]


def read_json_at(commit: str, path: str) -> dict[str, Any]:
    raw = git_bytes("show", f"{commit}:{path}")
    value = json.loads(raw.decode("utf-8"))
    if raw != canonical_json(value):
        raise RuntimeError("HISTORICAL_MANIFEST_CANONICAL_FAILURE:" + path)
    return value


def ledger_identity_at(commit: str, ledger_path: str) -> dict[str, str]:
    rows = parse_ledger(git_bytes("show", f"{commit}:{ledger_path}"))
    result: dict[str, str] = {}
    for digest, path in rows:
        actual = sha256_bytes(git_bytes("show", f"{commit}:{path}"))
        if actual != digest:
            raise RuntimeError(
                f"HISTORICAL_LEDGER_IDENTITY_FAILURE:{commit}:{path}"
            )
        result[path] = digest
    if ledger_path in result:
        raise RuntimeError("HISTORICAL_LEDGER_SELF_EXCLUSION_FAILURE:" + ledger_path)
    return result


def validate_chain_and_override() -> dict[str, Any]:
    if commit_parent(PREDECESSOR) != HISTORICAL_LAYER_HEAD:
        raise RuntimeError("SUCCESSOR_CHAIN_CONTIGUITY_FAILURE")
    if commit_parent(HISTORICAL_LAYER_HEAD) != HISTORICAL_LAYER_PREDECESSOR:
        raise RuntimeError("HISTORICAL_CHAIN_CONTIGUITY_FAILURE")

    historical = read_json_at(HISTORICAL_LAYER_HEAD, HISTORICAL_MANIFEST)
    successor = read_json_at(PREDECESSOR, FOUR_ROOT_MANIFEST)

    if (historical.get("predecessor") or {}).get("commit") != (
        HISTORICAL_LAYER_PREDECESSOR
    ):
        raise RuntimeError("HISTORICAL_MANIFEST_PREDECESSOR_FAILURE")
    if (successor.get("predecessor") or {}).get("commit") != (
        HISTORICAL_LAYER_HEAD
    ):
        raise RuntimeError("SUCCESSOR_MANIFEST_PREDECESSOR_FAILURE")

    historical_surface = sorted(
        list(historical.get("modified_paths") or [])
        + list(historical.get("additive_paths") or [])
    )
    changed = sorted(diff_entries(HISTORICAL_LAYER_HEAD, PREDECESSOR))
    override_set = sorted(set(historical_surface) & set(changed))
    if override_set != [EXACT_OVERRIDE_PATH]:
        raise RuntimeError("EXACT_OVERRIDE_SET_FAILURE:" + repr(override_set))

    successor_modified = list(successor.get("modified_paths") or [])
    if EXACT_OVERRIDE_PATH not in successor_modified:
        raise RuntimeError("SUCCESSOR_OVERRIDE_DECLARATION_FAILURE")

    transformations = {
        item.get("path"): item
        for item in (successor.get("transformations") or [])
    }
    item = transformations.get(EXACT_OVERRIDE_PATH)
    if not isinstance(item, dict):
        raise RuntimeError("SUCCESSOR_OVERRIDE_TRANSFORMATION_ABSENT")
    source = git_bytes("show", f"{HISTORICAL_LAYER_HEAD}:{EXACT_OVERRIDE_PATH}")
    if item.get("predecessor_blob_sha1") != git_blob_sha1(source):
        raise RuntimeError("SUCCESSOR_OVERRIDE_PREDECESSOR_BLOB_FAILURE")
    derived = apply_transformations(source, item)
    actual = git_bytes("show", f"{PREDECESSOR}:{EXACT_OVERRIDE_PATH}")
    if derived != actual:
        raise RuntimeError("SUCCESSOR_OVERRIDE_DERIVATION_FAILURE")

    historical_rewrite_paths = [
        HISTORICAL_MANIFEST,
        HISTORICAL_LEDGER,
        HISTORICAL_VERIFIER,
        HISTORICAL_TEST,
    ]
    changed_set = set(changed)
    rewritten = sorted(changed_set & set(historical_rewrite_paths))
    if rewritten:
        raise RuntimeError("HISTORICAL_ARTIFACT_REWRITE_FAILURE:" + repr(rewritten))

    historical_ledger = ledger_identity_at(
        HISTORICAL_LAYER_HEAD, HISTORICAL_LEDGER
    )
    successor_ledger = ledger_identity_at(PREDECESSOR, FOUR_ROOT_LEDGER)

    policy = successor.get("historical_artifact_policy") or {}
    required_policy = {
        "canonical_ledgers_rewritten": False,
        "frozen_builders_rewritten": False,
        "frozen_verifiers_rewritten": False,
        "historical_records_rewritten": False,
        "release_or_publication_actions_authorized": False,
    }
    if policy != required_policy:
        raise RuntimeError("SUCCESSOR_HISTORICAL_POLICY_FAILURE")

    return {
        "historical_surface_path_count": len(historical_surface),
        "current_override_set": override_set,
        "successor_changed_path_count": len(changed),
        "historical_ledger_entry_count": len(historical_ledger),
        "successor_ledger_entry_count": len(successor_ledger),
        "successor_transform_identity": "PASS",
    }


def repository_snapshot() -> dict[str, Any]:
    return {
        "head": git_text("rev-parse", "HEAD"),
        "status": git_text(
            "status", "--porcelain=v1", "--untracked-files=all"
        ),
        "refs_sha256": sha256_bytes(git_bytes("show-ref", "--head")),
        "worktrees_sha256": sha256_bytes(
            git_bytes("worktree", "list", "--porcelain")
        ),
    }


def execute_detached_replay(commit: str, commands: list[list[str]]) -> list[dict[str, Any]]:
    temp_root = Path(tempfile.mkdtemp(prefix="v0-osap-root-d-detached-"))
    worktree = temp_root / "worktree"
    added = False
    results: list[dict[str, Any]] = []
    try:
        require(
            "git", "worktree", "add", "--detach", str(worktree), commit,
            cwd=ROOT,
        )
        added = True
        replay_env = ENV.copy()
        replay_env.update({
            "CI": "true",
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_REF": "refs/heads/" + BRANCH,
            "GITHUB_REF_NAME": BRANCH,
        })
        for command in commands:
            resolved = list(command)
            if resolved and resolved[0] == "python":
                resolved[0] = sys.executable
            cp = require(*resolved, cwd=worktree, env=replay_env)
            results.append({
                "command": command,
                "return_code": cp.returncode,
                "stdout_sha256": sha256_bytes(cp.stdout.encode("utf-8")),
                "status": "PASS",
            })
        return results
    finally:
        if added:
            run(
                "git", "worktree", "remove", "--force", str(worktree),
                cwd=ROOT,
            )
        run("git", "worktree", "prune", "--expire", "now", cwd=ROOT)
        shutil.rmtree(temp_root, ignore_errors=True)


def validate_committed_surface(layer_head: str) -> None:
    expected = {SC_WORKFLOW: "M"}
    expected.update({path: "A" for path in ADDITIVE_PATHS})
    actual = diff_entries(PREDECESSOR, layer_head)
    if actual != expected:
        raise RuntimeError("COMMITTED_EXACT_SIX_PATH_SURFACE_FAILURE")

    manifest = load_manifest(ROOT)
    expected_workflow = expected_modified_workflow(manifest)
    predecessor_bytes = git_bytes("show", f"{PREDECESSOR}:{SC_WORKFLOW}")
    if predecessor_bytes != EXPECTED_PREDECESSOR_WORKFLOW.encode("utf-8"):
        raise RuntimeError("LIVE_PREDECESSOR_WORKFLOW_IDENTITY_FAILURE")
    if git_blob_sha1(predecessor_bytes) != EXPECTED_PREDECESSOR_WORKFLOW_BLOB_SHA1:
        raise RuntimeError("LIVE_PREDECESSOR_WORKFLOW_BLOB_FAILURE")

    for path in SURFACE_PATHS:
        committed = git_bytes("show", f"{layer_head}:{path}")
        worktree = (ROOT / path).read_bytes()
        if committed != worktree:
            raise RuntimeError("WORKTREE_LAYER_HEAD_IDENTITY_FAILURE:" + path)
    if git_bytes("show", f"{layer_head}:{SC_WORKFLOW}") != expected_workflow:
        raise RuntimeError("COMMITTED_WORKFLOW_DERIVATION_FAILURE")

    for path in ADDITIVE_PATHS:
        cp = run("git", "cat-file", "-e", f"{PREDECESSOR}:{path}")
        if cp.returncode == 0:
            raise RuntimeError("ADDITIVE_PREDECESSOR_ABSENCE_FAILURE:" + path)

    rows = parse_ledger(git_bytes("show", f"{layer_head}:{ROOT_D_LEDGER}"))
    if [path for _, path in rows] != ATTESTED_PATHS:
        raise RuntimeError("COMMITTED_LEDGER_PATH_SET_FAILURE")
    for digest, path in rows:
        if sha256_bytes(git_bytes("show", f"{layer_head}:{path}")) != digest:
            raise RuntimeError("COMMITTED_LEDGER_IDENTITY_FAILURE:" + path)


def verify_committed(execute_replay: bool = True) -> dict[str, Any]:
    before = repository_snapshot()
    if before["status"] != "":
        raise RuntimeError("SOURCE_REPOSITORY_NOT_CLEAN")

    package_result = verify_package(ROOT)
    layer_head = resolve_layer_head()
    validate_committed_surface(layer_head)
    chain = validate_chain_and_override()

    replay_results: dict[str, Any] = {
        "historical_successor_consumer": "NOT_EXECUTED",
        "successor_four_root": "NOT_EXECUTED",
    }
    if execute_replay:
        replay_results["historical_successor_consumer"] = execute_detached_replay(
            HISTORICAL_LAYER_HEAD,
            [
                [
                    "python",
                    HISTORICAL_VERIFIER,
                    "--mode",
                    "committed",
                    "--verify-eight-workflow-matrix",
                ],
                [
                    "python",
                    "-m",
                    "pytest",
                    "-q",
                    "-p",
                    "no:cacheprovider",
                    HISTORICAL_TEST,
                ],
            ],
        )
        replay_results["successor_four_root"] = execute_detached_replay(
            PREDECESSOR,
            [
                [
                    "python",
                    FOUR_ROOT_VERIFIER,
                    "--mode",
                    "committed",
                    "--verify-four-root-matrix",
                ],
                [
                    "python",
                    "-m",
                    "pytest",
                    "-q",
                    "-p",
                    "no:cacheprovider",
                    FOUR_ROOT_TEST,
                ],
            ],
        )

    after = repository_snapshot()
    if before != after:
        raise RuntimeError("IMMUTABLE_REPOSITORY_STATE_FAILURE")

    return {
        **package_result,
        "mode": "COMMITTED",
        "layer_head": layer_head,
        "predecessor": PREDECESSOR,
        "historical_layer_head": HISTORICAL_LAYER_HEAD,
        "chain_and_override": chain,
        "detached_replay": replay_results,
        "source_repository_mutation_performed": "NO",
        "git_control_mutation_residue": "NO",
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("package-only", "committed"),
        required=True,
    )
    parser.add_argument("--verify-root-d-contract", action="store_true")
    parser.add_argument(
        "--skip-detached-replay",
        action="store_true",
        help="Package-construction test hook; forbidden in hosted CI.",
    )
    args = parser.parse_args()
    try:
        if not args.verify_root_d_contract:
            raise RuntimeError("ROOT_D_OPERATION_REQUIRED")
        if args.skip_detached_replay and os.environ.get("CI") == "true":
            raise RuntimeError("HOSTED_CI_REPLAY_SKIP_FORBIDDEN")
        if args.mode == "package-only":
            if args.skip_detached_replay:
                raise RuntimeError("PACKAGE_ONLY_REPLAY_FLAG_INVALID")
            result = verify_package(ROOT)
        else:
            result = verify_committed(
                execute_replay=not args.skip_detached_replay
            )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {"error": str(exc), "status": "FAIL"},
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
