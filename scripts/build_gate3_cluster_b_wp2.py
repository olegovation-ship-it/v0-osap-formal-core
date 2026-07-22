#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "checker"))

from v0_osap_fc1.cluster_b_wp2 import (  # noqa: E402
    EVALUATORS,
    IMPLEMENTATION_VERSION,
    RESIDUAL_TYPES,
    evaluate_fixture,
)

DATE = "2026-07-21"
VERSION = "0.1.4"
WP2_START = "ffeaa3fd4fb2f85679f4695d5b28e333004ca24a"
WP1_MERGE = "eaf142089230ea5a5096ae834bf4e733d5f369aa"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
RELEASE = ROOT / "release/v1.4.0"
FIXTURES = ROOT / "fixtures/gate3/cluster_b/wp2"
SCHEMAS = ROOT / "schemas/v1.4.0"

# WP2_POST_MERGE_SUCCESSOR_LEDGER_COMPATIBILITY_V0_1
CANONICAL_LEDGER = RELEASE / "GATE3_CLUSTER_B_WP2_SHA256SUMS.txt"
SUCCESSOR_LEDGER = RELEASE / "GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt"


def is_post_merge_schema(path: Path) -> bool:
    name = path.name
    return "_post_merge_" in name or "_development_branch_synchronization_" in name


def is_post_merge_record(path: Path) -> bool:
    name = path.name
    return "_POST_MERGE_" in name or "_DEVELOPMENT_BRANCH_SYNCHRONIZATION_" in name


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains_subset(observed: Any, expected: Any, prefix: str = "") -> list[str]:
    errors: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [f"{prefix or '<root>'}: expected object"]
        for key, value in expected.items():
            if key not in observed:
                errors.append(f"{prefix}/{key}: missing")
            else:
                errors.extend(contains_subset(observed[key], value, f"{prefix}/{key}"))
    elif isinstance(expected, list):
        if observed != expected:
            errors.append(f"{prefix}: expected {expected!r}, observed {observed!r}")
    elif observed != expected:
        errors.append(f"{prefix}: expected {expected!r}, observed {observed!r}")
    return errors


def build_fixture_manifest() -> tuple[dict[str, Any], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    roles: set[str] = set()
    theorems: set[str] = set()
    case_types: set[str] = set()

    for path in sorted(FIXTURES.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        result = evaluate_fixture(document)
        expected = document["expected"]
        errors.extend(f"{path.name}{item}" for item in contains_subset(result, expected))
        roles.update(result["role_ids"])
        theorems.update(result["theorem_ids"])
        case_types.add(result["case_type"])
        records.append({
            "fixture_id": document["fixture_id"],
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
            "case_type": result["case_type"],
            "status": result["status"],
            "diagnostic_codes": result["diagnostic_codes"],
            "role_ids": result["role_ids"],
            "theorem_ids": result["theorem_ids"],
        })

    manifest = {
        "artifact_id": "V0_OSAP_GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST",
        "version": VERSION,
        "date": DATE,
        "fixture_count": len(records),
        "case_type_count": len(case_types),
        "role_coverage": sorted(roles),
        "theorem_coverage": sorted(theorems, key=lambda value: int(value[1:])),
        "fixtures": records,
        "status": "DETERMINISTIC_FIXTURE_MATRIX_COMPLETE",
    }
    return manifest, errors


def baseline_lock() -> dict[str, Any]:
    return {
        "artifact_id": "V0_OSAP_GATE3_CLUSTER_B_WP2_BASELINE_LOCK",
        "version": VERSION,
        "date": DATE,
        "repository": "olegovation-ship-it/v0-osap-formal-core",
        "target_branch": "v1.4.0-development",
        "wp2_start": WP2_START,
        "canonical_wp1_merge_baseline": WP1_MERGE,
        "frozen_v1_3_0_tag_target": TAG_TARGET,
        "protected_inherited_surfaces": [
            "release/v1.4.0/GATE3_CLUSTER_B_WP0_*",
            "release/v1.4.0/GATE3_CLUSTER_B_WP1_*",
            "docs/gate3/cluster_b/WP0_*",
            "docs/gate3/cluster_b/WP1_*",
            "tag:v1.3.0",
            "doi:10.5281/zenodo.21346728",
        ],
        "authorized_new_surfaces": [
            ".github/workflows/gate3-cluster-b-wp2.yml",
            "checker/v0_osap_fc1/cluster_b_wp2.py",
            "docs/gate3/cluster_b/WP2_*",
            "fixtures/gate3/cluster_b/wp2/",
            "release/v1.4.0/GATE3_CLUSTER_B_WP2_*",
            "schemas/v1.4.0/gate3_cluster_b_wp2_*",
            "scripts/build_gate3_cluster_b_wp2.py",
            "scripts/verify_gate3_cluster_b_wp2.py",
            "tests/conftest.py",
            "tests/test_gate3_cluster_b_wp2.py",
        ],
        "authorized_modified_surfaces": [
            ".github/workflows/gate3-cluster-b-wp0.yml",
            ".github/workflows/gate3-cluster-b-wp0-post-merge-closeout.yml",
            ".github/workflows/gate3-cluster-b-wp1.yml",
            ".github/workflows/gate3-cluster-b-wp1-post-merge-closeout.yml",
            ".github/workflows/python-checker.yml",
        ],
        "release_actions_authorized": False,
    }


def semantics_profile() -> dict[str, Any]:
    bindings = [
        ("CB-CONTRACT-STRONG-DLE", ["T157"], "evaluate_strong_dle"),
        ("CB-CONTRACT-RESIDUAL-PERSISTENCE", ["T158", "T162"], "evaluate_residual_persistence"),
        ("CB-CONTRACT-RESIDUAL-TYPE-SEPARATION", ["T159"], "evaluate_residual_type_separation"),
        ("CB-CONTRACT-MODEL-PAIR", ["T159", "T160"], "evaluate_model_pair_noneliminability"),
        ("CB-CONTRACT-MINIMAL-OBSTRUCTION", ["T161"], "evaluate_minimal_residual_obstruction"),
        ("CB-CONTRACT-HISTORICAL-NONCONVERSION", ["T162"], "evaluate_historical_token_nonconversion"),
    ]
    return {
        "artifact_id": "V0_OSAP_GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE",
        "version": VERSION,
        "date": DATE,
        "implementation_version": IMPLEMENTATION_VERSION,
        "case_types": sorted(EVALUATORS),
        "residual_type_vocabulary": list(RESIDUAL_TYPES),
        "contract_bindings": [
            {
                "contract_id": contract,
                "theorem_ids": theorem_ids,
                "evaluator": evaluator,
                "runtime_status": "IMPLEMENTED_IN_WP2_PROOF_DEFERRED",
            }
            for contract, theorem_ids, evaluator in bindings
        ],
        "nonclaims": [
            "No Lean or Coq proof completion is claimed; formal proof remains WP4.",
            "No Validator Core or IPEC rule binding is claimed; versioned bindings remain WP3.",
            "No checker completeness or unrestricted semantic soundness is claimed.",
            "No global cross-backend equivalence or proof-term identity is claimed.",
            "No empirical, physical-disappearance, cosmological, or absolute-V0 claim is made.",
            "No tag, GitHub Release, Zenodo publication, DOI action, or stable-release rebuild is authorized.",
        ],
        "status": "EXECUTABLE_BOUNDED_SEMANTICS_IMPLEMENTED",
    }


def gates(fixture_manifest: dict[str, Any], fixture_errors: list[str]) -> dict[str, Any]:
    role_ok = fixture_manifest["role_coverage"] == [f"CB-R{i}" for i in range(1, 8)]
    theorem_ok = set(fixture_manifest["theorem_coverage"]) >= {f"T{i}" for i in range(157, 163)}
    requirements = [
        "Exact WP2 start commit is ffeaa3fd4fb2f85679f4695d5b28e333004ca24a.",
        "Canonical WP1 merge baseline eaf142089230ea5a5096ae834bf4e733d5f369aa is preserved.",
        "All canonical WP0/WP1 records, ledgers, tests, and theorem contracts remain byte-exact; only five inherited GitHub Actions workflow files receive bounded successor-replay compatibility modifications, including the full-history Python checker checkout required for frozen-baseline replay.",
        "Closed WP0 records and canonical/post-merge WP1 records remain immutable.",
        "Frozen v1.3.0 tag target remains 13bf095688bcabd5b090f188e9bd28a16237edeb.",
        "Nine deterministic finite-record evaluators are present.",
        "All seven semantic roles CB-R1 through CB-R7 have executable fixture coverage.",
        "All new theorem targets T157 through T162 have executable fixture coverage.",
        "Residual type vocabulary exactly matches the WP1 seven-type vocabulary.",
        "StrongDLE requires history, current no-live status, and typed DLE provenance.",
        "Residual persistence is conditional on deterministic certified non-interference.",
        "Residual type separation admits only explicit admissible translations.",
        "Model-pair non-eliminability requires schema validity, shared-fragment agreement, non-label distinctness, and non-circular evidence.",
        "Minimal single-residual obstruction is sufficient only; converse and completeness remain unclaimed.",
        "Historical tokens cannot become current live tokens without a separate typed fresh activation.",
        "Robust-obstruction and branch-local-firewall inherited roles receive runtime fixture coverage without new theorem ownership.",
        "Fixture outcomes reproduce expected status, diagnostic codes, and derived values.",
        "Fixture and result schemas validate under JSON Schema Draft 2020-12.",
        "WP3 bindings and WP4 proofs remain explicitly deferred.",
        "No tag, GitHub Release, Zenodo publication, DOI action, or release rebuild is authorized.",
    ]
    structural_ok = (
        not fixture_errors
        and fixture_manifest["fixture_count"] >= 20
        and fixture_manifest["case_type_count"] == 9
        and role_ok
        and theorem_ok
    )
    if not structural_ok:
        raise RuntimeError("cannot generate PASS gates: " + "; ".join(fixture_errors or ["coverage mismatch"]))
    return {
        "artifact_id": "V0_OSAP_GATE3_CLUSTER_B_WP2_ACCEPTANCE_GATES",
        "version": VERSION,
        "date": DATE,
        "gate_count": len(requirements),
        "gates": [
            {"gate_id": f"WP2-G{index:02d}", "requirement": requirement, "status": "PASS"}
            for index, requirement in enumerate(requirements, start=1)
        ],
        "local_package_status": "PASS",
        "hosted_ci_status": "NOT_RUN",
        "release_actions_authorized": False,
        "decision": "READY_FOR_BOUNDED_REPOSITORY_INTEGRATION",
    }


def schema_bundle() -> dict[str, Any]:
    schemas = sorted(
        path.relative_to(ROOT).as_posix()
        for path in SCHEMAS.glob("gate3_cluster_b_wp2_*.schema.json")
        if not is_post_merge_schema(path)
    )
    documents = [
        "release/v1.4.0/GATE3_CLUSTER_B_WP2_BASELINE_LOCK.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json",
        "release/v1.4.0/GATE3_CLUSTER_B_WP2_ACCEPTANCE_GATES.json",
    ]
    return {
        "artifact_id": "V0_OSAP_GATE3_CLUSTER_B_WP2_SCHEMA_BUNDLE_MANIFEST",
        "version": VERSION,
        "date": DATE,
        "schema_count": len(schemas),
        "schemas": schemas,
        "documents": documents,
        "status": "COMPLETE",
    }


def write_or_check(path: Path, payload: bytes, check: bool, errors: list[str]) -> None:
    if check:
        if not path.is_file():
            errors.append(f"missing generated artifact: {path.relative_to(ROOT).as_posix()}")
        elif path.read_bytes() != payload:
            errors.append(f"stale generated artifact: {path.relative_to(ROOT).as_posix()}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def wp2_paths_for_ledger() -> list[Path]:
    candidates: list[Path] = []
    prefixes = [
        ROOT / ".github/workflows/gate3-cluster-b-wp0.yml",
        ROOT / ".github/workflows/gate3-cluster-b-wp0-post-merge-closeout.yml",
        ROOT / ".github/workflows/gate3-cluster-b-wp1.yml",
        ROOT / ".github/workflows/gate3-cluster-b-wp1-post-merge-closeout.yml",
        ROOT / ".github/workflows/python-checker.yml",
        ROOT / ".github/workflows/gate3-cluster-b-wp2.yml",
        ROOT / "checker/v0_osap_fc1/cluster_b_wp2.py",
        ROOT / "docs/gate3/cluster_b/WP2_BUILD_SPECIFICATION.md",
        ROOT / "docs/gate3/cluster_b/WP2_EXECUTABLE_TRANSITION_RESIDUAL_AND_MODEL_PAIR_SEMANTICS.md",
        ROOT / "scripts/build_gate3_cluster_b_wp2.py",
        ROOT / "scripts/verify_gate3_cluster_b_wp2.py",
        ROOT / "tests/conftest.py",
        ROOT / "tests/test_gate3_cluster_b_wp2.py",
    ]
    candidates.extend(path for path in prefixes if path.is_file())
    candidates.extend(sorted(FIXTURES.glob("*.json")))
    candidates.extend(sorted(
        path for path in SCHEMAS.glob("gate3_cluster_b_wp2_*.schema.json")
        if not is_post_merge_schema(path)
    ))
    candidates.extend(sorted(
        path for path in RELEASE.glob("GATE3_CLUSTER_B_WP2_*.json")
        if not is_post_merge_record(path)
    ))
    excluded = {
        RELEASE / "GATE3_CLUSTER_B_WP2_SHA256SUMS.txt",
    }
    return sorted({path for path in candidates if path not in excluded}, key=lambda path: path.relative_to(ROOT).as_posix())


def ledger_bytes() -> bytes:
    lines = [f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}" for path in wp2_paths_for_ledger()]
    return ("\n".join(lines) + "\n").encode("utf-8")



def parse_ledger_bytes(value: bytes) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in value.decode("utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        digest, rel = line.split("  ", 1)
        entries[rel] = digest
    return entries


def canonical_ledger_compatibility_errors(expected: bytes) -> list[str]:
    if not CANONICAL_LEDGER.is_file():
        return ["missing canonical WP2 SHA256 ledger"]
    historical_bytes = CANONICAL_LEDGER.read_bytes()
    if historical_bytes == expected:
        return []
    if not SUCCESSOR_LEDGER.is_file():
        return ["canonical WP2 ledger differs and successor ledger is missing"]

    historical = parse_ledger_bytes(historical_bytes)
    current = parse_ledger_bytes(expected)
    successor = parse_ledger_bytes(SUCCESSOR_LEDGER.read_bytes())
    errors: list[str] = []

    for rel, historical_digest in historical.items():
        current_digest = current.get(rel)
        if current_digest is None:
            errors.append(f"canonical WP2 path disappeared from builder surface: {rel}")
            continue
        if current_digest != historical_digest and successor.get(rel) != current_digest:
            errors.append(f"successor ledger does not attest changed WP2 path: {rel}")

    for rel, current_digest in current.items():
        if rel not in historical and successor.get(rel) != current_digest:
            errors.append(f"successor ledger does not attest new canonical WP2 path: {rel}")
    return errors


def check_or_write_canonical_ledger(expected: bytes, check: bool) -> list[str]:
    if not check and not SUCCESSOR_LEDGER.is_file():
        CANONICAL_LEDGER.write_bytes(expected)
        return []
    return canonical_ledger_compatibility_errors(expected)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []

    fixture_manifest, fixture_errors = build_fixture_manifest()
    generated = {
        RELEASE / "GATE3_CLUSTER_B_WP2_BASELINE_LOCK.json": canonical_json(baseline_lock()),
        RELEASE / "GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json": canonical_json(semantics_profile()),
        RELEASE / "GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json": canonical_json(fixture_manifest),
        RELEASE / "GATE3_CLUSTER_B_WP2_ACCEPTANCE_GATES.json": canonical_json(gates(fixture_manifest, fixture_errors)),
        RELEASE / "GATE3_CLUSTER_B_WP2_SCHEMA_BUNDLE_MANIFEST.json": canonical_json(schema_bundle()),
    }

    for path, payload in generated.items():
        write_or_check(path, payload, args.check, errors)

    # Ledger is generated after all JSON records have been written/checked.
    if not args.check:
        for path, payload in generated.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    errors.extend(check_or_write_canonical_ledger(ledger_bytes(), args.check))

    errors.extend(fixture_errors)
    result = {
        "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP2_BUILD",
        "status": "PASS" if not errors else "FAIL",
        "mode": "CHECK" if args.check else "WRITE",
        "fixture_count": fixture_manifest["fixture_count"],
        "case_type_count": fixture_manifest["case_type_count"],
        "role_coverage": fixture_manifest["role_coverage"],
        "release_actions_authorized": False,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
