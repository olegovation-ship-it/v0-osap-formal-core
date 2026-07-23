#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "checker"))

from v0_osap_fc1.cluster_b_wp2 import (  # noqa: E402
    EVALUATORS,
    RESIDUAL_TYPES,
    evaluate_fixture,
)

WP2_START = "ffeaa3fd4fb2f85679f4695d5b28e333004ca24a"
WP1_MERGE = "eaf142089230ea5a5096ae834bf4e733d5f369aa"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
TARGET_BRANCH = "v1.4.0-development"
RELEASE = ROOT / "release/v1.4.0"
FIXTURES = ROOT / "fixtures/gate3/cluster_b/wp2"
SCHEMAS = ROOT / "schemas/v1.4.0"

# WP2_POST_MERGE_SUCCESSOR_LEDGER_COMPATIBILITY_V0_1
CANONICAL_LEDGER = RELEASE / "GATE3_CLUSTER_B_WP2_SHA256SUMS.txt"
SUCCESSOR_LEDGER = RELEASE / "GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt"
POST_MERGE_SUPERSEDED_PATHS = {
    "scripts/build_gate3_cluster_b_wp2.py",
    "scripts/verify_gate3_cluster_b_wp2.py",
}

ALLOWED_NEW_FILES = {
    ".github/workflows/gate3-cluster-b-wp2.yml",
    "checker/v0_osap_fc1/cluster_b_wp2.py",
    "docs/gate3/cluster_b/WP2_BUILD_SPECIFICATION.md",
    "docs/gate3/cluster_b/WP2_EXECUTABLE_TRANSITION_RESIDUAL_AND_MODEL_PAIR_SEMANTICS.md",
    "scripts/build_gate3_cluster_b_wp2.py",
    "scripts/verify_gate3_cluster_b_wp2.py",
    "tests/conftest.py",
    "tests/test_gate3_cluster_b_wp2.py",

    # WP2_POST_MERGE_SUCCESSOR_LEDGER_COMPATIBILITY_V0_1
    ".github/workflows/gate3-cluster-b-wp2-post-merge-closeout.yml",
    "docs/gate3/cluster_b/WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md",
    "release/v1.4.0/tools/patch_wp2_post_merge_allowlist.py",
    "scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py",
    "scripts/capture_gate3_cluster_b_wp2_post_merge_evidence.py",
    "scripts/synchronize_v1_4_0_development_wp2.sh",
    "scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp2_post_merge_closeout.py",

    # WP3_SUCCESSOR_FIREWALL_HANDOFF_V0_1
    ".github/workflows/gate3-cluster-b-wp3.yml",
    "checker/v0_osap_fc1/cluster_b_wp3.py",
    "scripts/build_gate3_cluster_b_wp3.py",
    "scripts/verify_gate3_cluster_b_wp3.py",
    "tests/test_gate3_cluster_b_wp3.py",

    # WP3_POST_MERGE_SUCCESSOR_FIREWALL_HANDOFF_V0_1_1
    ".github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml",
    "release/v1.4.0/tools/patch_wp3_post_merge_allowlist.py",
    "scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py",
    "scripts/capture_gate3_cluster_b_wp3_post_merge_evidence.py",
    "scripts/synchronize_v1_4_0_development_wp3.sh",
    "scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py",
    "tests/test_gate3_cluster_b_wp3_post_merge_closeout.py",
}
ALLOWED_NEW_PREFIXES = (
    "fixtures/gate3/cluster_b/wp2/",
    "release/v1.4.0/GATE3_CLUSTER_B_WP2_",
    "schemas/v1.4.0/gate3_cluster_b_wp2_",

    # WP3_SUCCESSOR_FIREWALL_HANDOFF_V0_1
    "docs/gate3/cluster_b/WP3_",
    "fixtures/gate3/cluster_b/wp3/",
    "release/v1.4.0/GATE3_CLUSTER_B_WP3_",
    "schemas/v1.4.0/gate3_cluster_b_wp3_",
)
ALLOWED_MODIFIED_FILES = {
    ".github/workflows/gate3-cluster-b-wp0.yml",
    ".github/workflows/gate3-cluster-b-wp0-post-merge-closeout.yml",
    ".github/workflows/gate3-cluster-b-wp1.yml",
    ".github/workflows/gate3-cluster-b-wp1-post-merge-closeout.yml",
    ".github/workflows/python-checker.yml",
}
PROTECTED_PREFIXES = (
    "release/v1.4.0/GATE3_CLUSTER_B_WP0_",
    "release/v1.4.0/GATE3_CLUSTER_B_WP1_",
    "docs/gate3/cluster_b/WP0_",
    "docs/gate3/cluster_b/WP1_",
)


def run(*args: str, check: bool = True) -> str:
    proc = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{proc.stderr.strip()}")
    return proc.stdout.strip()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subset_errors(observed: Any, expected: Any, prefix: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [f"{prefix or '<root>'}: expected object"]
        for key, value in expected.items():
            if key not in observed:
                errors.append(f"{prefix}/{key}: missing")
            else:
                errors.extend(subset_errors(observed[key], value, f"{prefix}/{key}"))
    elif observed != expected:
        errors.append(f"{prefix}: expected {expected!r}, observed {observed!r}")
    return errors


def validate_schemas() -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema dependency unavailable"]

    fixture_schema = load(SCHEMAS / "gate3_cluster_b_wp2_fixture.schema.json")
    result_schema = load(SCHEMAS / "gate3_cluster_b_wp2_result.schema.json")
    for path in sorted(FIXTURES.glob("*.json")):
        try:
            document = load(path)
            jsonschema.Draft202012Validator(fixture_schema).validate(document)
            jsonschema.Draft202012Validator(result_schema).validate(evaluate_fixture(document))
        except Exception as exc:
            errors.append(f"schema failure {path.relative_to(ROOT).as_posix()}: {exc}")

    pairs = [
        (RELEASE / "GATE3_CLUSTER_B_WP2_BASELINE_LOCK.json", SCHEMAS / "gate3_cluster_b_wp2_baseline_lock.schema.json"),
        (RELEASE / "GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json", SCHEMAS / "gate3_cluster_b_wp2_fixture_manifest.schema.json"),
        (RELEASE / "GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json", SCHEMAS / "gate3_cluster_b_wp2_semantics_profile.schema.json"),
        (RELEASE / "GATE3_CLUSTER_B_WP2_ACCEPTANCE_GATES.json", SCHEMAS / "gate3_cluster_b_wp2_acceptance_gates.schema.json"),
    ]
    for document_path, schema_path in pairs:
        try:
            jsonschema.Draft202012Validator(load(schema_path)).validate(load(document_path))
        except Exception as exc:
            errors.append(f"schema failure {document_path.relative_to(ROOT).as_posix()}: {exc}")
    return errors


def fixture_errors() -> list[str]:
    errors: list[str] = []
    roles: set[str] = set()
    theorems: set[str] = set()
    cases: set[str] = set()
    paths = sorted(FIXTURES.glob("*.json"))
    if len(paths) < 20:
        errors.append(f"fixture count below 20: {len(paths)}")
    for path in paths:
        document = load(path)
        result = evaluate_fixture(document)
        roles.update(result["role_ids"])
        theorems.update(result["theorem_ids"])
        cases.add(result["case_type"])
        errors.extend(
            f"{path.name}{error}"
            for error in subset_errors(result, document["expected"])
        )
        if result["proof_claimed"] or result["ipec_binding_claimed"] or result["release_action_authorized"]:
            errors.append(f"authorization overclaim in {path.name}")
    if roles != {f"CB-R{i}" for i in range(1, 8)}:
        errors.append(f"semantic role coverage mismatch: {sorted(roles)}")
    if not {f"T{i}" for i in range(157, 163)} <= theorems:
        errors.append(f"T157-T162 coverage incomplete: {sorted(theorems)}")
    if cases != set(EVALUATORS):
        errors.append(f"case type coverage mismatch: {sorted(cases)}")
    return errors


def record_errors() -> list[str]:
    errors: list[str] = []
    lock = load(RELEASE / "GATE3_CLUSTER_B_WP2_BASELINE_LOCK.json")
    if lock["wp2_start"] != WP2_START:
        errors.append("WP2 exact start mismatch")
    if lock["canonical_wp1_merge_baseline"] != WP1_MERGE:
        errors.append("WP1 merge baseline mismatch")
    if lock["frozen_v1_3_0_tag_target"] != TAG_TARGET:
        errors.append("frozen v1.3.0 target mismatch")
    if set(lock["authorized_modified_surfaces"]) != ALLOWED_MODIFIED_FILES:
        errors.append("authorized modified workflow surface mismatch")
    if lock["release_actions_authorized"]:
        errors.append("release actions authorized in baseline lock")

    profile = load(RELEASE / "GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json")
    if set(profile["case_types"]) != set(EVALUATORS):
        errors.append("semantics profile case types mismatch")
    if tuple(profile["residual_type_vocabulary"]) != RESIDUAL_TYPES:
        errors.append("residual vocabulary mismatch")
    if len(profile["contract_bindings"]) != 6:
        errors.append("contract binding count mismatch")

    manifest = load(RELEASE / "GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json")
    if manifest["fixture_count"] != len(list(FIXTURES.glob("*.json"))):
        errors.append("fixture manifest count mismatch")
    for item in manifest["fixtures"]:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"manifest missing fixture: {item['path']}")
        elif sha256(path) != item["sha256"]:
            errors.append(f"fixture hash mismatch: {item['path']}")

    gates = load(RELEASE / "GATE3_CLUSTER_B_WP2_ACCEPTANCE_GATES.json")
    if gates["gate_count"] != 20 or len(gates["gates"]) != 20:
        errors.append("acceptance gate count mismatch")
    if any(gate["status"] != "PASS" for gate in gates["gates"]):
        errors.append("acceptance gate failure")
    if gates["release_actions_authorized"]:
        errors.append("release action gate failure")
    return errors


def read_sha256_ledger(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        digest, rel = line.split("  ", 1)
        entries[rel] = digest
    return entries


def ledger_errors() -> list[str]:
    if not CANONICAL_LEDGER.is_file():
        return ["missing WP2 SHA256 ledger"]
    historical = read_sha256_ledger(CANONICAL_LEDGER)
    successor = read_sha256_ledger(SUCCESSOR_LEDGER) if SUCCESSOR_LEDGER.is_file() else {}
    errors: list[str] = []

    overlap = set(historical) & set(successor)
    if successor and overlap != POST_MERGE_SUPERSEDED_PATHS:
        errors.append(f"unexpected WP2/post-merge ledger overlap: {sorted(overlap)}")

    for rel, historical_expected in historical.items():
        target = ROOT / rel
        if not target.is_file():
            errors.append(f"ledger missing file: {rel}")
            continue
        expected = successor.get(rel) if rel in POST_MERGE_SUPERSEDED_PATHS else historical_expected
        if expected is None:
            errors.append(f"successor ledger missing superseded path: {rel}")
            continue
        if sha256(target) != expected:
            errors.append(f"SHA256 mismatch: {rel}")

    if successor:
        for rel, expected in successor.items():
            target = ROOT / rel
            if not target.is_file():
                errors.append(f"successor ledger missing file: {rel}")
            elif sha256(target) != expected:
                errors.append(f"successor SHA256 mismatch: {rel}")
    return errors

def is_allowed_new(path: str) -> bool:
    return path in ALLOWED_NEW_FILES or any(path.startswith(prefix) for prefix in ALLOWED_NEW_PREFIXES)


def git_errors(allow_main: bool) -> list[str]:
    errors: list[str] = []
    if not (ROOT / ".git").exists():
        return ["not a git repository"]
    branch = run("git", "branch", "--show-current", check=False)
    effective = branch or os.environ.get("GITHUB_HEAD_REF", "") or os.environ.get("GITHUB_REF_NAME", "")
    if effective != TARGET_BRANCH and not (allow_main and effective == "main"):
        errors.append(f"unexpected branch {effective!r}")
    try:
        run("git", "cat-file", "-e", f"{WP2_START}^{{commit}}")
        run("git", "merge-base", "--is-ancestor", WP2_START, "HEAD")
        if run("git", "rev-parse", "refs/tags/v1.3.0^{}") != TAG_TARGET:
            errors.append("stable v1.3.0 tag target changed")
    except RuntimeError as exc:
        errors.append(str(exc))

    changed_existing = run(
        "git", "-c", "core.quotePath=false", "diff", "--name-only", "--diff-filter=MDR", WP2_START, "--", check=False
    ).splitlines()
    for path in sorted(filter(None, changed_existing)):
        if path in ALLOWED_MODIFIED_FILES:
            continue
        if any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            errors.append(f"protected inherited surface modified: {path}")
        else:
            errors.append(f"WP2 overlay modified/deleted pre-existing path: {path}")

    new_paths = set(run(
        "git", "-c", "core.quotePath=false", "diff", "--name-only", "--diff-filter=A", WP2_START, "--", check=False
    ).splitlines())
    new_paths.update(run(
        "git", "-c", "core.quotePath=false", "ls-files", "--others", "--exclude-standard", check=False
    ).splitlines())
    new_paths.discard("")
    for path in sorted(new_paths):
        if not is_allowed_new(path):
            errors.append(f"path outside WP2 allowlist: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--allow-main", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    errors.extend(validate_schemas())
    errors.extend(fixture_errors())
    errors.extend(record_errors())
    errors.extend(ledger_errors())
    if not args.package_only:
        errors.extend(git_errors(args.allow_main))

    result = {
        "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP2",
        "status": "PASS" if not errors else "FAIL",
        "decision": "READY_FOR_HOSTED_CI" if not errors else "HOLD_WITH_BLOCKERS",
        "baseline": WP2_START,
        "target_branch": TARGET_BRANCH,
        "fixture_count": len(list(FIXTURES.glob("*.json"))),
        "case_types": sorted(EVALUATORS),
        "semantic_roles": "7/7" if not errors else "CHECK_FAILED",
        "theorem_targets": [f"T{i}" for i in range(157, 163)],
        "release_actions_authorized": False,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
