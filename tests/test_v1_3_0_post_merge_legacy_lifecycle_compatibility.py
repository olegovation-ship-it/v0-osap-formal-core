from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "release/v1.3.0/V1_3_0_POST_MERGE_LEGACY_LIFECYCLE_GATE_COMPATIBILITY_AND_FROZEN_MANIFEST_REPLAY_RECORD.json"


def test_compatibility_record_preserves_non_actions() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert record["observed_failure"]["workflow_count"] == 9
    assert record["repair"]["acceptance_gates_weakened"] is False
    assert record["repair"]["historical_state_rewritten"] is False
    assert all(value is False for value in record["non_actions"].values())
    assert len(record["frozen_replay"]["zenodo_predecessor_artifacts"]) == 6
    assert len(record["frozen_replay"]["rc1_historical_manifests"]) == 2


def test_compatibility_verifier_executes() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/verify_v1_3_0_post_merge_legacy_lifecycle_compatibility.py",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "eight frozen predecessor/RC1 artifacts" in completed.stdout
