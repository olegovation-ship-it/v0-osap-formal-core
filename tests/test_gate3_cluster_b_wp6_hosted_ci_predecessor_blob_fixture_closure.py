from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / 'release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_blob_fixture_closure.py'
SPEC = importlib.util.spec_from_file_location("wp6_fixture_closure_verifier", VERIFIER_PATH)
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


def write_manifest(root: Path, value: dict) -> None:
    (root / MODULE.MANIFEST).write_bytes(MODULE.canonical_json(value))


def test_exact_seven_path_surface_constants() -> None:
    assert len(MODULE.MODIFIED_PATHS) == 2
    assert len(MODULE.ADDITIVE_PATHS) == 5
    assert len(MODULE.SURFACE_PATHS) == 7
    assert len(MODULE.ATTESTED_PATHS) == 6
    assert MODULE.LEDGER not in MODULE.ATTESTED_PATHS


def test_package_only_contract_passes() -> None:
    result = MODULE.verify_package(ROOT)
    assert result["status"] == "PASS"
    assert result["fixture_path_count"] == 3
    assert result["total_path_count"] == 7


def test_manifest_is_canonical_and_exact() -> None:
    raw = (ROOT / MODULE.MANIFEST).read_bytes()
    value = json.loads(raw.decode("utf-8"))
    assert raw == MODULE.canonical_json(value)
    MODULE.validate_manifest(value)


def test_exact_two_workflow_derivation() -> None:
    value = MODULE.load_manifest(ROOT)
    expected = MODULE.expected_modified_bytes(value)
    assert sorted(expected) == MODULE.MODIFIED_PATHS
    for path, data in expected.items():
        assert data == (ROOT / path).read_bytes()


def test_ledger_is_self_excluding_and_complete() -> None:
    rows = MODULE.parse_ledger((ROOT / MODULE.LEDGER).read_bytes())
    assert [path for _, path in rows] == MODULE.ATTESTED_PATHS
    assert MODULE.LEDGER not in [path for _, path in rows]
    MODULE.validate_ledger(ROOT)


def test_workflows_parse_and_route_through_successor() -> None:
    MODULE.validate_workflow_semantics(ROOT)
    for relative in [MODULE.ROOT_D_WORKFLOW, MODULE.SC_WORKFLOW, MODULE.WORKFLOW]:
        parsed = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
        assert isinstance(parsed, dict)
        assert "jobs" in parsed


def test_frozen_root_d_direct_execution_removed() -> None:
    marker = MODULE.ROOT_D_VERIFIER + "\n          --mode committed"
    for relative in [MODULE.ROOT_D_WORKFLOW, MODULE.SC_WORKFLOW]:
        assert marker not in (ROOT / relative).read_text(encoding="utf-8")


def test_fixture_contract_is_exact_three_paths() -> None:
    value = MODULE.load_manifest(ROOT)["fixture_contract"]
    assert value["source_commit"] == MODULE.FOUR_ROOT_PREDECESSOR
    assert value["fixture_paths"] == MODULE.FIXTURE_PATHS
    assert value["fixture_path_count"] == 3
    assert value["additive_paths_present"] is False


def test_materialize_fixture_exact_paths(tmp_path: Path) -> None:
    payloads = {path: (path + "\n").encode() for path in MODULE.FIXTURE_PATHS}
    result = MODULE.materialize_predecessor_fixture(
        tmp_path / "fixture",
        provider=lambda path: payloads[path],
    )
    assert sorted(result) == MODULE.FIXTURE_PATHS
    actual = sorted(
        str(p.relative_to(tmp_path / "fixture"))
        for p in (tmp_path / "fixture").rglob("*") if p.is_file()
    )
    assert actual == MODULE.FIXTURE_PATHS


def test_materialize_fixture_rejects_existing_root(tmp_path: Path) -> None:
    target = tmp_path / "fixture"
    target.mkdir()
    with pytest.raises(RuntimeError, match="FIXTURE_ROOT_ALREADY_EXISTS"):
        MODULE.materialize_predecessor_fixture(target, provider=lambda _: b"x\n")


def test_reject_wrong_fixture_source_commit() -> None:
    value = copy.deepcopy(MODULE.load_manifest(ROOT))
    value["fixture_contract"]["source_commit"] = "0" * 40
    with pytest.raises(RuntimeError, match="MANIFEST_FIXTURE_SOURCE_FAILURE"):
        MODULE.validate_manifest(value)


def test_reject_wrong_fixture_path_set() -> None:
    value = copy.deepcopy(MODULE.load_manifest(ROOT))
    value["fixture_contract"]["fixture_paths"] = value["fixture_contract"]["fixture_paths"][:2]
    with pytest.raises(RuntimeError, match="MANIFEST_FIXTURE_PATHS_FAILURE"):
        MODULE.validate_manifest(value)


def test_reject_fixture_additive_presence_authorization() -> None:
    value = copy.deepcopy(MODULE.load_manifest(ROOT))
    value["fixture_contract"]["additive_paths_present"] = True
    with pytest.raises(RuntimeError, match="MANIFEST_FIXTURE_ADDITIVE_ABSENCE_FAILURE"):
        MODULE.validate_manifest(value)


def test_reject_frozen_root_d_rewrite_authorization() -> None:
    value = copy.deepcopy(MODULE.load_manifest(ROOT))
    value["frozen_root_d_layer"]["rewrite_authorized"] = True
    with pytest.raises(RuntimeError, match="MANIFEST_ROOT_D_REWRITE_POLICY_FAILURE"):
        MODULE.validate_manifest(value)


def test_reject_missing_behavioral_clause() -> None:
    value = copy.deepcopy(MODULE.load_manifest(ROOT))
    del value["behavioral_contract"]["clauses"]["fixture_cleanup_required"]
    with pytest.raises(RuntimeError, match="MANIFEST_BEHAVIORAL_CLAUSES_FAILURE"):
        MODULE.validate_manifest(value)


def test_reject_wrong_predecessor_blob_binding() -> None:
    value = copy.deepcopy(MODULE.load_manifest(ROOT))
    value["transformations"][0]["predecessor_blob_sha1"] = "0" * 40
    with pytest.raises(RuntimeError, match="MANIFEST_PREDECESSOR_BLOB_FAILURE"):
        MODULE.expected_modified_bytes(value)


def test_reject_non_unique_transformation_anchor() -> None:
    value = copy.deepcopy(MODULE.load_manifest(ROOT))
    item = value["transformations"][0]["replacements"][0]
    item["old"] = "      - "
    item["old_sha256"] = hashlib.sha256(item["old"].encode()).hexdigest()
    with pytest.raises(RuntimeError, match="TRANSFORMATION_ANCHOR_COUNT_FAILURE"):
        MODULE.expected_modified_bytes(value)


def test_reject_ledger_self_inclusion(tmp_path: Path) -> None:
    root = copy_surface(tmp_path)
    ledger = root / MODULE.LEDGER
    ledger.write_text(
        ledger.read_text(encoding="utf-8")
        + ("0" * 64) + "  " + MODULE.LEDGER + "\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="LEDGER_ATTESTED_PATH_SET_FAILURE"):
        MODULE.validate_ledger(root)


def test_reject_modified_workflow_byte_drift(tmp_path: Path) -> None:
    root = copy_surface(tmp_path)
    path = root / MODULE.ROOT_D_WORKFLOW
    path.write_bytes(path.read_bytes() + b"# drift\n")
    with pytest.raises(RuntimeError, match="MODIFIED_WORKFLOW_DERIVATION_FAILURE"):
        MODULE.verify_package(root)


def test_python_sources_compile() -> None:
    for relative in [MODULE.VERIFIER, MODULE.TEST]:
        compile((ROOT / relative).read_text(encoding="utf-8"), relative, "exec")
