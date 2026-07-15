from __future__ import annotations

import argparse
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

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)

def require_text(path: str, *needles: str) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    for needle in needles:
        require(needle in text, f"{path}: missing {needle!r}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-tags", action="store_true")
    args = parser.parse_args()

    evidence = read_json(ROOT / EVIDENCE_PATH)
    artifact_evidence = read_json(
        ROOT / "artifacts/v1_3_0_zenodo_publication_evidence.json"
    )
    record = read_json(ROOT / RECORD_PATH)
    manifest = read_json(ROOT / MANIFEST_PATH)

    require(evidence == artifact_evidence, "duplicated evidence objects differ")
    z = evidence["zenodo_record"]
    require(z["record_id"] == ZENODO_RECORD_ID, "Zenodo record ID mismatch")
    require(z["doi"] == ZENODO_DOI, "Zenodo DOI mismatch")
    require(z["record_url"] == ZENODO_URL, "Zenodo record URL mismatch")
    require(z["title"] == ZENODO_TITLE, "Zenodo title mismatch")
    require(z["publication_date"] == ZENODO_PUBLICATION_DATE, "publication date mismatch")
    require(z["resource_type"] == "Software", "resource type mismatch")
    require(z["access_right"] == "Open", "access-right mismatch")
    require(z["archived_file"] == ZENODO_ARCHIVE, "archive filename mismatch")
    require(z["version_display"] == "v1.3.0", "version mismatch")

    require(record["state"] == MACHINE_STATE, "record state mismatch")
    require(record["human_state"] == HUMAN_STATE, "record human state mismatch")
    require(record["zenodo_publication"]["doi"] == ZENODO_DOI, "record DOI mismatch")
    require(record["zenodo_publication"]["record_id"] == ZENODO_RECORD_ID, "record ID mismatch")

    for rel in FROZEN_PREDECESSORS:
        expected = record["frozen_predecessor_artifacts_sha256"][rel]
        require(sha256_file(ROOT / rel) == expected, f"historical artifact changed: {rel}")

    for rel, expected in manifest["files"].items():
        require((ROOT / rel).is_file(), f"manifest file missing: {rel}")
        require(sha256_file(ROOT / rel) == expected, f"manifest hash mismatch: {rel}")

    require_text(
        "CITATION.cff",
        f'doi: "{ZENODO_DOI}"',
        f'title: "{ZENODO_TITLE}"',
        'version: "1.3.0"',
        'date-released: "2026-07-13"',
        'repository-artifact: "https://github.com/olegovation-ship-it/v0-osap-formal-core/releases/tag/v1.3.0"',
    )
    require_text(
        "README.md",
        ZENODO_DOI,
        ZENODO_TITLE,
        HUMAN_STATE,
        IMMUTABLE_DOI,
    )
    require_text("CHANGELOG.md", ZENODO_DOI, HUMAN_STATE, IMMUTABLE_DOI)
    require_text("docs/status_and_nonclaims.md", ZENODO_DOI, HUMAN_STATE, IMMUTABLE_DOI)

    require(record["immutable_history"]["tag"] == IMMUTABLE_TAG, "historical tag mismatch")
    require(
        record["immutable_history"]["target_commit"] == IMMUTABLE_TARGET,
        "historical target mismatch",
    )
    require(record["immutable_history"]["doi"] == IMMUTABLE_DOI, "historical DOI mismatch")
    require(record["release_actions"]["zenodo_version_published"] is True, "publication not closed")
    require(record["release_actions"]["version_doi_finalized"] is True, "DOI not finalized")
    require(record["release_actions"]["historical_doi_mutated"] is False, "historical DOI mutation")
    require(record["release_actions"]["stable_tag_moved"] is False, "stable tag moved")

    if args.require_tags:
        require(tag_target(FINAL_TAG) == FINAL_TARGET, "stable tag target mismatch")
        require(tag_object_type(FINAL_TAG) == "tag", "stable tag is not annotated")
        require(tag_target(IMMUTABLE_TAG) == IMMUTABLE_TARGET, "historical tag target mismatch")

    print(
        "PASS: V0 OSAP v1.3.0 Zenodo publication evidence is closed, "
        "the version DOI is finalized, and predecessor history is preserved."
    )

if __name__ == "__main__":
    main()
