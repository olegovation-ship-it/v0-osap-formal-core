from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_wp0_records_are_present_and_consistent():
    lock = load("release/v1.4.0/GATE3_CLUSTER_B_WP0_BASELINE_LOCK.json")
    branch = load("release/v1.4.0/GATE3_CLUSTER_B_WP0_BRANCH_BOOTSTRAP_SPEC.json")
    preserve = load("release/v1.4.0/GATE3_CLUSTER_B_WP0_FROZEN_UPSTREAM_PRESERVATION_RECORD.json")
    gates = load("release/v1.4.0/GATE3_CLUSTER_B_WP0_ACCEPTANCE_GATES.json")
    assert lock["branch_start"]["exact_commit"] == "a13a96fda4964dde1719c7d014f11878e1103b20"
    assert branch["target_branch"] == "v1.4.0-development"
    assert preserve["canonical_new_theorem_ids_authorized"] == []
    assert preserve["release_actions_authorized"] is False
    assert gates["gate_count"] == len(gates["gates"]) == 14


def test_release_actions_are_all_false():
    lock = load("release/v1.4.0/GATE3_CLUSTER_B_WP0_BASELINE_LOCK.json")
    assert not any(lock["release_actions_authorized"].values())


def test_schema_bundle_count():
    manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP0_SCHEMA_BUNDLE_MANIFEST.json")
    assert manifest["schema_count"] == 4
    assert all((ROOT / p).is_file() for p in manifest["schemas"])


def test_verifier_package_only_passes():
    spec = importlib.util.spec_from_file_location("wp0_verify", ROOT / "scripts/verify_gate3_cluster_b_wp0.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.validate_json(ROOT) == []


def test_wp0_does_not_add_implementation_surfaces():
    forbidden = [ROOT / "checker/v0_osap_fc1/cluster_b.py", ROOT / "lean/V0OSAP/ClusterB.lean", ROOT / "coq/theories/ClusterB.v"]
    assert all(not p.exists() for p in forbidden)


def test_wp0_allowlist_covers_control_surfaces():
    spec = importlib.util.spec_from_file_location(
        "wp0_allowlist",
        ROOT / "scripts/verify_gate3_cluster_b_wp0.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    assert module.is_allowed_path(
        "scripts/verify_gate3_cluster_b_wp0.py"
    )
    assert module.is_allowed_path(
        ".github/workflows/gate3-cluster-b-wp0.yml"
    )
    assert module.is_allowed_path(
        "release/v1.4.0/GATE3_CLUSTER_B_WP0_BASELINE_LOCK.json"
    )
    assert module.is_allowed_path(
        "schemas/v1.4.0/gate3_cluster_b_wp0_baseline_lock.schema.json"
    )

    assert not module.is_allowed_path(
        "checker/v0_osap_fc1/cluster_b.py"
    )


def git_object_available(revision: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", revision],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def test_wp0_full_git_firewall_accepts_current_patch():
    spec = importlib.util.spec_from_file_location(
        "wp0_full_git_firewall",
        ROOT / "scripts/verify_gate3_cluster_b_wp0.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    required_objects = (
        f"{module.BASE}^{{commit}}",
        "refs/tags/v1.3.0^{}",
    )

    if not all(git_object_available(obj) for obj in required_objects):
        pytest.skip(
            "full-history checkout with the frozen v1.3.0 tag is required"
        )

    assert module.git_checks(ROOT, allow_main=False) == []
