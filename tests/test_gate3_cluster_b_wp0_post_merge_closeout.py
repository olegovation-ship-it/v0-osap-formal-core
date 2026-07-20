from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERGE = "46c02d96c047e70fe0d54feb60a0aadce2de95c7"
HEAD = "df4f8524b26e13eda34f96ff8ff48124a7cf9db0"
R = "release/v1.4.0/"


def load(name: str):
    return json.loads((ROOT / (R + name)).read_text(encoding="utf-8"))


def test_exact_merge_and_closeout_identity():
    x = load("GATE3_CLUSTER_B_WP0_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json")
    assert x["merged_pr"] == 20
    assert x["accepted_head_commit"] == HEAD
    assert x["merge_commit"] == MERGE
    assert x["wp0_acceptance_gates"] == {"pass":14,"total":14,"pending":0,"fail":0}
    assert x["hosted_ci_checks"]["pass"] == 27
    assert x["hosted_ci_checks"]["fail"] == 0


def test_hosted_ci_evidence_is_authenticated_and_complete():
    x = load("GATE3_CLUSTER_B_WP0_POST_MERGE_HOSTED_CI_EVIDENCE.json")
    assert x["evidence_state"] == "AUTHENTIC_GITHUB_API_EVIDENCE_RECORDED"
    assert x["workflow_run_count"] == len(x["workflow_runs"]) == 17
    assert all(item["conclusion"] == "success" for item in x["workflow_runs"])
    names = {item["workflow_name"] for item in x["workflow_runs"]}
    assert {"V0 OSAP Gate 3 Cluster B WP0","Python checker","Lean 4","Coq","Schema validation","Release readiness"} <= names


def test_wp0_job_evidence_is_exact():
    x = load("GATE3_CLUSTER_B_WP0_POST_MERGE_HOSTED_CI_EVIDENCE.json")
    jobs = {item["name"]: item for item in x["wp0_jobs"]}
    assert jobs["wp0-schema-and-records"]["job_id"] == 88416637786
    assert jobs["wp0-git-and-preservation-firewall"]["job_id"] == 88416637820


def test_branch_sync_is_fast_forward_only_and_non_destructive():
    x = load("GATE3_CLUSTER_B_WP0_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json")
    assert x["baseline_merge_commit"] == MERGE
    assert x["sync_mode"] == "FAST_FORWARD_ONLY"
    assert x["relation"] in {"SYNCHRONIZED_TO_CURRENT_MAIN","DEVELOPMENT_AHEAD_WITH_CLOSEOUT_PATCH","FAST_FORWARD_AVAILABLE"}
    assert x["history_rewrite_authorized"] is False
    assert x["force_push_authorized"] is False
    assert x["branch_deletion_authorized"] is False


def test_frozen_upstream_and_release_firewalls():
    p = load("GATE3_CLUSTER_B_WP0_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json")
    c = load("GATE3_CLUSTER_B_WP0_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json")
    assert p["conditional_theorem_ids_unchanged"] == ["T140","T150","T156"]
    assert p["canonical_new_theorem_ids_authorized"] == []
    assert p["release_actions_authorized"] is False
    assert not any(c["release_actions"].values())


def test_post_merge_gates_all_pass():
    x = load("GATE3_CLUSTER_B_WP0_POST_MERGE_CLOSEOUT_GATES.json")
    assert x["gate_count"] == len(x["gates"]) == 12
    assert all(gate["status"] == "PASS" for gate in x["gates"])


def test_schema_bundle_and_package_verifier():
    manifest = load("GATE3_CLUSTER_B_WP0_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json")
    assert manifest["schema_count"] == len(manifest["schemas"]) == 5
    assert all((ROOT / rel).is_file() for rel in manifest["schemas"])
    spec = importlib.util.spec_from_file_location("wp0_post_merge_verify", ROOT / "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.validate_records() == []


WP1_SUPERSEDED_WP0_PATHS = {
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
}


def _read_sha256_ledger(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split("  ", 1)
        entries[rel] = expected
    return entries


def test_post_merge_sha256_ledger():
    historical_path = (
        ROOT
        / R
        / "GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt"
    )
    successor_path = (
        ROOT
        / R
        / "GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
    )

    historical = _read_sha256_ledger(historical_path)
    successor = _read_sha256_ledger(successor_path)

    assert WP1_SUPERSEDED_WP0_PATHS <= historical.keys()
    assert WP1_SUPERSEDED_WP0_PATHS <= successor.keys()

    for rel, historical_expected in historical.items():
        path = ROOT / rel
        assert path.is_file(), rel

        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        accepted = (
            successor[rel]
            if rel in WP1_SUPERSEDED_WP0_PATHS
            else historical_expected
        )

        assert observed == accepted, rel
