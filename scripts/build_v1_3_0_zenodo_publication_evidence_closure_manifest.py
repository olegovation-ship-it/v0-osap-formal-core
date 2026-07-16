from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from v1_3_0_zenodo_publication_evidence_closure_lib import (
    EVIDENCE_PATH,
    FINAL_RELEASE_EVIDENCE_MERGE_COMMIT,
    FINAL_TAG,
    FINAL_TARGET,
    FROZEN_PREDECESSORS,
    HUMAN_STATE,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TARGET,
    MACHINE_STATE,
    MANIFEST_PATH,
    RECORD_PATH,
    REPOSITORY,
    ZENODO_DOI,
    ZENODO_RECORD_ID,
    ZENODO_TITLE,
    ZENODO_URL,
    read_json,
    repository_root,
    sha256_file,
    write_json,
)

ROOT = repository_root()
HISTORICAL_SNAPSHOT = "53dcd231aa7d5208a2360d737f01bc2e95e9450b"
POST_MERGE_RECORD = (
    ROOT
    / "release/v1.3.0/"
    "V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json"
)
POST_MERGE_MACHINE_STATE = (
    "POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED_MAIN_DEVELOPMENT_SYNCHRONIZED_"
    "ZENODO_LIFECYCLE_REPLAY_COMPATIBLE_RELEASE_IMMUTABLE"
)
FILES = [
    "README.md",
    "CHANGELOG.md",
    "docs/status_and_nonclaims.md",
    "pyproject.toml",
    "CITATION.cff",
    "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE.json",
    "artifacts/v1_3_0_zenodo_publication_evidence.json",
    "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_RECORD.json",
    (
        "release/v1.3.0/"
        "V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_AND_DOI_FINALIZATION_REPORT.md"
    ),
    (
        "release/v1.3.0/"
        "V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_ACCEPTANCE_GATES.md"
    ),
    "scripts/v1_3_0_zenodo_publication_evidence_closure_lib.py",
    "scripts/build_v1_3_0_zenodo_publication_evidence_closure_manifest.py",
    "scripts/verify_v1_3_0_zenodo_publication_evidence_closure.py",
    "tests/test_v1_3_0_zenodo_publication_evidence_closure.py",
    ".github/workflows/v1-3-0-zenodo-publication-evidence-closure.yml",
    *FROZEN_PREDECESSORS,
]


def historical_blob(rel: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{HISTORICAL_SNAPSHOT}:{rel}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def post_merge_replay_mode() -> bool:
    if not POST_MERGE_RECORD.is_file():
        return False

    record = read_json(POST_MERGE_RECORD)
    if record["state"] != POST_MERGE_MACHINE_STATE:
        raise SystemExit("ERROR: unrecognized post-merge archival-closeout state")
    if (
        record["merge_closeout"]["merge_commit"] != HISTORICAL_SNAPSHOT
        or record["release_state"]["stable_tag_peeled_target"] != FINAL_TARGET
        or record["release_state"]["zenodo_version_doi"] != ZENODO_DOI
        or record["release_state"]["release_immutable"] is not True
    ):
        raise SystemExit("ERROR: post-merge archival-closeout evidence mismatch")
    if not all(value is False for value in record["non_actions"].values()):
        raise SystemExit("ERROR: post-merge record contains a forbidden release action")
    return True


def build_current_manifest() -> None:
    missing = [rel for rel in FILES if not (ROOT / rel).is_file()]
    if missing:
        raise SystemExit("ERROR: missing manifest inputs: " + ", ".join(missing))

    evidence = read_json(ROOT / EVIDENCE_PATH)
    record = read_json(ROOT / RECORD_PATH)
    manifest = {
        "artifact_id": (
            "V0_OSAP_V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_MANIFEST"
        ),
        "version": "0.1",
        "date": "2026-07-14",
        "state": MACHINE_STATE,
        "human_state": HUMAN_STATE,
        "repository": REPOSITORY,
        "final_release_evidence_merge_commit": (
            FINAL_RELEASE_EVIDENCE_MERGE_COMMIT
        ),
        "stable_tag": FINAL_TAG,
        "exact_stable_target": FINAL_TARGET,
        "zenodo": {
            "record_id": ZENODO_RECORD_ID,
            "doi": ZENODO_DOI,
            "url": ZENODO_URL,
            "title": ZENODO_TITLE,
        },
        "immutable_history": {
            "tag": IMMUTABLE_TAG,
            "target_commit": IMMUTABLE_TARGET,
            "doi": IMMUTABLE_DOI,
        },
        "publication_evidence": evidence["zenodo_record"],
        "frozen_predecessor_artifacts_sha256": record[
            "frozen_predecessor_artifacts_sha256"
        ],
        "files": {rel: sha256_file(ROOT / rel) for rel in FILES},
        "release_actions": record["release_actions"],
        "claim_boundary": record["claim_boundary"],
    }
    write_json(ROOT / MANIFEST_PATH, manifest)
    print(
        "PASS: v1.3.0 Zenodo publication-evidence closure manifest generated "
        f"with {len(FILES)} hashed files."
    )


def replay_frozen_manifest() -> None:
    historical = historical_blob(MANIFEST_PATH.as_posix())
    current_path = ROOT / MANIFEST_PATH
    if not current_path.is_file():
        raise SystemExit("ERROR: frozen Zenodo closure manifest is missing")
    if current_path.read_bytes() != historical:
        raise SystemExit(
            "ERROR: frozen Zenodo closure manifest differs from the "
            f"{HISTORICAL_SNAPSHOT} snapshot"
        )

    manifest = json.loads(historical.decode("utf-8"))
    if (
        manifest["state"] != MACHINE_STATE
        or manifest["exact_stable_target"] != FINAL_TARGET
        or manifest["zenodo"]["doi"] != ZENODO_DOI
    ):
        raise SystemExit("ERROR: frozen Zenodo closure manifest identity mismatch")

    digest = hashlib.sha256(historical).hexdigest()
    print(
        "PASS: frozen v1.3.0 Zenodo publication-evidence manifest replayed "
        f"byte-for-byte from {HISTORICAL_SNAPSHOT}; sha256={digest}; "
        "no current lifecycle surface was rehashed or rewritten."
    )


def main() -> int:
    if post_merge_replay_mode():
        replay_frozen_manifest()
    else:
        build_current_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
