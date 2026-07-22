from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "checker"))

from v0_osap_fc1.cluster_b_wp2 import (  # noqa: E402
    EVALUATORS,
    RESIDUAL_TYPES,
    evaluate_fixture,
)

FIXTURES = ROOT / "fixtures/gate3/cluster_b/wp2"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_subset(observed, expected):
    if isinstance(expected, dict):
        assert isinstance(observed, dict)
        for key, value in expected.items():
            assert key in observed
            assert_subset(observed[key], value)
    else:
        assert observed == expected


def fixture_documents():
    return [load(path) for path in sorted(FIXTURES.glob("*.json"))]


def test_fixture_matrix_has_bounded_coverage():
    docs = fixture_documents()
    assert len(docs) == 28
    assert {doc["case_type"] for doc in docs} == set(EVALUATORS)


def test_all_fixture_expectations_replay_deterministically():
    for document in fixture_documents():
        first = evaluate_fixture(document)
        second = evaluate_fixture(document)
        assert first == second
        assert_subset(first, document["expected"])
        assert first["proof_claimed"] is False
        assert first["ipec_binding_claimed"] is False
        assert first["release_action_authorized"] is False


def test_all_seven_semantic_roles_are_covered():
    roles = {
        role
        for document in fixture_documents()
        for role in evaluate_fixture(document)["role_ids"]
    }
    assert roles == {f"CB-R{i}" for i in range(1, 8)}


def test_t157_t162_have_runtime_fixture_coverage():
    theorem_ids = {
        theorem_id
        for document in fixture_documents()
        for theorem_id in evaluate_fixture(document)["theorem_ids"]
    }
    assert {f"T{i}" for i in range(157, 163)} <= theorem_ids


def test_residual_vocabulary_is_exact_wp1_vocabulary():
    assert RESIDUAL_TYPES == (
        "TARGET_PRESENCE",
        "HISTORICAL",
        "MEMORY",
        "SIGNAL",
        "CAUSAL",
        "INFORMATION",
        "GENERIC_TRACE",
    )


def test_strong_dle_requires_all_three_contract_components():
    by_id = {doc["fixture_id"]: evaluate_fixture(doc) for doc in fixture_documents()}
    assert by_id["03_t157_strong_dle_pass"]["derived"]["strong_dle"] is True
    assert by_id["04_t157_reject_missing_history"]["status"] == "REJECT"
    assert by_id["05_t157_reject_current_live_conflict"]["status"] == "REJECT"
    assert by_id["06_t157_reject_missing_provenance"]["status"] == "REJECT"


def test_noninterfering_persistence_is_conditional_and_identity_preserving():
    by_id = {doc["fixture_id"]: evaluate_fixture(doc) for doc in fixture_documents()}
    assert by_id["07_t158_persistence_pass"]["derived"]["residual_persists"] is True
    assert by_id["08_t158_reject_identity_change"]["status"] == "REJECT"
    assert by_id["09_t158_reject_retype_interference"]["status"] == "REJECT"
    assert by_id["10_t158_deferred_missing_certificate"]["status"] == "DEFERRED"


def test_model_pair_requires_nonlabel_distinctness_and_shared_fragment_agreement():
    by_id = {doc["fixture_id"]: evaluate_fixture(doc) for doc in fixture_documents()}
    assert by_id["14_t160_model_pair_pass"]["derived"]["non_eliminable_from_shared_fragment"] is True
    assert by_id["15_t160_reject_label_only_distinctness"]["status"] == "REJECT"
    assert by_id["16_t160_reject_shared_fragment_mismatch"]["status"] == "REJECT"
    assert by_id["17_t160_deferred_no_residual_difference"]["status"] == "DEFERRED"


def test_historical_token_nonconversion_requires_separate_fresh_activation():
    by_id = {doc["fixture_id"]: evaluate_fixture(doc) for doc in fixture_documents()}
    assert by_id["20_t162_historical_nonconversion_pass"]["status"] == "PASS"
    assert by_id["21_t162_reject_archive_export"]["status"] == "REJECT"
    assert by_id["22_t162_fresh_activation_new_token_pass"]["status"] == "PASS"
    assert by_id["23_t162_reject_unwitnessed_new_token"]["status"] == "REJECT"


def test_build_artifacts_are_current():
    proc = subprocess.run(
        [sys.executable, "scripts/build_gate3_cluster_b_wp2.py", "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_package_only_verifier_passes():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_gate3_cluster_b_wp2.py", "--package-only"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr

def test_wp2_successor_repository_firewall_accepts_current_patch():
    proc = subprocess.run(
        [sys.executable, "scripts/verify_gate3_cluster_b_wp2.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_wp0_historical_test_file_is_byte_exact_at_wp2_start():
    revision = (
        "ffeaa3fd4fb2f85679f4695d5b28e333004ca24a:"
        "tests/test_gate3_cluster_b_wp0.py"
    )
    available = subprocess.run(
        ["git", "cat-file", "-e", revision],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0
    if not available:
        pytest.skip(
            "shallow checkout omits the exact WP2 baseline; the dedicated WP2 "
            "workflow performs full-history historical-byte replay"
        )

    expected = subprocess.run(
        ["git", "show", revision],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout
    assert (ROOT / "tests/test_gate3_cluster_b_wp0.py").read_bytes() == expected


def test_hosted_ci_compatibility_replays_frozen_wp0_wp1_baseline():
    workflow = (
        ROOT / ".github/workflows/gate3-cluster-b-wp2.yml"
    ).read_text(encoding="utf-8")

    assert "fetch-depth: 0" in workflow
    assert "git worktree add --detach" in workflow
    assert "ffeaa3fd4fb2f85679f4695d5b28e333004ca24a" in workflow

    inherited_verifiers = (
        "scripts/verify_gate3_cluster_b_wp0.py --package-only",
        "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py --package-only",
        "scripts/verify_gate3_cluster_b_wp1.py --package-only",
        "scripts/verify_gate3_cluster_b_wp1_post_merge_closeout.py --package-only",
    )

    for verifier in inherited_verifiers:
        assert verifier in workflow

# WP2_CURRENT_SUCCESSOR_LEGACY_LEDGER_TEST_DISPATCH_REPAIR_V0_1
def test_current_successor_dispatches_only_closed_predecessor_currentness_nodes():
    spec = importlib.util.spec_from_file_location(
        "wp2_successor_conftest",
        ROOT / "tests/conftest.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    expected = {
        "tests/test_gate3_cluster_b_wp0.py::test_wp0_full_git_firewall_accepts_current_patch",
        "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py::test_post_merge_sha256_ledger",
        "tests/test_gate3_cluster_b_wp1.py::test_wp1_schemas_and_records_validate",
        "tests/test_gate3_cluster_b_wp1.py::test_builder_outputs_are_current",
        "tests/test_gate3_cluster_b_wp1_post_merge_closeout.py::test_wp1_post_merge_records_and_ledger_validate",
        "tests/test_gate3_cluster_b_wp1_post_merge_closeout.py::test_builder_ledger_is_current",
    }

    assert module.LEGACY_PREDECESSOR_CURRENTNESS_NODEIDS == expected
    assert module.WP2_LOCK == (
        ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP2_BASELINE_LOCK.json"
    )


# WP2_FROZEN_PREDECESSOR_WORKFLOW_DISPATCH_ISOLATION_REPAIR_V0_1
def test_frozen_predecessor_workflows_are_manual_dispatch_only():
    workflow_paths = (
        ".github/workflows/gate3-cluster-b-wp0.yml",
        ".github/workflows/gate3-cluster-b-wp0-post-merge-closeout.yml",
        ".github/workflows/gate3-cluster-b-wp1.yml",
        ".github/workflows/gate3-cluster-b-wp1-post-merge-closeout.yml",
    )

    for relative in workflow_paths:
        text = (ROOT / relative).read_text(encoding="utf-8")
        event_surface = text.split("permissions:", 1)[0]
        assert "\n  workflow_dispatch:\n" in event_surface
        assert "\n  push:" not in event_surface
        assert "\n  pull_request:" not in event_surface
