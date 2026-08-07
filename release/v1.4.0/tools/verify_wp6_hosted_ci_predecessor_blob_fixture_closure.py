#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[3]
BRANCH = 'v1.4.0-development'
PREDECESSOR = '466f820a313366c5f0bd4b23afaea44fe6fdc3b3'
PREDECESSOR_PARENT = '7aac3b8a992253666209cb9a2371eb00c0d749cd'
FOUR_ROOT_PREDECESSOR = '96a6164fd4fe6b8a85992df746672e4261fed8d3'

ROOT_D_WORKFLOW = '.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml'
SC_WORKFLOW = '.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml'
WORKFLOW = '.github/workflows/gate3-cluster-b-wp6-hosted-ci-predecessor-blob-fixture-closure.yml'
MANIFEST = 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE_MANIFEST.json'
LEDGER = 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE_SHA256SUMS.txt'
VERIFIER = 'release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_blob_fixture_closure.py'
TEST = 'tests/test_gate3_cluster_b_wp6_hosted_ci_predecessor_blob_fixture_closure.py'

ROOT_D_MANIFEST = "release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_MANIFEST.json"
ROOT_D_LEDGER = "release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_SHA256SUMS.txt"
ROOT_D_VERIFIER = "release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py"
ROOT_D_TEST = "tests/test_gate3_cluster_b_wp6_root_d_successor_attested_override.py"
FOUR_ROOT_VERIFIER = "release/v1.4.0/tools/verify_wp6_four_root_corrective_layer.py"
FOUR_ROOT_TEST = "tests/test_gate3_cluster_b_wp6_four_root_corrective_layer.py"

MODIFIED_PATHS = ['.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml', '.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml']
ADDITIVE_PATHS = ['.github/workflows/gate3-cluster-b-wp6-hosted-ci-predecessor-blob-fixture-closure.yml', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE_SHA256SUMS.txt', 'release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_blob_fixture_closure.py', 'tests/test_gate3_cluster_b_wp6_hosted_ci_predecessor_blob_fixture_closure.py']
ATTESTED_PATHS = ['.github/workflows/gate3-cluster-b-wp6-hosted-ci-predecessor-blob-fixture-closure.yml', '.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml', '.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE_MANIFEST.json', 'release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_blob_fixture_closure.py', 'tests/test_gate3_cluster_b_wp6_hosted_ci_predecessor_blob_fixture_closure.py']
SURFACE_PATHS = ['.github/workflows/gate3-cluster-b-wp6-hosted-ci-predecessor-blob-fixture-closure.yml', '.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml', '.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE_SHA256SUMS.txt', 'release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_blob_fixture_closure.py', 'tests/test_gate3_cluster_b_wp6_hosted_ci_predecessor_blob_fixture_closure.py']
FIXTURE_PATHS = [
    ".github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml",
    ".github/workflows/gate3-cluster-b-wp6-successor-attestation-layer.yml",
    ".github/workflows/gate3-cluster-b-wp6.yml",
]
FOUR_ROOT_ADDITIVE_PATHS = [
    ".github/workflows/gate3-cluster-b-wp6-four-root-corrective-layer.yml",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_FOUR_ROOT_CORRECTIVE_LAYER_MANIFEST.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP6_FOUR_ROOT_CORRECTIVE_LAYER_SHA256SUMS.txt",
    "release/v1.4.0/tools/verify_wp6_four_root_corrective_layer.py",
    "tests/test_gate3_cluster_b_wp6_four_root_corrective_layer.py",
]
FROZEN_ROOT_D_PATHS = [ROOT_D_MANIFEST, ROOT_D_LEDGER, ROOT_D_VERIFIER, ROOT_D_TEST]

EXPECTED_PREDECESSOR_WORKFLOWS = {'.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml': {'bytes': 'name: V0 OSAP Gate 3 Cluster B WP6 Root D Successor-Attested Override\n\non:\n  pull_request:\n    branches: [main]\n    paths:\n      - \'.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_MANIFEST.json\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_SHA256SUMS.txt\'\n      - \'release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py\'\n      - \'tests/test_gate3_cluster_b_wp6_root_d_successor_attested_override.py\'\n  push:\n    branches: [v1.4.0-development, main]\n    paths:\n      - \'.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_MANIFEST.json\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_SHA256SUMS.txt\'\n      - \'release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py\'\n      - \'tests/test_gate3_cluster_b_wp6_root_d_successor_attested_override.py\'\n  workflow_dispatch:\n\npermissions:\n  contents: read\n\njobs:\n  root-d-successor-attested-override:\n    runs-on: ubuntu-latest\n    env:\n      GIT_OPTIONAL_LOCKS: "0"\n      PYTHONDONTWRITEBYTECODE: "1"\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          fetch-depth: 0\n      - uses: actions/setup-python@v5\n        with:\n          python-version: "3.12"\n      - name: Install exact validation and detached replay dependencies\n        run: python -m pip install --disable-pip-version-check pytest jsonschema pyyaml\n      - name: Verify exact six-path Root D surface and successor-attested override contract\n        run: >-\n          python release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py\n          --mode committed\n          --verify-root-d-contract\n      - name: Dedicated Root D successor-attested override regression\n        run: >-\n          python -m pytest -q -p no:cacheprovider\n          tests/test_gate3_cluster_b_wp6_root_d_successor_attested_override.py\n      - name: Whitespace and exact Root D corrective-surface integrity\n        run: git diff --check 7aac3b8a992253666209cb9a2371eb00c0d749cd...HEAD\n', 'sha256': 'ceb3007e8311241cc6395d3fc65b10f3e63d6efda824e2ea960820ce43c1d018', 'blob_sha1': '7a91c2ea8fbe70e4eab665896b7d124543e56265'}, '.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml': {'bytes': 'name: V0 OSAP Gate 3 Cluster B WP6 Successor-Consumer Integration Corrective Layer\n\non:\n  pull_request:\n    branches: [main]\n    paths:\n      - \'.github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp2.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp3.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_MANIFEST.json\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_SHA256SUMS.txt\'\n      - \'release/v1.4.0/tools/verify_wp6_successor_consumer_integration_corrective_layer.py\'\n      - \'tests/test_gate3_cluster_b_wp6_successor_consumer_integration_corrective_layer.py\'\n      - \'.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_MANIFEST.json\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_SHA256SUMS.txt\'\n      - \'release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py\'\n      - \'tests/test_gate3_cluster_b_wp6_root_d_successor_attested_override.py\'\n  push:\n    branches: [v1.4.0-development, main]\n    paths:\n      - \'.github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp2.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp3.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5-sync-helper-repair.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp5.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-post-merge-closeout.yml\'\n      - \'.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_MANIFEST.json\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_SUCCESSOR_CONSUMER_INTEGRATION_CORRECTIVE_LAYER_SHA256SUMS.txt\'\n      - \'release/v1.4.0/tools/verify_wp6_successor_consumer_integration_corrective_layer.py\'\n      - \'tests/test_gate3_cluster_b_wp6_successor_consumer_integration_corrective_layer.py\'\n      - \'.github/workflows/gate3-cluster-b-wp6-root-d-successor-attested-override.yml\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_MANIFEST.json\'\n      - \'release/v1.4.0/GATE3_CLUSTER_B_WP6_ROOT_D_SUCCESSOR_ATTESTED_OVERRIDE_SHA256SUMS.txt\'\n      - \'release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py\'\n      - \'tests/test_gate3_cluster_b_wp6_root_d_successor_attested_override.py\'\n  workflow_dispatch:\n\npermissions:\n  contents: read\n\njobs:\n  successor-consumer-integration-corrective-layer:\n    runs-on: ubuntu-latest\n    env:\n      GIT_OPTIONAL_LOCKS: "0"\n      PYTHONDONTWRITEBYTECODE: "1"\n    steps:\n      - uses: actions/checkout@v4\n        with:\n          fetch-depth: 0\n      - uses: actions/setup-python@v5\n        with:\n          python-version: "3.12"\n      - name: Install exact Python validation dependencies\n        run: python -m pip install --disable-pip-version-check pytest jsonschema pyyaml\n      - name: Verify frozen historical layer through the Root D successor-attested override contract\n        run: >-\n          python release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py\n          --mode committed\n          --verify-root-d-contract\n      - name: Dedicated Root D successor-attested override regression\n        run: >-\n          python -m pytest -q -p no:cacheprovider\n          tests/test_gate3_cluster_b_wp6_root_d_successor_attested_override.py\n      - name: Whitespace and exact Root D corrective-surface integrity\n        run: git diff --check 7aac3b8a992253666209cb9a2371eb00c0d749cd...HEAD\n', 'sha256': '45b27ad09fb0311770c62566f2ad334b0d810c676fd938b53cf7dd03872d228d', 'blob_sha1': 'c478531cabb1ba7fea846700622a6fe00a4e4258'}}

ENV = os.environ.copy()
ENV.update({
    "GIT_OPTIONAL_LOCKS": "0",
    "PYTHONDONTWRITEBYTECODE": "1",
    "GIT_LFS_SKIP_SMUDGE": "1",
})


def run(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None,
        text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=cwd or ROOT, env=env or ENV, capture_output=True,
        text=text, check=False,
    )


def require(*args: str, cwd: Path | None = None,
            env: dict[str, str] | None = None,
            text: bool = True) -> subprocess.CompletedProcess:
    cp = run(*args, cwd=cwd, env=env, text=text)
    if cp.returncode:
        out = cp.stdout if text else cp.stdout.decode("utf-8", "replace")
        err = cp.stderr if text else cp.stderr.decode("utf-8", "replace")
        raise RuntimeError("$ " + " ".join(args) + "\n" + out + err)
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
    raw = (root / MANIFEST).read_bytes()
    value = json.loads(raw.decode("utf-8"))
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
        if len(digest) != 64 or any(
            ch not in "0123456789abcdef" for ch in digest
        ):
            raise RuntimeError(f"LEDGER_DIGEST_FAILURE:{ordinal}")
        if not path or path in seen:
            raise RuntimeError(f"LEDGER_PATH_FAILURE:{ordinal}")
        seen.add(path)
        rows.append((digest, path))
    return rows


def validate_text_file(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("PACKAGE_MEMBER_REGULAR_FILE_FAILURE:" + str(path))
    raw = path.read_bytes()
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise RuntimeError("PACKAGE_MEMBER_BYTE_CONTRACT_FAILURE:" + str(path))
    raw.decode("utf-8")


def validate_manifest(manifest: dict[str, Any]) -> None:
    expected_fields = sorted([
        "additive_path_count", "additive_paths", "artifact_id",
        "behavioral_contract", "branch", "byte_contract", "fixture_contract",
        "frozen_root_d_layer", "ledger_attested_path_count",
        "ledger_attested_paths", "ledger_path", "ledger_self_excluded",
        "modified_path_count", "modified_paths", "path_roles", "predecessor",
        "root_cause", "successor_four_root_layer", "total_path_count",
        "transformations", "version",
    ])
    if sorted(manifest) != expected_fields:
        raise RuntimeError("MANIFEST_TOP_LEVEL_FIELDS_FAILURE")
    scalar = {
        "artifact_id":
            "V0_OSAP_GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_BLOB_FIXTURE_CLOSURE",
        "version": "1.0",
        "branch": BRANCH,
        "modified_path_count": 2,
        "additive_path_count": 5,
        "total_path_count": 7,
        "ledger_attested_path_count": 6,
        "ledger_path": LEDGER,
        "ledger_self_excluded": True,
    }
    for key, expected in scalar.items():
        if manifest.get(key) != expected:
            raise RuntimeError("MANIFEST_SCALAR_FAILURE:" + key)
    if manifest.get("modified_paths") != MODIFIED_PATHS:
        raise RuntimeError("MANIFEST_MODIFIED_PATHS_FAILURE")
    if manifest.get("additive_paths") != ADDITIVE_PATHS:
        raise RuntimeError("MANIFEST_ADDITIVE_PATHS_FAILURE")
    if manifest.get("ledger_attested_paths") != ATTESTED_PATHS:
        raise RuntimeError("MANIFEST_ATTESTED_PATHS_FAILURE")
    predecessor = manifest.get("predecessor") or {}
    if predecessor.get("commit") != PREDECESSOR:
        raise RuntimeError("MANIFEST_PREDECESSOR_COMMIT_FAILURE")
    if predecessor.get("parent") != PREDECESSOR_PARENT:
        raise RuntimeError("MANIFEST_PREDECESSOR_PARENT_FAILURE")
    root_d = manifest.get("frozen_root_d_layer") or {}
    if root_d.get("exact_head") != PREDECESSOR:
        raise RuntimeError("MANIFEST_ROOT_D_HEAD_FAILURE")
    if root_d.get("rewrite_authorized") is not False:
        raise RuntimeError("MANIFEST_ROOT_D_REWRITE_POLICY_FAILURE")
    fixture = manifest.get("fixture_contract") or {}
    if fixture.get("source_commit") != FOUR_ROOT_PREDECESSOR:
        raise RuntimeError("MANIFEST_FIXTURE_SOURCE_FAILURE")
    if fixture.get("fixture_paths") != FIXTURE_PATHS:
        raise RuntimeError("MANIFEST_FIXTURE_PATHS_FAILURE")
    if fixture.get("fixture_path_count") != 3:
        raise RuntimeError("MANIFEST_FIXTURE_COUNT_FAILURE")
    if fixture.get("environment_variable") != "V0_OSAP_PREDECESSOR_BLOB_DIR":
        raise RuntimeError("MANIFEST_FIXTURE_ENVIRONMENT_FAILURE")
    if fixture.get("additive_paths_present") is not False:
        raise RuntimeError("MANIFEST_FIXTURE_ADDITIVE_ABSENCE_FAILURE")
    contract = (manifest.get("behavioral_contract") or {}).get("clauses") or {}
    required_true = {
        "additive_predecessor_absence_required",
        "circular_self_trust_forbidden",
        "fixture_additive_paths_forbidden",
        "fixture_cleanup_required",
        "fixture_environment_scope_is_successor_four_root_replay_only",
        "fixture_exact_three_path_materialization_required",
        "fixture_source_commit_is_exact",
        "frozen_root_d_artifact_rewrite_forbidden",
        "frozen_root_d_replay_required",
        "historical_four_root_artifact_rewrite_forbidden",
        "repository_and_git_control_residue_forbidden",
        "two_failed_workflows_must_route_through_successor_closure",
    }
    if set(contract) != required_true or any(contract[k] is not True for k in required_true):
        raise RuntimeError("MANIFEST_BEHAVIORAL_CLAUSES_FAILURE")
    transformations = manifest.get("transformations")
    if not isinstance(transformations, list) or len(transformations) != 2:
        raise RuntimeError("MANIFEST_TRANSFORMATION_COUNT_FAILURE")
    if [item.get("path") for item in transformations] != MODIFIED_PATHS:
        raise RuntimeError("MANIFEST_TRANSFORMATION_ORDER_FAILURE")


def transformation_records(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    validate_manifest(manifest)
    return {item["path"]: item for item in manifest["transformations"]}


def expected_modified_bytes(manifest: dict[str, Any]) -> dict[str, bytes]:
    records = transformation_records(manifest)
    output: dict[str, bytes] = {}
    for path in MODIFIED_PATHS:
        source = EXPECTED_PREDECESSOR_WORKFLOWS[path]["bytes"].encode("utf-8")
        expected = EXPECTED_PREDECESSOR_WORKFLOWS[path]
        if sha256_bytes(source) != expected["sha256"]:
            raise RuntimeError("EMBEDDED_PREDECESSOR_SHA256_FAILURE:" + path)
        if git_blob_sha1(source) != expected["blob_sha1"]:
            raise RuntimeError("EMBEDDED_PREDECESSOR_BLOB_FAILURE:" + path)
        item = records[path]
        if item.get("predecessor_sha256") != expected["sha256"]:
            raise RuntimeError("MANIFEST_PREDECESSOR_SHA256_FAILURE:" + path)
        if item.get("predecessor_blob_sha1") != expected["blob_sha1"]:
            raise RuntimeError("MANIFEST_PREDECESSOR_BLOB_FAILURE:" + path)
        text = source.decode("utf-8")
        replacements = item.get("replacements")
        if not isinstance(replacements, list) or len(replacements) != item.get("replacement_count"):
            raise RuntimeError("TRANSFORMATION_REPLACEMENT_LIST_FAILURE:" + path)
        for ordinal, replacement in enumerate(replacements, 1):
            if replacement.get("ordinal") != ordinal:
                raise RuntimeError("TRANSFORMATION_ORDINAL_FAILURE:" + path)
            old = replacement.get("old")
            new = replacement.get("new")
            if not isinstance(old, str) or not isinstance(new, str):
                raise RuntimeError("TRANSFORMATION_TYPE_FAILURE:" + path)
            if replacement.get("old_sha256") != sha256_bytes(old.encode("utf-8")):
                raise RuntimeError("TRANSFORMATION_OLD_DIGEST_FAILURE:" + path)
            if replacement.get("new_sha256") != sha256_bytes(new.encode("utf-8")):
                raise RuntimeError("TRANSFORMATION_NEW_DIGEST_FAILURE:" + path)
            if replacement.get("predecessor_anchor_count") != 1 or text.count(old) != 1:
                raise RuntimeError("TRANSFORMATION_ANCHOR_COUNT_FAILURE:" + path)
            text = text.replace(old, new, 1)
        data = text.encode("utf-8")
        if not data.endswith(b"\n") or b"\r" in data:
            raise RuntimeError("TRANSFORMATION_BYTE_CONTRACT_FAILURE:" + path)
        output[path] = data
    return output


def validate_ledger(root: Path = ROOT) -> dict[str, str]:
    rows = parse_ledger((root / LEDGER).read_bytes())
    if [path for _, path in rows] != ATTESTED_PATHS:
        raise RuntimeError("LEDGER_ATTESTED_PATH_SET_FAILURE")
    if LEDGER in [path for _, path in rows]:
        raise RuntimeError("LEDGER_SELF_EXCLUSION_FAILURE")
    result: dict[str, str] = {}
    for digest, path in rows:
        actual = sha256_bytes((root / path).read_bytes())
        if actual != digest:
            raise RuntimeError("LEDGER_IDENTITY_FAILURE:" + path)
        result[path] = digest
    return result


def validate_workflow_semantics(root: Path = ROOT) -> None:
    required_paths = SURFACE_PATHS
    required_markers = [
        VERIFIER,
        TEST,
        "--verify-hosted-ci-predecessor-blob-fixture-closure",
        "pytest jsonschema pyyaml",
        f"git diff --check {PREDECESSOR}...HEAD",
    ]
    for relative in [ROOT_D_WORKFLOW, SC_WORKFLOW, WORKFLOW]:
        text = (root / relative).read_text(encoding="utf-8")
        for path in required_paths:
            if path not in text:
                raise RuntimeError("WORKFLOW_TRIGGER_PATH_MISSING:" + relative + ":" + path)
        for marker in required_markers:
            if marker not in text:
                raise RuntimeError("WORKFLOW_MARKER_MISSING:" + relative + ":" + marker)
        if ROOT_D_VERIFIER + "\n          --mode committed" in text:
            raise RuntimeError("WORKFLOW_DIRECT_FROZEN_ROOT_D_EXECUTION:" + relative)
        if yaml is None:
            raise RuntimeError("PYYAML_UNAVAILABLE")
        parsed = yaml.safe_load(text)
        if not isinstance(parsed, dict) or "jobs" not in parsed:
            raise RuntimeError("WORKFLOW_YAML_STRUCTURE_FAILURE:" + relative)


def verify_package(root: Path = ROOT) -> dict[str, Any]:
    for relative in SURFACE_PATHS:
        validate_text_file(root / relative)
    manifest = load_manifest(root)
    validate_manifest(manifest)
    expected = expected_modified_bytes(manifest)
    for path, data in expected.items():
        if (root / path).read_bytes() != data:
            raise RuntimeError("MODIFIED_WORKFLOW_DERIVATION_FAILURE:" + path)
    validate_ledger(root)
    validate_workflow_semantics(root)
    for relative in [VERIFIER, TEST]:
        ast.parse((root / relative).read_text(encoding="utf-8"), filename=relative)
    return {
        "status": "PASS",
        "mode": "PACKAGE_ONLY",
        "modified_path_count": 2,
        "additive_path_count": 5,
        "total_path_count": 7,
        "ledger_attested_path_count": 6,
        "fixture_path_count": 3,
        "fixture_source_commit": FOUR_ROOT_PREDECESSOR,
        "root_cause":
            "ROOT_D_DETACHED_FOUR_ROOT_REPLAY_PREDECESSOR_BLOB_FIXTURE_OMISSION",
    }


def git_text(*args: str, cwd: Path = ROOT) -> str:
    return require("git", *args, cwd=cwd).stdout.rstrip("\n")


def git_bytes(*args: str, cwd: Path = ROOT) -> bytes:
    return require("git", *args, cwd=cwd, text=False).stdout


def diff_entries(base: str, head: str) -> dict[str, str]:
    output = git_text("diff", "--name-status", "--no-renames", base, head, "--")
    rows: dict[str, str] = {}
    for line in output.splitlines():
        if line:
            code, path = line.split("\t", 1)
            rows[path] = code
    return rows


def repository_snapshot() -> dict[str, str]:
    return {
        "head": git_text("rev-parse", "HEAD"),
        "status": git_text("status", "--porcelain=v1", "--untracked-files=all"),
        "refs_sha256": sha256_bytes(git_bytes("show-ref", "--head")),
        "worktrees_sha256": sha256_bytes(
            git_bytes("worktree", "list", "--porcelain")
        ),
    }


def resolve_layer_head() -> str:
    expected = {path: "M" for path in MODIFIED_PATHS}
    expected.update({path: "A" for path in ADDITIVE_PATHS})
    candidates = [git_text("rev-parse", "HEAD")]
    env_sha = os.environ.get("GITHUB_SHA", "").strip()
    if env_sha:
        candidates.append(env_sha)
    matches: list[str] = []
    for candidate in dict.fromkeys(candidates):
        if run("git", "cat-file", "-e", candidate + "^{commit}").returncode:
            continue
        if git_text("rev-parse", candidate + "^") != PREDECESSOR:
            continue
        if diff_entries(PREDECESSOR, candidate) == expected:
            matches.append(candidate)
    if len(matches) != 1:
        raise RuntimeError("LAYER_HEAD_RESOLUTION_FAILURE:" + repr(matches))
    return matches[0]


def validate_committed_surface(layer_head: str) -> None:
    expected = {path: "M" for path in MODIFIED_PATHS}
    expected.update({path: "A" for path in ADDITIVE_PATHS})
    if diff_entries(PREDECESSOR, layer_head) != expected:
        raise RuntimeError("COMMITTED_EXACT_SEVEN_PATH_SURFACE_FAILURE")
    manifest = load_manifest(ROOT)
    expected_modified = expected_modified_bytes(manifest)
    for path in MODIFIED_PATHS:
        predecessor_bytes = git_bytes("show", f"{PREDECESSOR}:{path}")
        embedded = EXPECTED_PREDECESSOR_WORKFLOWS[path]["bytes"].encode("utf-8")
        if predecessor_bytes != embedded:
            raise RuntimeError("LIVE_PREDECESSOR_WORKFLOW_IDENTITY_FAILURE:" + path)
        committed = git_bytes("show", f"{layer_head}:{path}")
        if committed != expected_modified[path]:
            raise RuntimeError("COMMITTED_WORKFLOW_DERIVATION_FAILURE:" + path)
    for path in ADDITIVE_PATHS:
        if run("git", "cat-file", "-e", f"{PREDECESSOR}:{path}").returncode == 0:
            raise RuntimeError("ADDITIVE_PREDECESSOR_ABSENCE_FAILURE:" + path)
    for path in FROZEN_ROOT_D_PATHS:
        if git_bytes("show", f"{layer_head}:{path}") != git_bytes("show", f"{PREDECESSOR}:{path}"):
            raise RuntimeError("FROZEN_ROOT_D_ARTIFACT_REWRITE_FAILURE:" + path)
    rows = parse_ledger(git_bytes("show", f"{layer_head}:{LEDGER}"))
    if [path for _, path in rows] != ATTESTED_PATHS:
        raise RuntimeError("COMMITTED_LEDGER_PATH_SET_FAILURE")
    for digest, path in rows:
        if sha256_bytes(git_bytes("show", f"{layer_head}:{path}")) != digest:
            raise RuntimeError("COMMITTED_LEDGER_IDENTITY_FAILURE:" + path)


def materialize_predecessor_fixture(
    fixture_root: Path,
    provider: Callable[[str], bytes] | None = None,
) -> dict[str, str]:
    if fixture_root.exists():
        raise RuntimeError("FIXTURE_ROOT_ALREADY_EXISTS")
    fixture_root.mkdir(parents=True)
    provider = provider or (
        lambda relative: git_bytes("show", f"{FOUR_ROOT_PREDECESSOR}:{relative}")
    )
    identities: dict[str, str] = {}
    for relative in FIXTURE_PATHS:
        data = provider(relative)
        target = fixture_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        identities[relative] = sha256_bytes(data)
    actual_files = sorted(
        str(path.relative_to(fixture_root))
        for path in fixture_root.rglob("*") if path.is_file()
    )
    if actual_files != FIXTURE_PATHS:
        raise RuntimeError("FIXTURE_EXACT_PATH_SET_FAILURE")
    for relative in FOUR_ROOT_ADDITIVE_PATHS:
        if (fixture_root / relative).exists():
            raise RuntimeError("FIXTURE_ADDITIVE_PATH_PRESENCE_FAILURE:" + relative)
    return identities


def execute_frozen_root_d_replay() -> dict[str, Any]:
    temp_root = Path(tempfile.mkdtemp(prefix="v0-osap-fixture-closure-"))
    worktree = temp_root / "root-d-worktree"
    fixture = temp_root / "predecessor-blobs"
    added = False
    try:
        materialize_predecessor_fixture(fixture)
        require("git", "worktree", "add", "--detach", str(worktree), PREDECESSOR)
        added = True
        replay_env = ENV.copy()
        replay_env.update({
            "CI": "true",
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_REF": "refs/heads/" + BRANCH,
            "GITHUB_REF_NAME": BRANCH,
            "V0_OSAP_PREDECESSOR_BLOB_DIR": str(fixture),
        })
        commands = [
            [
                sys.executable,
                ROOT_D_VERIFIER,
                "--mode", "committed",
                "--verify-root-d-contract",
            ],
            [
                sys.executable,
                "-m", "pytest", "-q", "-p", "no:cacheprovider",
                ROOT_D_TEST,
            ],
        ]
        results: list[dict[str, Any]] = []
        for command in commands:
            cp = require(*command, cwd=worktree, env=replay_env)
            results.append({
                "command": command,
                "return_code": cp.returncode,
                "stdout_sha256": sha256_bytes(cp.stdout.encode("utf-8")),
                "status": "PASS",
            })
        return {
            "fixture_source_commit": FOUR_ROOT_PREDECESSOR,
            "fixture_path_count": len(FIXTURE_PATHS),
            "fixture_environment_variable":
                "V0_OSAP_PREDECESSOR_BLOB_DIR",
            "frozen_root_d_head": PREDECESSOR,
            "results": results,
            "status": "PASS",
        }
    finally:
        if added:
            run("git", "worktree", "remove", "--force", str(worktree), cwd=ROOT)
        run("git", "worktree", "prune", "--expire", "now", cwd=ROOT)
        shutil.rmtree(temp_root, ignore_errors=True)


def verify_committed() -> dict[str, Any]:
    before = repository_snapshot()
    if before["status"]:
        raise RuntimeError("SOURCE_REPOSITORY_NOT_CLEAN")
    package_result = verify_package(ROOT)
    layer_head = resolve_layer_head()
    validate_committed_surface(layer_head)
    replay = execute_frozen_root_d_replay()
    after = repository_snapshot()
    if before != after:
        raise RuntimeError("IMMUTABLE_REPOSITORY_STATE_FAILURE")
    return {
        **package_result,
        "mode": "COMMITTED",
        "layer_head": layer_head,
        "predecessor": PREDECESSOR,
        "frozen_root_d_replay": replay,
        "source_repository_mutation_performed": "NO",
        "git_control_mutation_residue": "NO",
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("package-only", "committed"), required=True)
    parser.add_argument(
        "--verify-hosted-ci-predecessor-blob-fixture-closure",
        action="store_true",
    )
    args = parser.parse_args()
    try:
        if not args.verify_hosted_ci_predecessor_blob_fixture_closure:
            raise RuntimeError("FIXTURE_CLOSURE_OPERATION_REQUIRED")
        result = verify_package(ROOT) if args.mode == "package-only" else verify_committed()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "status": "FAIL"},
                         indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
