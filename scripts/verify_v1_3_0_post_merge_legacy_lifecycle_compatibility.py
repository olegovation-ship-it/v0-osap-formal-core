from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release/v1.3.0"
RECORD = RELEASE / "V1_3_0_POST_MERGE_LEGACY_LIFECYCLE_GATE_COMPATIBILITY_AND_FROZEN_MANIFEST_REPLAY_RECORD.json"
MANIFEST = RELEASE / "V1_3_0_POST_MERGE_LEGACY_LIFECYCLE_GATE_COMPATIBILITY_AND_FROZEN_MANIFEST_REPLAY_MANIFEST.json"
POST_MERGE_RECORD = RELEASE / "V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json"
ZENODO_RECORD = RELEASE / "V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_RECORD.json"
RC1_RECORD = RELEASE / "RC1_RELEASE_EVIDENCE_CLOSURE_RECORD.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    record = load(RECORD)
    manifest = load(MANIFEST)
    post_merge = load(POST_MERGE_RECORD)
    zenodo = load(ZENODO_RECORD)
    rc1 = load(RC1_RECORD)

    assert record["state"] == (
        "POST_MERGE_LEGACY_LIFECYCLE_COMPATIBILITY_RECORDED_"
        "FROZEN_MANIFEST_REPLAY_PRESERVED"
    )
    assert post_merge["state"].startswith("POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED")
    assert post_merge["release_state"]["stable_tag_peeled_target"] == (
        "13bf095688bcabd5b090f188e9bd28a16237edeb"
    )
    assert post_merge["release_state"]["zenodo_version_doi"] == "10.5281/zenodo.21346728"

    gate_text = (ROOT / "scripts/verify_rc1_gate_audit.py").read_text(encoding="utf-8")
    required_gate_tokens = (
        "POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED",
        "MAIN_DEVELOPMENT_SYNCHRONIZED",
        "ZENODO_LIFECYCLE_REPLAY_COMPATIBLE",
        "RELEASE_IMMUTABLE",
        "post_merge_companion_markers",
        "10.5281/zenodo.21346728",
        "13bf095688bcabd5b090f188e9bd28a16237edeb",
        "0.7.0.dev1",
        "T140",
        "T150",
        "T156",
    )
    for token in required_gate_tokens:
        assert token in gate_text, token

    for rel in ("README.md", "docs/status_and_nonclaims.md"):
        body = (ROOT / rel).read_text(encoding="utf-8")
        for marker in (
            "POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED",
            "MAIN_DEVELOPMENT_SYNCHRONIZED",
            "ZENODO_LIFECYCLE_REPLAY_COMPATIBLE",
            "RELEASE_IMMUTABLE",
        ):
            assert marker in body, (rel, marker)
        assert "10.5281/zenodo.21346728" in body
        assert "10.5281/zenodo.21306969" in body
        assert "T121-T156" in body

    recorded_zenodo = record["frozen_replay"]["zenodo_predecessor_artifacts"]
    assert recorded_zenodo == zenodo["frozen_predecessor_artifacts_sha256"]
    recorded_rc1 = record["frozen_replay"]["rc1_historical_manifests"]
    assert recorded_rc1 == rc1["frozen_historical_manifests"]

    for rel, expected in {**recorded_zenodo, **recorded_rc1}.items():
        path = ROOT / rel
        assert path.is_file(), rel
        assert sha256(path) == expected, rel

    assert all(value is False for value in record["non_actions"].values())
    assert record["repair"]["acceptance_gates_weakened"] is False
    assert record["repair"]["historical_state_rewritten"] is False

    for rel, expected in manifest["files"].items():
        path = ROOT / rel
        assert path.is_file(), rel
        assert sha256(path) == expected, rel

    completed = subprocess.run(
        [sys.executable, "scripts/verify_rc1_gate_audit.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "legacy RC1 gate audit still fails after compatibility repair:\n"
            + completed.stdout
            + completed.stderr
        )

    print(
        "PASS: post-merge legacy lifecycle marker compatibility verified; "
        "eight frozen predecessor/RC1 artifacts replayed byte-for-byte without "
        "weakening release gates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
