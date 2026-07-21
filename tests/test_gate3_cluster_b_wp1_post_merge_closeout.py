from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def module(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_wp1_post_merge_records_and_ledger_validate():
    verify = module("wp1_pm_verify", "scripts/verify_gate3_cluster_b_wp1_post_merge_closeout.py")
    assert verify.validate_records() == []
    assert verify.verify_ledger() == []


def test_merge_identity_and_replay_summary_are_exact():
    record = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json")
    assert record["merged_pr"] == 22
    assert record["accepted_head_commit"] == "8229685e4852f81d9bd2fc20ceec57bf1c7e91e5"
    assert record["merge_commit"] == "eaf142089230ea5a5096ae834bf4e733d5f369aa"
    assert record["detached_post_merge_replay"] == {"status":"PASS","pytest_passed":86,"failed":0,"rc":0}


def test_release_and_preservation_firewalls():
    record = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json")
    preservation = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json")
    assert not any(record["release_actions"].values())
    assert record["closed_wp0_records_modified"] is False
    assert record["canonical_wp1_records_modified"] is False
    assert preservation["release_actions_authorized"] is False
    assert preservation["proof_implementation_authorized"] is False
    assert preservation["runtime_semantics_authorized"] is False


def test_closeout_gates_are_fourteen_of_fourteen():
    gates = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_CLOSEOUT_GATES.json")
    assert gates["gate_count"] == len(gates["gates"]) == 14
    assert all(g["status"] == "PASS" for g in gates["gates"])


def test_allowlist_patch_is_idempotent_and_complete():
    patch = module("wp1_pm_patch", "release/v1.4.0/tools/patch_wp1_post_merge_allowlist.py")
    for path, transform in patch.SURFACES:
        text = path.read_text(encoding="utf-8")
        assert transform(text) == text
    wp0_text = (ROOT / "scripts/verify_gate3_cluster_b_wp0.py").read_text(encoding="utf-8")
    wp1_text = (ROOT / "scripts/verify_gate3_cluster_b_wp1.py").read_text(encoding="utf-8")
    assert all(f'    "{p}",' in wp0_text for p in patch.NEW_ALLOWED)
    assert all(f'    "{p}",' in wp1_text for p in patch.NEW_ALLOWED)
    assert set(patch.SUPERSEDED) == {
        "scripts/build_gate3_cluster_b_wp1.py",
        "scripts/verify_gate3_cluster_b_wp0.py",
        "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
        "scripts/verify_gate3_cluster_b_wp1.py",
        "tests/test_gate3_cluster_b_wp0.py",
        "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
        "tests/test_gate3_cluster_b_wp1.py",
    }


def test_wp1_historical_ledger_overlap_is_exact():
    verify = module("wp1_pm_verify_overlap", "scripts/verify_gate3_cluster_b_wp1_post_merge_closeout.py")
    historical = verify.read_ledger(verify.HISTORICAL_LEDGER)
    successor = verify.read_ledger(verify.SUCCESSOR_LEDGER)
    assert set(historical) & set(successor) == verify.SUPERSEDED
    for rel in verify.SUPERSEDED:
        observed = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        assert observed == successor[rel]
        assert observed != historical[rel]


def test_builder_ledger_is_current():
    build = module("wp1_pm_builder", "scripts/build_gate3_cluster_b_wp1_post_merge_closeout.py")
    ledger = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"
    assert ledger.read_text(encoding="utf-8") == build.expected_ledger()


def test_sync_script_is_fast_forward_only_and_release_free():
    text = (ROOT / "scripts/synchronize_v1_4_0_development_wp1.sh").read_text(encoding="utf-8")
    assert "merge --ff-only" in text
    assert "push --force" not in text
    assert "git tag" not in text
    assert "gh release" not in text
    assert "zenodo" not in text.lower()
