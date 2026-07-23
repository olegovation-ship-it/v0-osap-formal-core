#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "c90041d3da5b680b574b910de50d8769d32fbfa9"
ACCEPTED = "633c01e33271ffb17c045f69aa266a595ebc7e74"
MERGE = "cdae3ea4e50f6222182f2398c350476fbe820f92"
DEV = "v1.4.0-development"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
CANONICAL = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt"
SUCCESSOR = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt"
CONTROLLED = ['release/v1.4.0/tools/patch_wp4_allowlist.py', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4.py']
EXPECTED_SUCCESSOR = ['.github/workflows/gate3-cluster-b-wp4-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp4_allowlist.py', 'release/v1.4.0/tools/patch_wp4_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp4_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/build_gate3_cluster_b_wp4_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp4_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp4.sh', 'scripts/verify_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp4_post_merge_closeout.py']
EXPECTED_CHANGED = ['.github/workflows/gate3-cluster-b-wp4-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp4_allowlist.py', 'release/v1.4.0/tools/patch_wp4_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp4_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp4.py', 'scripts/build_gate3_cluster_b_wp4_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp4_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp4.sh', 'scripts/verify_gate3_cluster_b_wp4.py', 'scripts/verify_gate3_cluster_b_wp4_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp4_post_merge_closeout.py']
PAIRS = [('release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_archival_closeout_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_development_branch_synchronization_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_hosted_ci_evidence.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_frozen_upstream_preservation_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json', 'schemas/v1.4.0/gate3_cluster_b_wp4_post_merge_closeout_gates.schema.json')]

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_sha(obj: dict) -> str:
    cp = json.loads(json.dumps(obj))
    cp["canonical_sha256"] = None
    return hashlib.sha256(
        json.dumps(cp, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

def parse_ledger(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            value, rel = line.split("  ", 1)
            out[rel] = value
    return out

def run(*args: str, check: bool = True, text: bool = True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=text, check=False)
    if check and cp.returncode:
        stderr = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(stderr.strip())
    return cp

def lines(*args: str) -> list[str]:
    return [row for row in run("git", *args).stdout.splitlines() if row]

def validate_records() -> list[str]:
    errors: list[str] = []
    for document, schema in PAIRS:
        try:
            Draft202012Validator(load(schema)).validate(load(document))
        except Exception as exc:
            errors.append(f"schema failure {document}: {exc}")

    close = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json")
    sync = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json")
    evidence = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_HOSTED_CI_EVIDENCE.json")
    preserve = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json")
    gates = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT_GATES.json")

    if close["merged_pr"] != 27 or close["merge_commit"] != MERGE or close["accepted_head_commit"] != ACCEPTED:
        errors.append("merge identity mismatch")
    if close["hosted_ci_checks"] != {"pass": 25, "fail": 0, "pending": 0, "skipped": 0, "total": 25}:
        errors.append("hosted check summary mismatch")
    if close["wp4_acceptance_gates"] != {"pass": 24, "fail": 0, "pending": 0, "total": 24}:
        errors.append("WP4 acceptance summary mismatch")
    if (
        close["canonical_wp4_records_modified"]
        or close["canonical_wp4_ledger_modified"]
        or close["closed_wp0_wp1_wp2_wp3_canonical_records_modified"]
        or close["proof_or_new_runtime_semantics_added"]
        or close["wp5_authorized"]
        or any(close["release_actions"].values())
    ):
        errors.append("closeout authorization firewall failure")
    if (
        sync["canonical_wp4_merge_baseline"] != MERGE
        or sync["sync_mode"] != "FAST_FORWARD_ONLY_AFTER_CLOSEOUT_MERGE"
        or sync["main_ahead_by"] != 1
        or sync["development_ahead_by"] != 0
        or sync["compare_status_at_capture"] != "MAIN_CONTAINS_DEVELOPMENT"
    ):
        errors.append("synchronization record mismatch")
    if sync["force_push_authorized"] or sync["history_rewrite_authorized"] or sync["branch_deletion_authorized"]:
        errors.append("synchronization authorization failure")
    if (
        evidence["source_pr"] != 27
        or evidence["source_head_sha"] != ACCEPTED
        or evidence["merge_commit"] != MERGE
        or evidence["check_summary"] != {"success": 25, "failure": 0, "pending": 0, "skipped": 0, "total": 25}
        or evidence["canonical_sha256"] != canonical_sha(evidence)
    ):
        errors.append("hosted evidence mismatch")
    if (
        preserve["canonical_wp4_records_modified"]
        or preserve["canonical_wp4_ledger_modified"]
        or preserve["closed_wp0_wp1_wp2_wp3_canonical_records_modified"]
        or preserve["fixture_count_preserved"] != 12
        or preserve["theorem_ids_preserved"] != [f"T{i}" for i in range(157, 163)]
        or preserve["statement_parity_percent_preserved"] != 100
        or preserve["release_actions_authorized"]
        or preserve["proof_implementation_authorized"]
        or preserve["runtime_semantics_modified_by_closeout"]
        or preserve["wp5_start_authorized"]
    ):
        errors.append("preservation record mismatch")
    if gates["gate_count"] != 21 or len(gates["gates"]) != 21 or any(row["status"] != "PASS" for row in gates["gates"]):
        errors.append("closeout gate failure")

    manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json")
    if manifest.get("schema_count") != 5 or manifest.get("document_count") != 5 or len(manifest.get("pairs", [])) != 5:
        errors.append("schema bundle mismatch")
    else:
        for item in manifest["pairs"]:
            document = ROOT / item["document"]
            schema = ROOT / item["schema"]
            if not document.is_file() or digest(document) != item["document_sha256"]:
                errors.append("schema bundle document hash mismatch: " + item["document"])
            if not schema.is_file() or digest(schema) != item["schema_sha256"]:
                errors.append("schema bundle schema hash mismatch: " + item["schema"])
    return errors

def verify_ledger() -> list[str]:
    errors: list[str] = []
    if not CANONICAL.is_file() or not SUCCESSOR.is_file():
        return ["missing historical or successor WP4 ledger"]
    historical = parse_ledger(CANONICAL)
    successor = parse_ledger(SUCCESSOR)
    if set(successor) != set(EXPECTED_SUCCESSOR):
        errors.append("successor ledger path set mismatch")
    if set(historical) & set(successor) != set(CONTROLLED):
        errors.append("unexpected historical/successor overlap")
    try:
        historical_bytes = run(
            "git", "show", f"{MERGE}:release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt", text=False
        ).stdout
        if CANONICAL.read_bytes() != historical_bytes:
            errors.append("canonical WP4 ledger modified")
    except Exception as exc:
        errors.append("cannot verify canonical WP4 ledger: " + str(exc))
    for rel, old_hash in historical.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append("historical file missing: " + rel)
            continue
        expected = successor.get(rel, old_hash)
        if digest(path) != expected:
            errors.append("historical/successor hash mismatch: " + rel)
    for rel, expected in successor.items():
        path = ROOT / rel
        if not path.is_file() or digest(path) != expected:
            errors.append("successor hash mismatch: " + rel)
    return errors

def git_checks(allow_main: bool, package_only: bool) -> list[str]:
    errors: list[str] = []
    branch = run("git", "branch", "--show-current", check=False).stdout.strip()
    effective = branch or os.environ.get("GITHUB_HEAD_REF", "") or os.environ.get("GITHUB_REF_NAME", "")
    if not package_only and effective != DEV and not (allow_main and effective == "main"):
        errors.append("unexpected branch " + repr(effective))

    try:
        parents = run("git", "show", "-s", "--format=%P", MERGE).stdout.strip().split()
        if parents != [BASELINE, ACCEPTED]:
            errors.append("merge parent identity mismatch")
        if run("git", "rev-parse", MERGE + "^{tree}").stdout.strip() != run(
            "git", "rev-parse", ACCEPTED + "^{tree}"
        ).stdout.strip():
            errors.append("merge tree mismatch")
    except Exception as exc:
        errors.append("merge identity check failure: " + str(exc))

    if run("git", "merge-base", "--is-ancestor", ACCEPTED, "HEAD", check=False).returncode:
        errors.append("HEAD does not contain accepted WP4 head")

    changed = set(lines("diff", "--name-only", MERGE, "--"))
    changed.update(lines("ls-files", "--others", "--exclude-standard"))
    changed.discard("")
    if changed != set(EXPECTED_CHANGED):
        errors.append(
            "closeout path set mismatch: missing="
            + repr(sorted(set(EXPECTED_CHANGED) - changed))
            + ", extra="
            + repr(sorted(changed - set(EXPECTED_CHANGED)))
        )
    statuses: dict[str, str] = {}
    for row in lines("diff", "--name-status", MERGE, "--"):
        code, rel = row.split("\t", 1)
        statuses[rel] = code
    for rel in lines("ls-files", "--others", "--exclude-standard"):
        statuses[rel] = "A"
    for rel in CONTROLLED:
        if statuses.get(rel) != "M":
            errors.append("controlled path status mismatch: " + rel)
    for rel in set(EXPECTED_CHANGED) - set(CONTROLLED):
        if statuses.get(rel) != "A":
            errors.append("new path status mismatch: " + rel)

    immutable = {
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_ACCEPTANCE_GATES.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_BASELINE_LOCK.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_PRESERVATION_FIREWALL.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_SCHEMA_BUNDLE_MANIFEST.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_SHA256SUMS.txt",
        "release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json",
    }
    if changed & immutable:
        errors.append("canonical WP4 record or ledger changed: " + repr(sorted(changed & immutable)))

    tag = run("git", "rev-parse", "refs/tags/v1.3.0^{}", check=False).stdout.strip()
    if tag != TAG_TARGET:
        errors.append("stable v1.3.0 tag target changed")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--allow-main", action="store_true")
    args = parser.parse_args()

    errors = validate_records() + verify_ledger() + git_checks(args.allow_main, args.package_only)
    result = {
        "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP4_POST_MERGE_CLOSEOUT",
        "errors": errors,
        "hosted_checks": "25/25 PASS",
        "merge_commit": MERGE,
        "merged_pr": 27,
        "release_actions_authorized": False,
        "status": "PASS" if not errors else "FAIL",
        "wp4_acceptance": "24/24 PASS",
        "wp5_authorized": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
