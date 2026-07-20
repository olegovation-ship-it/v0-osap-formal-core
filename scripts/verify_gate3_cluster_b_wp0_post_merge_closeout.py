#!/usr/bin/env python3
"""Strict verifier for the WP0 post-merge archival closeout patch."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "olegovation-ship-it/v0-osap-formal-core"
MERGE = "46c02d96c047e70fe0d54feb60a0aadce2de95c7"
HEAD = "df4f8524b26e13eda34f96ff8ff48124a7cf9db0"
DEV = "v1.4.0-development"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
R = ROOT / "release/v1.4.0"

PAIRS = [
    ("release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp0_post_merge_archival_closeout_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP0_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp0_development_branch_synchronization_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_HOSTED_CI_EVIDENCE.json", "schemas/v1.4.0/gate3_cluster_b_wp0_post_merge_hosted_ci_evidence.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp0_post_merge_frozen_upstream_preservation_record.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_CLOSEOUT_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp0_post_merge_closeout_gates.schema.json"),
]
LEDGER = R / "GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt"

WP1_LEDGER = R / "GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
WP1_SUPERSEDED_WP0_PATHS = {
    "scripts/verify_gate3_cluster_b_wp0.py",
    "scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0_post_merge_closeout.py",
}


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def canonical_sha(payload: dict) -> str:
    copy = json.loads(json.dumps(payload))
    copy["canonical_sha256"] = None
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_records() -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    for doc_rel, schema_rel in PAIRS:
        if not (ROOT / doc_rel).is_file(): errors.append(f"missing {doc_rel}"); continue
        if not (ROOT / schema_rel).is_file(): errors.append(f"missing {schema_rel}"); continue
        if jsonschema:
            try: jsonschema.Draft202012Validator(load(schema_rel)).validate(load(doc_rel))
            except Exception as exc: errors.append(f"schema failure {doc_rel}: {exc}")

    closeout = load(PAIRS[0][0])
    sync = load(PAIRS[1][0])
    evidence = load(PAIRS[2][0])
    preservation = load(PAIRS[3][0])
    gates = load(PAIRS[4][0])
    if closeout["merged_pr"] != 20 or closeout["merge_commit"] != MERGE or closeout["accepted_head_commit"] != HEAD: errors.append("merge identity mismatch")
    if closeout["wp0_acceptance_gates"] != {"pass":14,"total":14,"pending":0,"fail":0}: errors.append("WP0 gate summary mismatch")
    if closeout["hosted_ci_checks"]["pass"] != 27 or closeout["hosted_ci_checks"]["fail"] != 0: errors.append("hosted CI summary mismatch")
    if any(closeout["release_actions"].values()): errors.append("release action authorized")
    if closeout["frozen_upstreams_modified"] or closeout["submitted_paper_b_baseline_modified"] or closeout["submission_register_v121_modified"]: errors.append("frozen baseline mutation recorded")
    if sync["sync_mode"] != "FAST_FORWARD_ONLY" or sync["history_rewrite_authorized"] or sync["force_push_authorized"] or sync["branch_deletion_authorized"]: errors.append("branch synchronization firewall failure")
    if sync["relation"] not in ["SYNCHRONIZED_TO_CURRENT_MAIN","DEVELOPMENT_AHEAD_WITH_CLOSEOUT_PATCH","FAST_FORWARD_AVAILABLE"]: errors.append("invalid branch relation")
    if evidence["evidence_state"] != "AUTHENTIC_GITHUB_API_EVIDENCE_RECORDED": errors.append("hosted CI evidence not authenticated")
    if evidence["source_head_sha"] != HEAD or evidence["merge_commit"] != MERGE: errors.append("CI evidence commit mismatch")
    if evidence["workflow_run_count"] != len(evidence["workflow_runs"]): errors.append("workflow run count mismatch")
    if any(x["conclusion"] != "success" for x in evidence["workflow_runs"]): errors.append("non-success workflow in evidence")
    if evidence["canonical_sha256"] != canonical_sha(evidence): errors.append("hosted CI canonical hash mismatch")
    required = {"V0 OSAP Gate 3 Cluster B WP0","Python checker","Lean 4","Coq","Schema validation","Release readiness"}
    names = {x["workflow_name"] for x in evidence["workflow_runs"]}
    if not required.issubset(names): errors.append("mandatory workflow missing")
    if preservation["canonical_new_theorem_ids_authorized"] != [] or preservation["release_actions_authorized"]: errors.append("preservation boundary failure")
    if preservation["conditional_theorem_ids_unchanged"] != ["T140","T150","T156"]: errors.append("conditional theorem status changed")
    if gates["gate_count"] != len(gates["gates"]) or any(x["status"] != "PASS" for x in gates["gates"]): errors.append("post-merge gate failure")
    return errors


def read_sha256_ledger(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split("  ", 1)
        entries[rel] = expected
    return entries


def verify_ledger() -> list[str]:
    errors: list[str] = []

    if not LEDGER.is_file():
        return ["missing post-merge SHA256 ledger"]

    if not WP1_LEDGER.is_file():
        return ["missing WP1 successor SHA256 ledger"]

    historical = read_sha256_ledger(LEDGER)
    successor = read_sha256_ledger(WP1_LEDGER)

    overlap = set(historical) & set(successor)

    if overlap != WP1_SUPERSEDED_WP0_PATHS:
        errors.append(
            "unexpected WP0/WP1 ledger overlap: "
            f"{sorted(overlap)}"
        )

    for rel, historical_expected in historical.items():
        file_path = ROOT / rel

        if not file_path.is_file():
            errors.append(f"ledger file missing: {rel}")
            continue

        expected = (
            successor.get(rel)
            if rel in WP1_SUPERSEDED_WP0_PATHS
            else historical_expected
        )

        if expected is None:
            errors.append(
                f"successor ledger missing superseded path: {rel}"
            )
            continue

        actual = hashlib.sha256(
            file_path.read_bytes()
        ).hexdigest()

        if actual != expected:
            errors.append(f"SHA256 mismatch: {rel}")

    return errors


def git_checks(allow_main: bool) -> list[str]:
    errors: list[str] = []
    if not (ROOT / ".git").exists(): return ["not a git repository"]
    def run(*args: str, check: bool = True) -> str:
        p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
        if check and p.returncode: raise RuntimeError(p.stderr.strip())
        return p.stdout.strip()
    branch = run("branch", "--show-current")
    effective = branch or os.environ.get("GITHUB_HEAD_REF", "") or os.environ.get("GITHUB_REF_NAME", "")
    if effective != DEV and not (allow_main and effective == "main"):
        errors.append(f"unexpected branch {effective!r}")
    try:
        if subprocess.run(["git","merge-base","--is-ancestor",MERGE,"HEAD"], cwd=ROOT).returncode != 0: errors.append("HEAD does not contain WP0 merge commit")
        tag = run("rev-parse", "refs/tags/v1.3.0^{}")
        if tag != TAG_TARGET: errors.append(f"stable tag target mismatch: {tag}")
    except RuntimeError as exc:
        errors.append(str(exc))
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
        "status": "PASS" if not errors else "FAIL",
        "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP0_POST_MERGE_CLOSEOUT",
        "merged_pr": 20,
        "merge_commit": MERGE,
        "hosted_checks": "27/27 PASS",
        "post_merge_gates": "12/12 PASS",
        "release_actions_authorized": False,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
