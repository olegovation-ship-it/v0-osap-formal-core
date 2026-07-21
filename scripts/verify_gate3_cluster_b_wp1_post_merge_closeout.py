#!/usr/bin/env python3
"""Strict verifier for WP1 post-merge archival closeout."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "olegovation-ship-it/v0-osap-formal-core"
PRE_MERGE_MAIN = "f79bc16da3a4aa53c1e0cbbbbb65f003fea42e15"
MERGE = "eaf142089230ea5a5096ae834bf4e733d5f369aa"
HEAD = "8229685e4852f81d9bd2fc20ceec57bf1c7e91e5"
DEV = "v1.4.0-development"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
R = ROOT / "release/v1.4.0"
HISTORICAL_LEDGER = R / "GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
SUCCESSOR_LEDGER = R / "GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt"
SUPERSEDED = {
    "scripts/build_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp1.py",
}
EXPECTED_SUCCESSOR_PATHS = [
    ".github/workflows/gate3-cluster-b-wp1-post-merge-closeout.yml",
    "docs/gate3/cluster_b/WP1_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_CLOSEOUT_GATES.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_HOSTED_CI_EVIDENCE.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json",
    "release/v1.4.0/tools/patch_wp1_post_merge_allowlist.py",
    "schemas/v1.4.0/gate3_cluster_b_wp1_development_branch_synchronization_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_archival_closeout_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_closeout_gates.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_frozen_upstream_preservation_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_hosted_ci_evidence.schema.json",
    "scripts/build_gate3_cluster_b_wp1_post_merge_closeout.py",
    "scripts/capture_gate3_cluster_b_wp1_post_merge_evidence.py",
    "scripts/synchronize_v1_4_0_development_wp1.sh",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp1_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp1_post_merge_closeout.py",
    "scripts/build_gate3_cluster_b_wp1.py",
]
EXPECTED_CHANGED_PATHS = [
    ".github/workflows/gate3-cluster-b-wp1-post-merge-closeout.yml",
    "docs/gate3/cluster_b/WP1_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_CLOSEOUT_GATES.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_HOSTED_CI_EVIDENCE.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt",
    "release/v1.4.0/tools/patch_wp1_post_merge_allowlist.py",
    "schemas/v1.4.0/gate3_cluster_b_wp1_development_branch_synchronization_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_archival_closeout_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_closeout_gates.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_frozen_upstream_preservation_record.schema.json",
    "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_hosted_ci_evidence.schema.json",
    "scripts/build_gate3_cluster_b_wp1_post_merge_closeout.py",
    "scripts/capture_gate3_cluster_b_wp1_post_merge_evidence.py",
    "scripts/synchronize_v1_4_0_development_wp1.sh",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp1_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp1_post_merge_closeout.py",
    "scripts/build_gate3_cluster_b_wp1.py",
]
IMMUTABLE_WP1_RECORDS = {
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_ACCEPTANCE_GATES.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_BASELINE_LOCK.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_CANONICAL_CONTRACTS.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_CANONICAL_GLOSSARY.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_SCHEMA_BUNDLE_MANIFEST.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_ID_COLLISION_AUDIT.json",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json",
}
PAIRS = [
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_archival_closeout_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp1_development_branch_synchronization_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_HOSTED_CI_EVIDENCE.json", "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_hosted_ci_evidence.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_frozen_upstream_preservation_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_CLOSEOUT_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp1_post_merge_closeout_gates.schema.json"),
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
        if not (ROOT / doc_rel).is_file(): errors.append(f"missing {doc_rel}"); continue
        if not (ROOT / schema_rel).is_file(): errors.append(f"missing {schema_rel}"); continue
        try: jsonschema.Draft202012Validator(load(schema_rel)).validate(load(doc_rel))
        except Exception as exc: errors.append(f"schema failure {doc_rel}: {exc}")

    closeout, sync, evidence, preservation, gates = [load(x[0]) for x in PAIRS]
    if closeout["merged_pr"] != 22 or closeout["merge_commit"] != MERGE or closeout["accepted_head_commit"] != HEAD: errors.append("merge identity mismatch")
    if closeout["pre_merge_main"] != PRE_MERGE_MAIN: errors.append("pre-merge baseline mismatch")
    if closeout["wp1_acceptance_gates"] != {"pass":16,"total":16,"pending":0,"fail":0}: errors.append("WP1 acceptance summary mismatch")
    if closeout["hosted_ci_checks"]["pass"] != 19 or closeout["hosted_ci_checks"]["fail"] != 0: errors.append("hosted CI summary mismatch")
    if closeout["detached_post_merge_replay"] != {"status":"PASS","pytest_passed":86,"failed":0,"rc":0}: errors.append("detached replay summary mismatch")
    if any(closeout["release_actions"].values()) or closeout["closed_wp0_records_modified"] or closeout["canonical_wp1_records_modified"]: errors.append("closeout immutability firewall failure")
    if closeout["proof_or_runtime_semantics_added"]: errors.append("proof/runtime semantics overclaim")

    if sync["sync_mode"] != "FAST_FORWARD_ONLY" or sync["canonical_wp1_merge_baseline"] != MERGE: errors.append("synchronization identity mismatch")
    if sync["history_rewrite_authorized"] or sync["force_push_authorized"] or sync["branch_deletion_authorized"]: errors.append("branch synchronization firewall failure")
    if sync["ahead_by"] != 0 or sync["behind_by"] != 0 or sync["compare_status"] != "identical": errors.append("baseline branch equality not recorded")

    if evidence["evidence_state"] != "AUTHENTIC_GITHUB_API_AND_DETACHED_REPLAY_EVIDENCE_RECORDED": errors.append("evidence state mismatch")
    if evidence["source_head_sha"] != HEAD or evidence["merge_commit"] != MERGE: errors.append("CI evidence commit mismatch")
    if evidence["workflow_run_count"] != len(evidence["workflow_runs"]) or evidence["workflow_run_count"] != 19: errors.append("workflow run count mismatch")
    if any(x["conclusion"] != "success" for x in evidence["workflow_runs"]): errors.append("non-success workflow in evidence")
    if evidence["canonical_sha256"] != canonical_sha(evidence): errors.append("hosted evidence canonical hash mismatch")
    required = {"V0 OSAP Gate 3 Cluster B WP1","V0 OSAP Gate 3 Cluster B WP0 Post-Merge Closeout","Python checker","Lean 4","Coq","Schema validation","Release readiness"}
    if not required.issubset({x["workflow_name"] for x in evidence["workflow_runs"]}): errors.append("mandatory workflow missing")
    if evidence["detached_post_merge_replay"]["full_pytest"].get("passed") != 86 or evidence["detached_post_merge_replay"].get("result") != "PASS": errors.append("detached replay evidence mismatch")

    if preservation["canonical_wp1_merge_baseline"] != MERGE or preservation["closed_wp0_records_modified"] or preservation["canonical_wp1_records_modified"]: errors.append("preservation record mismatch")
    if preservation["wp1_theorem_ids_canonicalized_by_merge"] != ["T157","T158","T159","T160","T161","T162"]: errors.append("WP1 theorem-ID preservation mismatch")
    if preservation["wp1_conditional_theorem_ids_unchanged"] != ["T158","T160"]: errors.append("WP1 conditional set changed")
    if preservation["proof_implementation_authorized"] or preservation["runtime_semantics_authorized"] or preservation["release_actions_authorized"]: errors.append("preservation authorization failure")

    if gates["gate_count"] != 14 or gates["gate_count"] != len(gates["gates"]) or any(x["status"] != "PASS" for x in gates["gates"]): errors.append("post-merge gate failure")
    manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json")
    if manifest.get("schema_count") != 5 or len(manifest.get("schemas", [])) != 5: errors.append("schema bundle count mismatch")
    return errors


def read_ledger(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"): continue
        expected, rel = line.split("  ", 1)
        entries[rel] = expected
    return entries


def verify_ledger() -> list[str]:
    if not HISTORICAL_LEDGER.is_file(): return ["missing historical WP1 ledger"]
    if not SUCCESSOR_LEDGER.is_file(): return ["missing WP1 post-merge ledger"]
    historical = read_ledger(HISTORICAL_LEDGER)
    successor = read_ledger(SUCCESSOR_LEDGER)
    errors: list[str] = []
    if set(successor) != set(EXPECTED_SUCCESSOR_PATHS): errors.append("successor ledger path set mismatch")
    overlap = set(historical) & set(successor)
    if overlap != SUPERSEDED: errors.append(f"unexpected WP1/post-merge ledger overlap: {sorted(overlap)}")
    for rel, old_hash in historical.items():
        path = ROOT / rel
        if not path.is_file(): errors.append(f"historical ledger file missing: {rel}"); continue
        expected = successor.get(rel) if rel in SUPERSEDED else old_hash
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected: errors.append(f"historical/successor SHA256 mismatch: {rel}")
    for rel, expected in successor.items():
        path = ROOT / rel
        if not path.is_file(): errors.append(f"successor ledger file missing: {rel}"); continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected: errors.append(f"successor SHA256 mismatch: {rel}")
    return errors


def run_git(*args: str, check: bool = True) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if check and p.returncode: raise RuntimeError(p.stderr.strip())
    return p.stdout.strip()


def git_checks(allow_main: bool) -> list[str]:
    errors: list[str] = []
    if not (ROOT / ".git").exists(): return ["not a git repository"]
    branch = run_git("branch", "--show-current", check=False)
    effective = branch or os.environ.get("GITHUB_HEAD_REF", "") or os.environ.get("GITHUB_REF_NAME", "")
    if effective != DEV and not (allow_main and effective == "main"): errors.append(f"unexpected branch {effective!r}")
    if subprocess.run(["git","merge-base","--is-ancestor",MERGE,"HEAD"],cwd=ROOT).returncode != 0: errors.append("HEAD does not contain canonical WP1 merge baseline")
    if run_git("rev-parse","refs/tags/v1.3.0^{}") != TAG_TARGET: errors.append("stable v1.3.0 tag target changed")
    changed = set(run_git("-c","core.quotePath=false","diff","--name-only","--no-renames",MERGE,"--",check=False).splitlines())
    changed.update(run_git("-c","core.quotePath=false","ls-files","--others","--exclude-standard",check=False).splitlines())
    changed.discard("")
    if changed != set(EXPECTED_CHANGED_PATHS):
        errors.append(f"closeout path set mismatch: missing={sorted(set(EXPECTED_CHANGED_PATHS)-changed)}, extra={sorted(changed-set(EXPECTED_CHANGED_PATHS))}")
    if any(x.startswith("release/v1.4.0/GATE3_CLUSTER_B_WP0_") for x in changed): errors.append("closed WP0 release record changed")
    if changed & IMMUTABLE_WP1_RECORDS: errors.append(f"canonical WP1 record changed: {sorted(changed & IMMUTABLE_WP1_RECORDS)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--allow-main", action="store_true")
    args = parser.parse_args()
    errors = validate_records() + verify_ledger()
    if not args.package_only: errors += git_checks(args.allow_main)
    result = {
        "artifact":"V0_OSAP_GATE3_CLUSTER_B_WP1_POST_MERGE_CLOSEOUT",
        "status":"PASS" if not errors else "FAIL",
        "merged_pr":22,
        "merge_commit":MERGE,
        "hosted_checks":"19/19 PASS",
        "detached_replay":"86/86 PASS",
        "post_merge_gates":"14/14 PASS",
        "release_actions_authorized":False,
        "errors":errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
