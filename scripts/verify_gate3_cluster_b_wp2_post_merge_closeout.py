#!/usr/bin/env python3
"""Strict verifier for WP2 post-merge archival closeout."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "olegovation-ship-it/v0-osap-formal-core"
PRE_MERGE_MAIN = "eaf142089230ea5a5096ae834bf4e733d5f369aa"
MERGE = "b6370af53add3fdff1ddb48824dd76ebba3aaa32"
HEAD = "b0f5fc5b0d5103e1bb22b06ca51716d40e22a5d7"
DEV = "v1.4.0-development"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
R = ROOT / "release/v1.4.0"
HISTORICAL_LEDGER = R / "GATE3_CLUSTER_B_WP2_SHA256SUMS.txt"
SUCCESSOR_LEDGER = R / "GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt"
SUPERSEDED = {
    "scripts/build_gate3_cluster_b_wp2.py",
    "scripts/verify_gate3_cluster_b_wp2.py",
}
EXPECTED_SUCCESSOR_PATHS = ['.github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp2_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp2_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp2.py', 'scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp2_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp2.sh', 'scripts/verify_gate3_cluster_b_wp2.py', 'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp2_post_merge_closeout.py']
EXPECTED_CHANGED_PATHS = ['.github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp2_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp2_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp2.py', 'scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp2_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp2.sh', 'scripts/verify_gate3_cluster_b_wp2.py', 'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp2_post_merge_closeout.py', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt']
IMMUTABLE_WP2_RECORDS = {
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_ACCEPTANCE_GATES.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_BASELINE_LOCK.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_SCHEMA_BUNDLE_MANIFEST.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_SHA256SUMS.txt",
}
PAIRS = [
    ("release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_archival_closeout_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP2_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp2_development_branch_synchronization_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_HOSTED_CI_EVIDENCE.json", "schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_hosted_ci_evidence.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_frozen_upstream_preservation_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_CLOSEOUT_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp2_post_merge_closeout_gates.schema.json"),
]

def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def canonical_sha(payload: dict) -> str:
    cp = json.loads(json.dumps(payload))
    cp["canonical_sha256"] = None
    return hashlib.sha256(json.dumps(cp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def validate_records() -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema dependency unavailable"]
    for doc_rel, schema_rel in PAIRS:
        if not (ROOT / doc_rel).is_file():
            errors.append(f"missing {doc_rel}"); continue
        if not (ROOT / schema_rel).is_file():
            errors.append(f"missing {schema_rel}"); continue
        try:
            jsonschema.Draft202012Validator(load(schema_rel)).validate(load(doc_rel))
        except Exception as exc:
            errors.append(f"schema failure {doc_rel}: {exc}")

    closeout, sync, evidence, preservation, gates = [load(x[0]) for x in PAIRS]
    if closeout["merged_pr"] != 23 or closeout["merge_commit"] != MERGE or closeout["accepted_head_commit"] != HEAD:
        errors.append("merge identity mismatch")
    if closeout["pre_merge_main"] != PRE_MERGE_MAIN:
        errors.append("pre-merge baseline mismatch")
    if closeout["wp2_acceptance_gates"] != {"pass":20,"total":20,"pending":0,"fail":0}:
        errors.append("WP2 acceptance summary mismatch")
    if closeout["hosted_ci_checks"]["pass"] != 25 or closeout["hosted_ci_checks"]["fail"] != 0:
        errors.append("hosted CI summary mismatch")
    replay = closeout["detached_post_merge_replay"]
    if replay.get("pytest_passed") != 106 or replay.get("pytest_skipped") != 6 or replay.get("failed") != 0:
        errors.append("detached replay summary mismatch")
    if any(closeout["release_actions"].values()) or closeout["closed_wp0_wp1_records_modified"] or closeout["canonical_wp2_records_modified"]:
        errors.append("closeout immutability firewall failure")
    if closeout["proof_or_new_runtime_semantics_added"]:
        errors.append("closeout semantic overclaim")

    if sync["sync_mode"] != "FAST_FORWARD_ONLY" or sync["canonical_wp2_merge_baseline"] != MERGE:
        errors.append("synchronization identity mismatch")
    if sync["history_rewrite_authorized"] or sync["force_push_authorized"] or sync["branch_deletion_authorized"]:
        errors.append("branch synchronization firewall failure")
    if sync["ahead_by"] != 0 or sync["behind_by"] != 0 or sync["compare_status"] != "identical":
        errors.append("baseline branch equality not recorded")

    if evidence["evidence_state"] != "AUTHENTIC_GITHUB_API_AND_CODESPACES_REPLAY_EVIDENCE_RECORDED":
        errors.append("evidence state mismatch")
    if evidence["source_head_sha"] != HEAD or evidence["merge_commit"] != MERGE or evidence["source_pr"] != 23:
        errors.append("CI evidence identity mismatch")
    if evidence["workflow_run_count"] != len(evidence["workflow_runs"]) or evidence["workflow_run_count"] != 17:
        errors.append("workflow run count mismatch")
    if any(x["conclusion"] != "success" for x in evidence["workflow_runs"]):
        errors.append("non-success workflow in evidence")
    if evidence["check_summary"] != {"failure":0,"pending":0,"skipped":0,"success":25,"total":25}:
        errors.append("check summary mismatch")
    if evidence["canonical_sha256"] != canonical_sha(evidence):
        errors.append("hosted evidence canonical hash mismatch")
    mandatory = {"V0 OSAP Gate 3 Cluster B WP2","Python checker","Lean 4","Coq","Schema validation","Release readiness"}
    if not mandatory.issubset({x["workflow_name"] for x in evidence["workflow_runs"]}):
        errors.append("mandatory workflow missing")

    if preservation["canonical_wp2_merge_baseline"] != MERGE:
        errors.append("preservation merge baseline mismatch")
    if preservation["fixture_count_preserved"] != 28:
        errors.append("fixture count changed")
    if preservation["theorem_ids_preserved"] != [f"T{i}" for i in range(157, 163)]:
        errors.append("theorem set changed")
    if preservation["semantic_role_ids_preserved"] != [f"CB-R{i}" for i in range(1, 8)]:
        errors.append("semantic role set changed")
    if preservation["release_actions_authorized"] or preservation["proof_implementation_authorized"] or preservation["runtime_semantics_modified_by_closeout"]:
        errors.append("preservation authorization failure")

    if gates["gate_count"] != 18 or gates["gate_count"] != len(gates["gates"]) or any(x["status"] != "PASS" for x in gates["gates"]):
        errors.append("post-merge gate failure")
    manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json")
    if manifest.get("schema_count") != 5 or len(manifest.get("schemas", [])) != 5:
        errors.append("schema bundle count mismatch")
    return errors

def read_ledger(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        expected, rel = line.split("  ", 1)
        entries[rel] = expected
    return entries

def verify_ledger() -> list[str]:
    if not HISTORICAL_LEDGER.is_file():
        return ["missing historical WP2 ledger"]
    if not SUCCESSOR_LEDGER.is_file():
        return ["missing WP2 post-merge ledger"]
    historical = read_ledger(HISTORICAL_LEDGER)
    successor = read_ledger(SUCCESSOR_LEDGER)
    errors: list[str] = []
    if set(successor) != set(EXPECTED_SUCCESSOR_PATHS):
        errors.append("successor ledger path set mismatch")
    overlap = set(historical) & set(successor)
    if overlap != SUPERSEDED:
        errors.append(f"unexpected WP2/post-merge ledger overlap: {sorted(overlap)}")
    for rel, old_hash in historical.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"historical ledger file missing: {rel}"); continue
        expected = successor.get(rel) if rel in SUPERSEDED else old_hash
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"historical/successor SHA256 mismatch: {rel}")
    for rel, expected in successor.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"successor ledger file missing: {rel}"); continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"successor SHA256 mismatch: {rel}")
    return errors

def run_git(*args: str, check: bool = True) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if check and p.returncode:
        raise RuntimeError(p.stderr.strip())
    return p.stdout.strip()

def git_checks(allow_main: bool) -> list[str]:
    errors: list[str] = []
    if not (ROOT / ".git").exists():
        return ["not a git repository"]
    branch = run_git("branch", "--show-current", check=False)
    effective = branch or os.environ.get("GITHUB_HEAD_REF", "") or os.environ.get("GITHUB_REF_NAME", "")
    if effective != DEV and not (allow_main and effective == "main"):
        errors.append(f"unexpected branch {effective!r}")
    if subprocess.run(["git","merge-base","--is-ancestor",MERGE,"HEAD"],cwd=ROOT).returncode != 0:
        errors.append("HEAD does not contain canonical WP2 merge baseline")
    if run_git("rev-parse","refs/tags/v1.3.0^{}") != TAG_TARGET:
        errors.append("stable v1.3.0 tag target changed")
    changed = set(run_git("-c","core.quotePath=false","diff","--name-only","--no-renames",MERGE,"--",check=False).splitlines())
    changed.update(run_git("-c","core.quotePath=false","ls-files","--others","--exclude-standard",check=False).splitlines())
    changed.discard("")
    expected = set(EXPECTED_CHANGED_PATHS)
    wp3_successor_paths = {
        '.github/workflows/gate3-cluster-b-wp3.yml',
        'checker/v0_osap_fc1/cluster_b_wp3.py',
        'docs/gate3/cluster_b/WP3_BUILD_SPECIFICATION.md',
        'docs/gate3/cluster_b/WP3_VALIDATOR_IPEC_EXTENSION_AND_TYPED_OUTCOME_BINDING.md',
        'fixtures/gate3/cluster_b/wp3/01_dle_transition_pass.json',
        'fixtures/gate3/cluster_b/wp3/02_dle_transition_reject.json',
        'fixtures/gate3/cluster_b/wp3/03_strong_dle_pass.json',
        'fixtures/gate3/cluster_b/wp3/04_strong_dle_reject.json',
        'fixtures/gate3/cluster_b/wp3/05_residual_persistence_deferred.json',
        'fixtures/gate3/cluster_b/wp3/06_residual_type_separation_pass.json',
        'fixtures/gate3/cluster_b/wp3/07_model_pair_pass.json',
        'fixtures/gate3/cluster_b/wp3/08_model_pair_reject.json',
        'fixtures/gate3/cluster_b/wp3/09_minimal_obstruction_pass.json',
        'fixtures/gate3/cluster_b/wp3/10_historical_nonconversion_reject.json',
        'fixtures/gate3/cluster_b/wp3/11_robust_obstruction_pass.json',
        'fixtures/gate3/cluster_b/wp3/12_branch_firewall_reject.json',
        'fixtures/gate3/cluster_b/wp3/13_robust_obstruction_reject.json',
        'fixtures/gate3/cluster_b/wp3/14_residual_persistence_reject.json',
        'fixtures/gate3/cluster_b/wp3/15_residual_type_separation_reject.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_ACCEPTANCE_GATES.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_BASELINE_LOCK.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_EXTENSION_RULE_REGISTRY_T157_T162.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_FIXTURE_MANIFEST.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_IPEC_V0_1_COMPATIBILITY_PROFILE.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_PRESERVATION_FIREWALL.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_SCHEMA_BUNDLE_MANIFEST.json',
        'release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt',
        'schemas/v1.4.0/gate3_cluster_b_wp3_acceptance_gates.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_adapter_binding_manifest.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_baseline_lock.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_binding_result.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_extension_rule_registry.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_fixture.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_fixture_manifest.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_ipec_compatibility_profile.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_preservation_firewall.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_schema_bundle_manifest.schema.json',
        'schemas/v1.4.0/gate3_cluster_b_wp3_source_result.schema.json',
        'scripts/build_gate3_cluster_b_wp3.py',
        'scripts/verify_gate3_cluster_b_wp2.py',
        'scripts/verify_gate3_cluster_b_wp3.py',
        'tests/test_gate3_cluster_b_wp3.py',
    }
    successor_expected = expected | wp3_successor_paths
    if changed != expected and changed != successor_expected:
        comparison = successor_expected if changed & wp3_successor_paths else expected
        errors.append(
            "closeout path set mismatch: "
            f"missing={sorted(comparison - changed)}, "
            f"extra={sorted(changed - comparison)}"
        )
    if any(x.startswith("release/v1.4.0/GATE3_CLUSTER_B_WP0_") or x.startswith("release/v1.4.0/GATE3_CLUSTER_B_WP1_") for x in changed):
        errors.append("closed WP0/WP1 release record changed")
    if changed & IMMUTABLE_WP2_RECORDS:
        errors.append(f"canonical WP2 record changed: {sorted(changed & IMMUTABLE_WP2_RECORDS)}")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--allow-main", action="store_true")
    args = parser.parse_args()
    errors = validate_records() + verify_ledger()
    if not args.package_only:
        errors += git_checks(args.allow_main)
    result = {
        "artifact":"V0_OSAP_GATE3_CLUSTER_B_WP2_POST_MERGE_CLOSEOUT",
        "status":"PASS" if not errors else "FAIL",
        "merged_pr":23,"merge_commit":MERGE,"hosted_checks":"25/25 PASS",
        "detached_replay":"106 passed / 6 skipped / 0 failed","post_merge_gates":"18/18 PASS",
        "release_actions_authorized":False,"errors":errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
