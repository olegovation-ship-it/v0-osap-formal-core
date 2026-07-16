from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT
    / "release/v1.3.0/"
    "V1_3_0_POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_AND_FROZEN_ZENODO_"
    "MANIFEST_COMPATIBILITY_RECORD.json"
)


def test_publication_replay_compatibility_record() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    assert len(record["observed_downstream_failures"]) == 3
    assert record["repair"]["acceptance_gates_weakened"] is False
    assert record["repair"]["historical_manifest_rewritten"] is False
    assert record["repair"]["zenodo_builder_mode_after_closeout"] == (
        "HISTORICAL_SNAPSHOT_REPLAY_NO_REWRITE"
    )
    assert record["historical_snapshots"][
        "zenodo_publication_and_post_merge_baseline"
    ] == "53dcd231aa7d5208a2360d737f01bc2e95e9450b"
    assert all(value is False for value in record["non_actions"].values())


def test_compatibility_workflow_is_validation_only() -> None:
    workflow = (
        ROOT
        / ".github/workflows/"
        "v1-3-0-post-merge-publication-lifecycle-replay-compatibility.yml"
    ).read_text(encoding="utf-8")
    for command in (
        "verify_v1_3_0_final_release_evidence_closure.py --require-tags",
        "build_v1_3_0_zenodo_publication_evidence_closure_manifest.py",
        "verify_v1_3_0_zenodo_publication_evidence_closure.py --require-tags",
        "verify_v1_3_0_post_zenodo_historical_replay_compatibility.py",
        "verify_v1_3_0_post_merge_publication_lifecycle_replay_compatibility.py",
    ):
        assert command in workflow
    for forbidden in (
        "git tag -a",
        "gh release create",
        "zenodo upload",
        "--execute",
    ):
        assert forbidden not in workflow
