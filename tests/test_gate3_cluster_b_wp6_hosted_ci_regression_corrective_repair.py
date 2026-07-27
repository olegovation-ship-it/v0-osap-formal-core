from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_REGRESSION_CORRECTIVE_REPAIR_MANIFEST.json"
RECORD = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP6_HOSTED_CI_REGRESSION_CORRECTIVE_REPAIR_RECORD.json"
VERIFIER = ROOT / "release/v1.4.0/tools/verify_wp6_hosted_ci_regression_corrective_repair.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


def test_wp6_hosted_ci_regression_corrective_repair_surface():
    result = run(sys.executable, str(VERIFIER), "--mode", "auto")
    assert result.returncode == 0, result.stdout + result.stderr


def test_wp6_hosted_ci_regression_corrective_repair_firewall():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert manifest["version"] == "0.3"
    assert manifest["changed_path_count"] == 20
    assert manifest["controlled_modified_path_count"] == 14
    assert manifest["additive_path_count"] == 6
    assert manifest["ledger_entry_count"] == 19
    assert record["status"] == "PREPARED_OUTSIDE_REPOSITORY"
    assert not any(record["authorization_firewall"].values())
    assert record["repair_policy"]["frozen_ledgers_rewritten"] is False
    assert record["repair_policy"]["historical_records_rewritten"] is False
