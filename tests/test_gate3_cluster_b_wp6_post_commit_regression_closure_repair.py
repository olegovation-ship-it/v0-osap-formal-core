from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_MANIFEST.json"
RECORD = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_COMMIT_REGRESSION_CLOSURE_REPAIR_RECORD.json"
VERIFIER = ROOT / "release/v1.4.0/tools/verify_wp6_post_commit_regression_closure_repair.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_wp6_post_commit_regression_closure_surface():
    result = run(sys.executable, str(VERIFIER), "--mode", "auto")
    assert result.returncode == 0, result.stdout + result.stderr


def test_wp6_post_commit_regression_closure_authorization_firewall():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert manifest["changed_path_count"] == 12
    assert manifest["controlled_modified_path_count"] == 6
    assert manifest["additive_path_count"] == 6
    assert manifest["ledger_entry_count"] == 11
    assert record["status"] == "PREPARED_UNCOMMITTED"
    assert not any(record["authorization_firewall"].values())
