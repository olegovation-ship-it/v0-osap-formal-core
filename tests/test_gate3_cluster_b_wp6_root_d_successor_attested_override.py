from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / 'release/v1.4.0/tools/verify_wp6_root_d_successor_attested_override.py'
SPEC = importlib.util.spec_from_file_location(
    "wp6_root_d_successor_attested_override_verifier",
    VERIFIER_PATH,
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def copy_surface(tmp_path: Path) -> Path:
    for relative in MODULE.SURFACE_PATHS:
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    return tmp_path


def write_manifest(root: Path, manifest: dict) -> None:
    (root / MODULE.ROOT_D_MANIFEST).write_bytes(
        MODULE.canonical_json(manifest)
    )


def test_exact_six_path_surface_constants() -> None:
    assert MODULE.MODIFIED_PATHS == ['.github/workflows/gate3-cluster-b-wp6-successor-consumer-integration-corrective-layer.yml']
    assert len(MODULE.ADDITIVE_PATHS) == 5
    assert len(MODULE.SURFACE_PATHS) == 6
    assert MODULE.ROOT_D_LEDGER not in MODULE.ATTESTED_PATHS
    assert len(MODULE.ATTESTED_PATHS) == 5


def test_package_only_contract_passes() -> None:
    result = MODULE.verify_package(ROOT)
    assert result["status"] == "PASS"
    assert result["modified_path_count"] == 1
    assert result["additive_path_count"] == 5
    assert result["total_path_count"] == 6


def test_embedded_predecessor_workflow_identity() -> None:
    data = MODULE.EXPECTED_PREDECESSOR_WORKFLOW.encode("utf-8")
    assert MODULE.sha256_bytes(data) == (
        MODULE.EXPECTED_PREDECESSOR_WORKFLOW_SHA256
    )
    assert MODULE.git_blob_sha1(data) == (
        MODULE.EXPECTED_PREDECESSOR_WORKFLOW_BLOB_SHA1
    )
    assert MODULE.EXPECTED_PREDECESSOR_WORKFLOW_BLOB_SHA1 == (
        "786d077571800232181aaf732f60ba9ff695560f"
    )


def test_manifest_is_canonical_and_exact() -> None:
    raw = (ROOT / MODULE.ROOT_D_MANIFEST).read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    assert raw == MODULE.canonical_json(manifest)
    MODULE.validate_manifest(manifest)


def test_exact_workflow_derivation_from_predecessor() -> None:
    manifest = MODULE.load_manifest(ROOT)
    expected = MODULE.expected_modified_workflow(manifest)
    actual = (ROOT / MODULE.SC_WORKFLOW).read_bytes()
    assert expected == actual
    assert actual != MODULE.EXPECTED_PREDECESSOR_WORKFLOW.encode("utf-8")


def test_ledger_is_self_excluding_and_identity_complete() -> None:
    rows = MODULE.parse_ledger(
        (ROOT / MODULE.ROOT_D_LEDGER).read_bytes()
    )
    assert [path for _, path in rows] == MODULE.ATTESTED_PATHS
    assert MODULE.ROOT_D_LEDGER not in [path for _, path in rows]
    MODULE.validate_ledger(ROOT)


def test_workflows_parse_and_route_through_root_d() -> None:
    MODULE.validate_workflow_semantics(ROOT)
    for relative in [MODULE.SC_WORKFLOW, MODULE.ROOT_D_WORKFLOW]:
        parsed = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
        assert isinstance(parsed, dict)
        assert "jobs" in parsed


def test_modified_workflow_no_longer_executes_frozen_verifier_directly() -> None:
    text = (ROOT / MODULE.SC_WORKFLOW).read_text(encoding="utf-8")
    assert (
        "python release/v1.4.0/tools/"
        "verify_wp6_successor_consumer_integration_corrective_layer.py"
    ) not in text
    assert (
        "python -m pytest -q -p no:cacheprovider\n"
        "          tests/test_gate3_cluster_b_wp6_"
        "successor_consumer_integration_corrective_layer.py"
    ) not in text
    assert MODULE.ROOT_D_VERIFIER in text
    assert MODULE.ROOT_D_TEST in text


def test_root_d_workflow_triggers_exact_surface() -> None:
    text = (ROOT / MODULE.ROOT_D_WORKFLOW).read_text(encoding="utf-8")
    for path in MODULE.SURFACE_PATHS:
        assert text.count(path) >= 2
    assert f"git diff --check {MODULE.PREDECESSOR}...HEAD" in text


def test_reject_wrong_authorized_override_set() -> None:
    manifest = copy.deepcopy(MODULE.load_manifest(ROOT))
    manifest["override_contract"]["exact_authorized_override_set"] = []
    with pytest.raises(RuntimeError, match="MANIFEST_OVERRIDE_SET_FAILURE"):
        MODULE.validate_manifest(manifest)


def test_reject_noncontiguous_override_contract() -> None:
    manifest = copy.deepcopy(MODULE.load_manifest(ROOT))
    manifest["override_contract"]["clauses"][
        "chain_contiguity_required"
    ] = False
    with pytest.raises(RuntimeError, match="MANIFEST_OVERRIDE_CLAUSES_FAILURE"):
        MODULE.validate_manifest(manifest)


def test_reject_historical_rewrite_authorization() -> None:
    manifest = copy.deepcopy(MODULE.load_manifest(ROOT))
    manifest["historical_successor_consumer_layer"][
        "rewrite_authorized"
    ] = True
    with pytest.raises(
        RuntimeError,
        match="MANIFEST_HISTORICAL_REWRITE_POLICY_FAILURE",
    ):
        MODULE.validate_manifest(manifest)


def test_reject_wrong_predecessor_blob_binding() -> None:
    manifest = copy.deepcopy(MODULE.load_manifest(ROOT))
    manifest["transformations"][0]["predecessor_blob_sha1"] = "0" * 40
    with pytest.raises(RuntimeError, match="MANIFEST_PREDECESSOR_BLOB_FAILURE"):
        MODULE.expected_modified_workflow(manifest)


def test_reject_missing_transformation_anchor() -> None:
    manifest = copy.deepcopy(MODULE.load_manifest(ROOT))
    replacement = manifest["transformations"][0]["replacements"][0]
    replacement["old"] = "ABSENT_UNIQUE_ANCHOR\n"
    replacement["old_sha256"] = hashlib.sha256(
        replacement["old"].encode("utf-8")
    ).hexdigest()
    with pytest.raises(RuntimeError, match="TRANSFORMATION_ANCHOR_COUNT_FAILURE"):
        MODULE.expected_modified_workflow(manifest)


def test_reject_ledger_self_inclusion(tmp_path: Path) -> None:
    root = copy_surface(tmp_path)
    ledger = root / MODULE.ROOT_D_LEDGER
    ledger.write_text(
        ledger.read_text(encoding="utf-8")
        + ("0" * 64)
        + "  "
        + MODULE.ROOT_D_LEDGER
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="LEDGER_ATTESTED_PATH_SET_FAILURE"):
        MODULE.validate_ledger(root)


def test_reject_modified_workflow_byte_drift(tmp_path: Path) -> None:
    root = copy_surface(tmp_path)
    workflow = root / MODULE.SC_WORKFLOW
    workflow.write_text(
        workflow.read_text(encoding="utf-8").replace(
            "Root D successor-attested override regression",
            "Root D unauthorized drift",
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="MODIFIED_WORKFLOW_DERIVATION_FAILURE"):
        MODULE.verify_package(root)


def test_python_sources_are_parseable() -> None:
    for relative in [MODULE.ROOT_D_VERIFIER, MODULE.ROOT_D_TEST]:
        compile(
            (ROOT / relative).read_text(encoding="utf-8"),
            relative,
            "exec",
        )
