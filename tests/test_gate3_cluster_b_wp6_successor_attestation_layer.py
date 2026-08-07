from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "release/v1.4.0/tools/verify_wp6_successor_attestation_layer.py"
SPEC = importlib.util.spec_from_file_location("wp6_successor_attestation_v02", VERIFIER_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_manifest_is_exact_canonical_v02() -> None:
    data = (ROOT / MODULE.MANIFEST).read_bytes()
    actual = json.loads(data.decode("utf-8"))
    assert actual == MODULE.EXPECTED_MANIFEST
    assert data == (
        json.dumps(actual, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    assert actual["version"] == "0.2"
    assert actual["unresolved_dependency_count"] == 0


def test_explicit_runtime_dependency_closure() -> None:
    workflow = (ROOT / MODULE.WORKFLOW).read_text(encoding="utf-8")
    exact = "python -m pip install --disable-pip-version-check pytest jsonschema"
    assert exact in workflow
    assert MODULE.EXPECTED_MANIFEST["corrective_reconstruction"][
        "explicit_runtime_dependency_closure"
    ]["pip_command"] == exact
    assert jsonschema.Draft202012Validator is not None
    assert pytest.__version__


def test_executable_four_root_digest_derivation() -> None:
    roots = MODULE.verify_four_roots()
    assert len(roots) == 4
    by_path = {row["path"]: row for row in roots}
    assert by_path[
        ".github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml"
    ]["sha256"] == "4f586cbd6624ca12beeeb2724843d8ba0723d1edb5297c23dd5159adae1394c8"
    assert by_path[
        "release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py"
    ]["sha256"] == "c434b920de60134ef492e89067da14812d4da21c9ca21d10a41dfe551d0a32eb"
    assert by_path[MODULE.WP3_LEDGER]["reconstructed_sha256"] == (
        "161c2064d81774f9adcc947f9af5ed82273bec9ebd1922c5d997104686d59fc3"
    )
    assert by_path[MODULE.WP5_LEDGER]["reconstructed_sha256"] == (
        "2cafecf875967dc1586bf5a353d671e770d2bba81bd0c775bd06197dd34bef0c"
    )


def test_predecessor_v09_surface_and_frozen_boundary() -> None:
    MODULE.verify_predecessor_identity()
    MODULE.verify_frozen_boundary()
    result = MODULE.verify_v09_surface()
    assert result["predecessor_artifact_change_count"] == 0
    assert result["ledger_sha256"] == "a311b72420ceae985f3365caa554a58095a558947a20afe2e147c63074f7a1d0"


def test_successor_ledger_is_exact_and_self_excluding() -> None:
    result = MODULE.verify_successor_ledger()
    assert result["entry_count"] == 4
    assert result["self_excluded"] is True
    rows = MODULE.parse_ledger_bytes(
        (ROOT / MODULE.LEDGER).read_bytes(), MODULE.LEDGER
    )
    paths = [path for _, path in rows]
    assert paths == sorted([
        MODULE.WORKFLOW,
        MODULE.MANIFEST,
        MODULE.VERIFIER,
        MODULE.TEST,
    ])
    assert MODULE.LEDGER not in paths


def test_replay_matrix_contract_is_exact() -> None:
    groups = MODULE.REPLAY_GROUPS
    assert [row["name"] for row in groups] == [
        "wp2-post-merge",
        "wp3",
        "wp3-post-merge",
        "wp5",
        "wp5-post-merge",
        "wp5-sync-helper",
    ]
    assert groups[0]["anchor"] == "c90041d3da5b680b574b910de50d8769d32fbfa9"
    assert groups[3]["anchor"] == "14e761e7a34889eebc3c4ef7df17fc56c9267af9"
    assert groups[4]["anchor"] == "dba0425c0f98950534bf5c6d407246da58eacd2f"
    assert all(row["command"][0] == "python" for row in groups)
