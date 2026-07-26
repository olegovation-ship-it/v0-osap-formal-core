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

FROZEN_LEDGER_ANCHOR = "ba32d8e855a79461fdcda14740acab86aafcb17a"
REPAIR_STEM = (
    "GATE3_CLUSTER_B_WP6_POST_MERGE_PUSH_CONTEXT_COMPATIBILITY_"
    "AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR"
)
REPAIR_MANIFEST = (
    ROOT / f"release/v1.4.0/{REPAIR_STEM}_MANIFEST.json"
)
REPAIR_LEDGER = (
    ROOT / f"release/v1.4.0/{REPAIR_STEM}_SHA256SUMS.txt"
)


def _repair_ledger_entries() -> dict[str, str]:
    entries: dict[str, str] = {}

    for line in REPAIR_LEDGER.read_text(
        encoding="utf-8"
    ).splitlines():
        if not line.strip():
            continue
        digest_value, relative = line.split("  ", 1)
        entries[relative] = digest_value

    return entries


def successor_overlay_attestation() -> dict[str, str] | None:
    try:
        if not REPAIR_MANIFEST.is_file():
            return None
        if not REPAIR_LEDGER.is_file():
            return None

        manifest = json.loads(
            REPAIR_MANIFEST.read_text(encoding="utf-8")
        )

        if manifest.get(
            "frozen_ledger_anchor_commit"
        ) != FROZEN_LEDGER_ANCHOR:
            return None

        controlled = set(
            manifest.get("controlled_modified_paths", [])
        )
        additive = set(manifest.get("additive_paths", []))
        expected_paths = controlled | additive

        if manifest.get("changed_path_count") != len(expected_paths):
            return None

        ledger_relative = manifest.get("ledger_path")

        if ledger_relative != REPAIR_LEDGER.relative_to(
            ROOT
        ).as_posix():
            return None

        status = subprocess.run(
            [
                "git",
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if status.returncode:
            return None

        status_lines = status.stdout.splitlines()

        if any(
            len(line) < 4 or " -> " in line
            for line in status_lines
        ):
            return None

        working_paths = {
            line[3:]
            for line in status_lines
            if line
        }

        if working_paths:
            actual_paths = working_paths
        else:
            committed = subprocess.run(
                [
                    "git",
                    "diff",
                    "--name-only",
                    "--no-renames",
                    FROZEN_LEDGER_ANCHOR + "..HEAD",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            if committed.returncode:
                return None

            actual_paths = {
                line
                for line in committed.stdout.splitlines()
                if line
            }

        if actual_paths != expected_paths:
            return None

        entries = _repair_ledger_entries()

        if len(entries) != len(expected_paths) - 1:
            return None

        for relative in expected_paths - {ledger_relative}:
            path = ROOT / relative

            if not path.is_file():
                return None

            actual = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()

            if entries.get(relative) != actual:
                return None

        return entries

    except Exception:
        return None


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

    repair = successor_overlay_attestation() or {}

    for rel, expected in manifest["files"].items():
        path = ROOT / rel
        assert path.is_file(), rel
        actual = sha256(path)
        assert actual == expected or repair.get(rel) == actual, rel

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
