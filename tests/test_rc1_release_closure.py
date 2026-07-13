from __future__ import annotations

from scripts.rc1_release_closure_lib import (
    CLOSURE_MERGE_COMMIT,
    expected_theorem_ids,
    forbidden_release_commands,
    read_json,
    repository_root,
    sha256_file,
)

ROOT = repository_root()
AUTHORIZED_STATE = "RC1_TAG_AUTHORIZED_TAG_NOT_CREATED_PRERELEASE_NOT_CREATED"


def test_rc1_expected_theorem_range_is_exact() -> None:
    ids = expected_theorem_ids()
    assert len(ids) == 36
    assert ids[0] == "T121"
    assert ids[-1] == "T156"


def test_rc1_tag_preparation_record_is_authorized_but_nonreleasing() -> None:
    record = read_json(ROOT / "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json")
    assert record["state"] == AUTHORIZED_STATE
    assert record["tag_target_commit"] == CLOSURE_MERGE_COMMIT
    assert record["conditional_theorems"] == ["T140", "T150", "T156"]
    assert record["release_actions"]["tag_target_authorized"] is True
    assert record["release_actions"]["rc1_tag_created"] is False
    assert record["release_actions"]["github_prerelease_created"] is False
    assert record["release_actions"]["final_tag_created"] is False
    assert record["release_actions"]["zenodo_version_created"] is False
    assert record["release_actions"]["doi_changed"] is False


def test_rc1_closure_workflow_contains_no_release_command() -> None:
    workflow = (ROOT / ".github/workflows/rc1-release-closure.yml").read_text(encoding="utf-8")
    assert forbidden_release_commands(workflow) == []
    assert "python -m pytest -q" in workflow
    assert "fetch-depth: 0" in workflow


def test_rc1_closure_manifest_hashes_replay() -> None:
    manifest = read_json(ROOT / "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json")
    assert manifest["state"] == AUTHORIZED_STATE
    assert manifest["tag_target_commit"] == CLOSURE_MERGE_COMMIT
    for rel_path, expected_hash in manifest["files"].items():
        assert sha256_file(ROOT / rel_path) == expected_hash
