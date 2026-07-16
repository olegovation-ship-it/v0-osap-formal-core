from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from v1_3_0_zenodo_publication_evidence_closure_lib import (
    EVIDENCE_PATH,
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
    ZENODO_ARCHIVE,
    ZENODO_DOI,
    ZENODO_PUBLICATION_DATE,
    ZENODO_RECORD_ID,
    ZENODO_TITLE,
    ZENODO_URL,
    read_json,
    repository_root,
    sha256_file,
    tag_object_type,
    tag_target,
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
POST_MERGE_MARKERS = (
    "POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED",
    "MAIN_DEVELOPMENT_SYNCHRONIZED",
    "ZENODO_LIFECYCLE_REPLAY_COMPATIBLE",
    "RELEASE_IMMUTABLE",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def historical_blob(rel: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{HISTORICAL_SNAPSHOT}:{rel}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def historical_text(rel: str) -> str:
    return historical_blob(rel).decode("utf-8")


def historical_sha256(rel: str) -> str:
    return hashlib.sha256(historical_blob(rel)).hexdigest()


def require_text(path: str, *needles: str) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    for needle in needles:
        require(needle in text, f"{path}: missing {needle!r}")


def post_merge_mode() -> bool:
    return POST_MERGE_RECORD.is_file()


def verify_post_merge_record() -> dict:
    record = read_json(POST_MERGE_RECORD)
    require(
        record["state"] == POST_MERGE_MACHINE_STATE,
        "post-merge archival-closeout state mismatch",
    )
    require(
        record["merge_closeout"]["merge_commit"] == HISTORICAL_SNAPSHOT,
        "post-merge synchronization baseline mismatch",
    )
    require(
        record["release_state"]["stable_tag_peeled_target"] == FINAL_TARGET,
        "post-merge stable target mismatch",
    )
    require(
        record["release_state"]["zenodo_version_doi"] == ZENODO_DOI,
        "post-merge Zenodo DOI mismatch",
    )
    require(
        record["immutable_history"]["doi"] == IMMUTABLE_DOI,
        "post-merge historical DOI mismatch",
    )
    require(
        record["release_state"]["release_immutable"] is True,
        "post-merge release is not recorded immutable",
    )
    require(
        all(value is False for value in record["non_actions"].values()),
        "post-merge record contains a forbidden release action",
    )
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-tags", action="store_true")
    args = parser.parse_args()

    replay_mode = post_merge_mode()
    post_merge = verify_post_merge_record() if replay_mode else None

    if replay_mode:
        for rel in (
            EVIDENCE_PATH.as_posix(),
            "artifacts/v1_3_0_zenodo_publication_evidence.json",
            RECORD_PATH.as_posix(),
            MANIFEST_PATH.as_posix(),
        ):
            require(
                (ROOT / rel).read_bytes() == historical_blob(rel),
                f"frozen Zenodo artifact mutated: {rel}",
            )

        evidence = json.loads(historical_blob(EVIDENCE_PATH.as_posix()))
        artifact_evidence = json.loads(
            historical_blob(
                "artifacts/v1_3_0_zenodo_publication_evidence.json"
            )
        )
        record = json.loads(historical_blob(RECORD_PATH.as_posix()))
        manifest = json.loads(historical_blob(MANIFEST_PATH.as_posix()))
    else:
        evidence = read_json(ROOT / EVIDENCE_PATH)
        artifact_evidence = read_json(
            ROOT / "artifacts/v1_3_0_zenodo_publication_evidence.json"
        )
        record = read_json(ROOT / RECORD_PATH)
        manifest = read_json(ROOT / MANIFEST_PATH)

    require(evidence == artifact_evidence, "duplicated evidence objects differ")
    zenodo = evidence["zenodo_record"]
    require(zenodo["record_id"] == ZENODO_RECORD_ID, "Zenodo record ID mismatch")
    require(zenodo["doi"] == ZENODO_DOI, "Zenodo DOI mismatch")
    require(zenodo["record_url"] == ZENODO_URL, "Zenodo record URL mismatch")
    require(zenodo["title"] == ZENODO_TITLE, "Zenodo title mismatch")
    require(
        zenodo["publication_date"] == ZENODO_PUBLICATION_DATE,
        "publication date mismatch",
    )
    require(zenodo["resource_type"] == "Software", "resource type mismatch")
    require(zenodo["access_right"] == "Open", "access-right mismatch")
    require(zenodo["archived_file"] == ZENODO_ARCHIVE, "archive filename mismatch")
    require(zenodo["version_display"] == "v1.3.0", "version mismatch")

    require(record["state"] == MACHINE_STATE, "record state mismatch")
    require(record["human_state"] == HUMAN_STATE, "record human state mismatch")
    require(
        record["zenodo_publication"]["doi"] == ZENODO_DOI,
        "record DOI mismatch",
    )
    require(
        record["zenodo_publication"]["record_id"] == ZENODO_RECORD_ID,
        "record ID mismatch",
    )

    for rel in FROZEN_PREDECESSORS:
        expected = record["frozen_predecessor_artifacts_sha256"][rel]
        require(
            sha256_file(ROOT / rel) == expected,
            f"historical artifact changed: {rel}",
        )
        if replay_mode:
            require(
                historical_sha256(rel) == expected,
                f"historical snapshot predecessor mismatch: {rel}",
            )

    if replay_mode:
        require(
            (ROOT / MANIFEST_PATH).read_bytes()
            == historical_blob(MANIFEST_PATH.as_posix()),
            "frozen Zenodo closure manifest changed",
        )
        for rel, expected in manifest["files"].items():
            require(
                historical_sha256(rel) == expected,
                f"snapshot manifest replay mismatch: {rel}",
            )

        for rel in (
            EVIDENCE_PATH.as_posix(),
            "artifacts/v1_3_0_zenodo_publication_evidence.json",
            RECORD_PATH.as_posix(),
            MANIFEST_PATH.as_posix(),
            "CITATION.cff",
            "pyproject.toml",
            *FROZEN_PREDECESSORS,
        ):
            require(
                (ROOT / rel).read_bytes() == historical_blob(rel),
                f"immutable publication artifact changed after closeout: {rel}",
            )

        for rel in (
            "README.md",
            "CHANGELOG.md",
            "docs/status_and_nonclaims.md",
        ):
            historical = historical_text(rel)
            require(
                HUMAN_STATE in historical
                and ZENODO_DOI in historical
                and IMMUTABLE_DOI in historical,
                f"historical publication state absent from snapshot {rel}",
            )

        for rel in (
            "README.md",
            "CHANGELOG.md",
            "docs/status_and_nonclaims.md",
        ):
            current = (ROOT / rel).read_text(encoding="utf-8")
            require(
                all(marker in current for marker in POST_MERGE_MARKERS),
                f"post-merge successor state incomplete in {rel}",
            )
            require(
                ZENODO_DOI in current and IMMUTABLE_DOI in current,
                f"publication DOI boundary absent from current {rel}",
            )

        for rel in ("README.md", "docs/status_and_nonclaims.md"):
            current = (ROOT / rel).read_text(encoding="utf-8")
            require(
                FINAL_TARGET in current,
                f"stable tag target absent from current {rel}",
            )
            require(
                all(theorem in current for theorem in ("T140", "T150", "T156")),
                f"conditional theorem boundary absent from current {rel}",
            )

        require(
            post_merge["candidate_scope"]["checker_component_version"]
            == "0.7.0.dev1",
            "checker component changed",
        )
        require(
            post_merge["candidate_scope"]["conditional_theorems"]
            == ["T140", "T150", "T156"],
            "conditional theorem ledger changed",
        )
    else:
        for rel, expected in manifest["files"].items():
            require((ROOT / rel).is_file(), f"manifest file missing: {rel}")
            require(
                sha256_file(ROOT / rel) == expected,
                f"manifest hash mismatch: {rel}",
            )

        require_text(
            "README.md",
            ZENODO_DOI,
            ZENODO_TITLE,
            HUMAN_STATE,
            IMMUTABLE_DOI,
        )
        require_text("CHANGELOG.md", ZENODO_DOI, HUMAN_STATE, IMMUTABLE_DOI)
        require_text(
            "docs/status_and_nonclaims.md",
            ZENODO_DOI,
            HUMAN_STATE,
            IMMUTABLE_DOI,
        )

    require_text(
        "CITATION.cff",
        f'doi: "{ZENODO_DOI}"',
        f'title: "{ZENODO_TITLE}"',
        'version: "1.3.0"',
        'date-released: "2026-07-13"',
        (
            'repository-artifact: "https://github.com/'
            'olegovation-ship-it/v0-osap-formal-core/releases/tag/v1.3.0"'
        ),
    )

    require(
        record["immutable_history"]["tag"] == IMMUTABLE_TAG,
        "historical tag mismatch",
    )
    require(
        record["immutable_history"]["target_commit"] == IMMUTABLE_TARGET,
        "historical target mismatch",
    )
    require(
        record["immutable_history"]["doi"] == IMMUTABLE_DOI,
        "historical DOI mismatch",
    )
    require(
        record["release_actions"]["zenodo_version_published"] is True,
        "publication not closed",
    )
    require(
        record["release_actions"]["version_doi_finalized"] is True,
        "DOI not finalized",
    )
    require(
        record["release_actions"]["historical_doi_mutated"] is False,
        "historical DOI mutation",
    )
    require(
        record["release_actions"]["stable_tag_moved"] is False,
        "stable tag moved",
    )

    if args.require_tags:
        require(
            tag_target(FINAL_TAG) == FINAL_TARGET,
            "stable tag target mismatch",
        )
        require(
            tag_object_type(FINAL_TAG) == "tag",
            "stable tag is not annotated",
        )
        require(
            tag_target(IMMUTABLE_TAG) == IMMUTABLE_TARGET,
            "historical tag target mismatch",
        )

    if replay_mode:
        print(
            "PASS: V0 OSAP v1.3.0 Zenodo publication evidence and manifest "
            f"replayed byte-for-byte from {HISTORICAL_SNAPSHOT}; guarded "
            "post-merge successor surfaces accepted without rehashing history."
        )
    else:
        print(
            "PASS: V0 OSAP v1.3.0 Zenodo publication evidence is closed, "
            "the version DOI is finalized, and predecessor history is preserved."
        )


if __name__ == "__main__":
    main()
