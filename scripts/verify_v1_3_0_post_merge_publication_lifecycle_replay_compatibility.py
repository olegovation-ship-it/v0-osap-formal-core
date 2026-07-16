from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release/v1.3.0"
RECORD = (
    RELEASE
    / "V1_3_0_POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_AND_FROZEN_ZENODO_"
    "MANIFEST_COMPATIBILITY_RECORD.json"
)
MANIFEST = (
    RELEASE
    / "V1_3_0_POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_AND_FROZEN_ZENODO_"
    "MANIFEST_COMPATIBILITY_MANIFEST.json"
)
ZENODO_MANIFEST_REL = (
    "release/v1.3.0/"
    "V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_MANIFEST.json"
)
ZENODO_SNAPSHOT = "53dcd231aa7d5208a2360d737f01bc2e95e9450b"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historical_blob(rel: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{ZENODO_SNAPSHOT}:{rel}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def run_checked(*args: str) -> str:
    completed = subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "command failed: "
            + " ".join(args)
            + "\n"
            + completed.stdout
            + completed.stderr
        )
    return completed.stdout


def main() -> int:
    record = load(RECORD)
    manifest = load(MANIFEST)

    assert record["state"] == (
        "POST_MERGE_PUBLICATION_LIFECYCLE_REPLAY_COMPATIBLE_"
        "FROZEN_ZENODO_MANIFEST_REPLAY_PRESERVED"
    )
    assert record["repair"]["acceptance_gates_weakened"] is False
    assert record["repair"]["historical_manifest_rewritten"] is False
    assert all(value is False for value in record["non_actions"].values())

    current_zenodo_manifest = ROOT / ZENODO_MANIFEST_REL
    assert current_zenodo_manifest.read_bytes() == historical_blob(
        ZENODO_MANIFEST_REL
    )

    final_verifier = (
        ROOT / "scripts/verify_v1_3_0_final_release_evidence_closure.py"
    ).read_text(encoding="utf-8")
    zenodo_builder = (
        ROOT
        / "scripts/build_v1_3_0_zenodo_publication_evidence_closure_manifest.py"
    ).read_text(encoding="utf-8")
    zenodo_verifier = (
        ROOT / "scripts/verify_v1_3_0_zenodo_publication_evidence_closure.py"
    ).read_text(encoding="utf-8")

    for token in (
        "POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED",
        "MAIN_DEVELOPMENT_SYNCHRONIZED",
        "ZENODO_LIFECYCLE_REPLAY_COMPATIBLE",
        "RELEASE_IMMUTABLE",
    ):
        assert token in final_verifier
        assert token in zenodo_verifier

    assert "replay_frozen_manifest" in zenodo_builder
    assert ZENODO_SNAPSHOT in zenodo_builder
    assert ZENODO_SNAPSHOT in zenodo_verifier

    run_checked(
        sys.executable,
        "scripts/verify_v1_3_0_final_release_evidence_closure.py",
        "--require-tags",
    )
    run_checked(
        sys.executable,
        "scripts/build_v1_3_0_zenodo_publication_evidence_closure_manifest.py",
    )
    run_checked(
        "git",
        "diff",
        "--exit-code",
        "--",
        ZENODO_MANIFEST_REL,
    )
    run_checked(
        sys.executable,
        "scripts/verify_v1_3_0_zenodo_publication_evidence_closure.py",
        "--require-tags",
    )
    run_checked(
        sys.executable,
        "scripts/verify_v1_3_0_post_zenodo_historical_replay_compatibility.py",
    )

    for rel, expected in manifest["files"].items():
        path = ROOT / rel
        assert path.is_file(), rel
        assert sha256(path) == expected, rel

    print(
        "PASS: final-release evidence, frozen Zenodo publication manifest, "
        "and post-Zenodo lifecycle replay are compatible with the guarded "
        "post-merge closeout; no historical artifact was rewritten."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
