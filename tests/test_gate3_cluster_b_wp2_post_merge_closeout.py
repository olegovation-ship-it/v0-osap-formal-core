from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MERGE = "b6370af53add3fdff1ddb48824dd76ebba3aaa32"

def module(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    loaded = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(loaded)
    return loaded

def test_wp2_post_merge_records_and_successor_ledger_validate():
    verify = module("wp2_pm_verify", "scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py")
    assert verify.validate_records() == []
    assert verify.verify_ledger() == []

def test_wp2_post_merge_builder_ledger_is_current():
    proc = subprocess.run(
        [sys.executable, "scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py", "--check"],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr

def test_canonical_wp2_ledger_remains_byte_exact_at_merge():
    revision = f"{MERGE}:release/v1.4.0/GATE3_CLUSTER_B_WP2_SHA256SUMS.txt"
    available = subprocess.run(
        ["git", "cat-file", "-e", revision], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0
    if not available:
        pytest.skip("shallow checkout omits the exact WP2 merge baseline")
    expected = subprocess.run(
        ["git", "show", revision], cwd=ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True,
    ).stdout
    assert (ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP2_SHA256SUMS.txt").read_bytes() == expected

def test_wp2_closeout_has_no_release_authorization():
    verify = module("wp2_pm_verify_nonclaims", "scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py")
    closeout = verify.load("release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json")
    assert all(value is False for value in closeout["release_actions"].values())
    assert closeout["proof_or_new_runtime_semantics_added"] is False
