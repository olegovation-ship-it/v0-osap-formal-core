from __future__ import annotations

import hashlib
import subprocess

from scripts.rc1_evidence_closure_lib import (
    CANDIDATE_TAG,
    CANDIDATE_TARGET,
    EXPECTED_PUBLISHED_AT,
    EXPECTED_RELEASE_NAME,
    EXPECTED_RELEASE_URL,
    FINAL_TAG,
    HUMAN_STATE,
    MACHINE_STATE,
    MANIFEST_PATH,
    RECORD_PATH,
    EVIDENCE_PATH,
    local_tag_exists,
    local_tag_target,
    read_json,
    repository_root,
    sha256_file,
)

ROOT = repository_root()
HISTORICAL_SNAPSHOT_COMMIT = "13bf095688bcabd5b090f188e9bd28a16237edeb"


def historical_sha256(rel_path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{HISTORICAL_SNAPSHOT_COMMIT}:{rel_path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return hashlib.sha256(result.stdout).hexdigest()


def test_recorded_github_prerelease_evidence_is_exact() -> None:
    evidence = read_json(ROOT / EVIDENCE_PATH)
    release = evidence["release"]
    assert evidence["authorized_target_commit"] == CANDIDATE_TARGET
    assert release == {
        "isDraft": False,
        "isPrerelease": True,
        "name": EXPECTED_RELEASE_NAME,
        "publishedAt": EXPECTED_PUBLISHED_AT,
        "tagName": CANDIDATE_TAG,
        "url": EXPECTED_RELEASE_URL,
    }


def test_evidence_closure_record_and_release_actions() -> None:
    record = read_json(ROOT / RECORD_PATH)
    assert record["state"] == MACHINE_STATE
    assert record["human_state"] == HUMAN_STATE
    assert record["tag_evidence"]["target_commit"] == CANDIDATE_TARGET
    assert record["release_actions"]["rc1_tag_created"] is True
    assert record["release_actions"]["github_prerelease_created"] is True
    assert record["release_actions"]["final_tag_created"] is False
    assert record["release_actions"]["zenodo_version_created"] is False
    assert record["release_actions"]["doi_changed"] is False


def test_local_candidate_tag_target_when_tags_are_available() -> None:
    if local_tag_exists(CANDIDATE_TAG):
        assert local_tag_target(CANDIDATE_TAG) == CANDIDATE_TARGET
    if local_tag_exists(FINAL_TAG):
        assert local_tag_target(FINAL_TAG) == HISTORICAL_SNAPSHOT_COMMIT


def test_evidence_closure_manifest_hashes_replay() -> None:
    manifest = read_json(ROOT / MANIFEST_PATH)
    assert manifest["state"] == MACHINE_STATE
    for rel_path, expected_hash in manifest["files"].items():
        assert historical_sha256(rel_path) == expected_hash
