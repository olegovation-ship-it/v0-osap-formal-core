from __future__ import annotations

import importlib.util
import json

import pytest
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "release/v1.4.0/tools/verify_wp6_hosted_ci_predecessor_consumer_closure_repair.py"
MANIFEST = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR_MANIFEST.json"
RECORD = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_PREDECESSOR_CONSUMER_CLOSURE_REPAIR_RECORD.json"
WP3 = ROOT / "scripts/verify_gate3_cluster_b_wp3.py"


def load_module():
    spec = importlib.util.spec_from_file_location("v09", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_v09_package_only_verifier() -> None:
    cp = subprocess.run(
        [sys.executable, str(VERIFIER), "--mode", "package-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode == 0, cp.stdout + cp.stderr
    result = json.loads(cp.stdout)
    assert result["status"] == "PASS"
    assert result["changed_path_count"] == 13
    assert result["controlled_modified_path_count"] == 7
    assert result["additive_path_count"] == 6
    assert result["historical_consumer_count"] == 6


def test_v09_manifest_preservation_boundary() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = manifest["controlled_modified_paths"] + manifest["additive_paths"]
    assert manifest["version"] == "0.9"
    assert len(paths) == len(set(paths)) == 13
    assert manifest["minimal_new_controlled_path"] == "scripts/verify_gate3_cluster_b_wp3.py"
    assert manifest["blanket_successor_allowlist_expansion"] is False
    assert not any("/schemas/" in "/" + path for path in paths)
    assert not any("/fixtures/" in "/" + path for path in paths)
    assert not any(path.startswith("lean/") or path.startswith("coq/") for path in paths)
    assert manifest["frozen_ledgers_rewritten"] is False
    assert manifest["historical_records_rewritten"] is False
    assert manifest["release_actions_performed"] is False
    assert manifest["unrelated_untracked_artifacts_allowed"] is True
    assert manifest["unrelated_tracked_changes_allowed"] is False
    assert manifest["working_tree_surface_policy"] == (
        "EXACT_13_PACKAGE_STATUSES_PLUS_UNRELATED_UNTRACKED_ARTIFACTS"
    )


def test_v09_historical_consumer_map_is_bounded() -> None:
    module = load_module()
    assert set(module.CONSUMERS) == {
        "wp2-verifier",
        "wp3-canonical-verifier",
        "wp3-post-merge-allowlist",
        "wp5-canonical-allowlist",
        "wp5-post-merge-allowlist",
        "wp5-sync-helper-allowlist",
    }
    assert module.CONSUMERS["wp3-canonical-verifier"] == (
        "c90041d3da5b680b574b910de50d8769d32fbfa9",
        "scripts/verify_gate3_cluster_b_wp3.py",
    )


def test_v09_failure_matrix_is_one_to_one_and_runs_wp3_canonical() -> None:
    module = load_module()
    matrix = module.FAILED_WORKFLOW_MATRIX
    assert len(matrix) == 7
    assert [entry["ordinal"] for entry in matrix] == list(range(1, 8))
    assert len({entry["workflow"] for entry in matrix}) == 7
    assert len({entry["run_id"] for entry in matrix}) == 7
    wp3 = next(entry for entry in matrix if entry["workflow"] == "V0 OSAP Gate 3 Cluster B WP3")
    assert wp3["command"] == ["python", "scripts/verify_gate3_cluster_b_wp3.py"]
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert record["failed_workflow_matrix"] == matrix
    expected_failed_runs = [
        {
            "failure_class": entry["failure_class"],
            "run_id": entry["run_id"],
            "workflow": entry["workflow"],
        }
        for entry in matrix
    ]
    assert record["failed_runs"] == expected_failed_runs


def test_v09_wp3_consumer_separates_frozen_replay_from_successor_overlay() -> None:
    source = WP3.read_text(encoding="utf-8")
    assert "wp3-canonical-verifier" in source
    assert "replay_frozen_wp3_consumer" in source
    assert "FAIL_PRESERVATION_FIREWALL frozen WP3 predecessor replay failed" in source
    assert "BASELINE='7b49aa76fef65bced7141a639e8ef6fe3b5ba313'" in source
    assert "def allowed(p): return p in AUTHORIZED_MODIFIED or p in EXACT or p in POST_MERGE_EXACT or any(p.startswith(x) for x in PREFIX)" in source
    assert "def verify_boundary() -> bool:" in source
    assert "if verify_boundary():" in source
    assert "Do not re-enter the current canonical builder" in source
    assert "frozen predecessor replay + separately attested successor overlay" in source


def test_v09_wp3_wrapper_short_circuits_after_delegated_replay(monkeypatch, capsys) -> None:
    spec = importlib.util.spec_from_file_location("v09_wp3", WP3)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monkeypatch.setattr(module, "verify_boundary", lambda: True)

    def forbidden() -> None:
        raise AssertionError("current canonical body re-entered after delegated replay")

    monkeypatch.setattr(module, "verify_wp2_successor_handoff", forbidden)
    monkeypatch.setattr(module, "verify_records", forbidden)
    monkeypatch.setattr(module, "verify_fixtures", forbidden)

    assert module.main() == 0
    assert "frozen predecessor replay + separately attested successor overlay" in capsys.readouterr().out


def test_v09_diagnostic_identity_is_exact() -> None:
    source = VERIFIER.read_text(encoding="utf-8")
    assert "committed v0.9 working tree has tracked/staged/structural changes" in source
    assert source.count('"error": "v0.9 successor attestation failed"') == 2
    assert "committed v0.4 working tree is not clean" not in source
    assert '"error": "v0.4 successor attestation failed"' not in source
    assert '"error": "v0.5 successor attestation failed"' not in source


def test_v09_unrelated_untracked_artifacts_are_allowed() -> None:
    module = load_module()
    actual = module.expected_codes("working-tree")
    actual = {
        **actual,
        "V0_OSAP_package.zip": "??",
        "V0_OSAP_package.zip.sha256.txt": "??",
        "read_only_failure_analysis.txt": "??",
    }
    allowed = module.verify_working_tree_surface_entries(actual)
    assert allowed == [
        "V0_OSAP_package.zip",
        "V0_OSAP_package.zip.sha256.txt",
        "read_only_failure_analysis.txt",
    ]


def test_v09_unrelated_tracked_change_is_rejected() -> None:
    module = load_module()
    actual = {**module.expected_codes("working-tree"), "README.md": " M"}
    with pytest.raises(RuntimeError, match="unrelated tracked/staged/structural"):
        module.verify_working_tree_surface_entries(actual)


def test_v09_missing_or_wrong_package_path_is_rejected() -> None:
    module = load_module()
    expected = module.expected_codes("working-tree")

    missing = dict(expected)
    missing.pop(module.CONTROLLED[0])
    with pytest.raises(RuntimeError, match="prepared v0.9 package surface mismatch"):
        module.verify_working_tree_surface_entries(missing)

    wrong = dict(expected)
    wrong[module.ADDITIVE[0]] = "A "
    with pytest.raises(RuntimeError, match="prepared v0.9 package surface mismatch"):
        module.verify_working_tree_surface_entries(wrong)
