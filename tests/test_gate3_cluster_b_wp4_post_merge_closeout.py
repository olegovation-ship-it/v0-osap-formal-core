from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest

ROOT = Path(__file__).resolve().parents[1]
MERGE = "cdae3ea4e50f6222182f2398c350476fbe820f92"
ACCEPTED = "633c01e33271ffb17c045f69aa266a595ebc7e74"
CONTROLLED = ['release/v1.4.0/tools/patch_wp4_allowlist.py', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4.py']
SUCCESSOR_INPUTS = ['.github/workflows/gate3-cluster-b-wp4-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp4_allowlist.py', 'release/v1.4.0/tools/patch_wp4_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp4_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/build_gate3_cluster_b_wp4_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp4_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp4.sh', 'scripts/verify_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp4_post_merge_closeout.py']

PAIRS = [('release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_archival_closeout_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_development_branch_synchronization_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_hosted_ci_evidence.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_frozen_upstream_preservation_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_closeout_gates.schema.json')]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def parse_ledger(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            value, rel = line.split("  ", 1)
            out[rel] = value
    return out

def test_wp4_post_merge_records_validate() -> None:
    for document, schema in PAIRS:
        Draft202012Validator(load(schema)).validate(load(document))

def test_wp4_post_merge_identity_is_exact() -> None:
    record = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json")
    assert record["merged_pr"] == 27
    assert record["accepted_head_commit"] == ACCEPTED
    assert record["merge_commit"] == MERGE
    assert record["hosted_ci_checks"] == {"pass": 25, "fail": 0, "pending": 0, "skipped": 0, "total": 25}
    assert record["wp4_acceptance_gates"] == {"pass": 24, "fail": 0, "pending": 0, "total": 24}

def test_wp4_post_merge_authorization_firewall_is_closed() -> None:
    record = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json")
    assert record["canonical_wp4_records_modified"] is False
    assert record["canonical_wp4_ledger_modified"] is False
    assert record["closed_wp0_wp1_wp2_wp3_canonical_records_modified"] is False
    assert record["proof_or_new_runtime_semantics_added"] is False
    assert record["wp5_authorized"] is False
    assert not any(record["release_actions"].values())

def test_wp4_theorem_and_fixture_preservation() -> None:
    record = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json")
    assert record["theorem_ids_preserved"] == [f"T{i}" for i in range(157, 163)]
    assert record["fixture_count_preserved"] == 12
    assert record["statement_parity_percent_preserved"] == 100
    assert record["runtime_semantics_modified_by_closeout"] is False
    assert record["proof_implementation_authorized"] is False

def test_wp4_successor_ledger_is_exact() -> None:
    ledger = parse_ledger(ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt")
    assert set(ledger) == set(SUCCESSOR_INPUTS)
    for rel, expected in ledger.items():
        assert digest(ROOT / rel) == expected

def test_wp4_canonical_ledger_is_byte_preserved() -> None:
    available = subprocess.run(
        ["git", "cat-file", "-e", MERGE + "^{commit}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if available.returncode:
        pytest.skip("canonical merge object unavailable in shallow checkout")
    cp = subprocess.run(
        ["git", "show", f"{MERGE}:release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    assert (ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt").read_bytes() == cp.stdout

def test_wp4_closeout_gates_are_all_pass() -> None:
    gates = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json")
    assert gates["gate_count"] == 21
    assert len(gates["gates"]) == 21
    assert all(row["status"] == "PASS" for row in gates["gates"])

def test_wp4_synchronization_is_fast_forward_only() -> None:
    record = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json")
    assert record["sync_mode"] == "FAST_FORWARD_ONLY_AFTER_CLOSEOUT_MERGE"
    assert record["force_push_authorized"] is False
    assert record["history_rewrite_authorized"] is False
    assert record["branch_deletion_authorized"] is False
    assert record["main_ahead_by"] == 1
    assert record["development_ahead_by"] == 0
