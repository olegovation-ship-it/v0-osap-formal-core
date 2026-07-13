from __future__ import annotations

import argparse

from rc1_release_closure_lib import (
    AUDIT_MERGE_COMMIT,
    CANDIDATE_TAG,
    CLOSURE_MERGE_COMMIT,
    FINAL_TAG,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TAG_TARGET,
    commit_exists,
    expected_theorem_ids,
    forbidden_release_commands,
    git,
    is_ancestor,
    read_json,
    repository_root,
    sha256_file,
    tag_exists,
)
from rc1_evidence_closure_lib import HUMAN_STATE, RECORD_PATH

ROOT = repository_root()
AUTHORIZED_STATE = "RC1_TAG_AUTHORIZED_TAG_NOT_CREATED_PRERELEASE_NOT_CREATED"
CLOSURE_STATE = "RC1_CLOSURE_READY_CI_PENDING_TAG_NOT_CREATED"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"RC1 release-closure verification failed: {message}")


def no_external_release_action(actions: dict[str, bool]) -> bool:
    allowed_true = {"tag_target_authorized"}
    return all((not value) or key in allowed_true for key, value in actions.items())


def verify(require_tags: bool = False) -> None:
    require(commit_exists(AUDIT_MERGE_COMMIT), "audit merge commit is unavailable")
    require(is_ancestor(AUDIT_MERGE_COMMIT), "audit merge commit is not an ancestor of HEAD")
    require(commit_exists(CLOSURE_MERGE_COMMIT), "closure merge commit is unavailable")
    require(is_ancestor(CLOSURE_MERGE_COMMIT), "closure merge commit is not an ancestor of HEAD")
    require(not tag_exists(FINAL_TAG), f"final tag {FINAL_TAG} exists prematurely")

    evidence_mode = (ROOT / RECORD_PATH).is_file()
    candidate_present = tag_exists(CANDIDATE_TAG)
    if evidence_mode:
        if require_tags:
            require(candidate_present, f"candidate tag {CANDIDATE_TAG} is unavailable")
        if candidate_present:
            target = git("rev-list", "-n", "1", CANDIDATE_TAG).stdout.strip()
            require(target == CLOSURE_MERGE_COMMIT, "candidate RC1 tag target changed")
    else:
        require(not candidate_present, f"candidate tag {CANDIDATE_TAG} already exists")

    historical_tag_present = tag_exists(IMMUTABLE_TAG)
    if require_tags:
        require(historical_tag_present, f"historical tag {IMMUTABLE_TAG} is unavailable")
    if historical_tag_present:
        target = git("rev-list", "-n", "1", IMMUTABLE_TAG).stdout.strip()
        require(target == IMMUTABLE_TAG_TARGET, "immutable v1.2.0 tag target changed")

    tag_record = read_json(ROOT / "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json")
    require(tag_record["state"] in {CLOSURE_STATE, AUTHORIZED_STATE}, "tag-record state mismatch")
    require(tag_record["audit_merge_commit"] == AUDIT_MERGE_COMMIT, "audit baseline mismatch")
    require(tag_record["candidate_tag_name"] == CANDIDATE_TAG, "candidate tag name mismatch")
    require(tag_record["immutable_tag_target_commit"] == IMMUTABLE_TAG_TARGET, "immutable target mismatch")
    require(tag_record["immutable_doi"] == IMMUTABLE_DOI, "immutable DOI mismatch")
    require(tag_record["conditional_theorems"] == ["T140", "T150", "T156"], "conditional theorem ledger changed")
    require(no_external_release_action(tag_record["release_actions"]), "historical tag-preparation record mutated")
    require(tag_record["tag_target_commit"] == CLOSURE_MERGE_COMMIT, "authorized tag target mismatch")
    require(tag_record["release_actions"]["tag_target_authorized"] is True, "target authorization missing")

    audit_manifest = read_json(ROOT / "release/v1.3.0/RC1_RELEASE_MANIFEST.json")
    require(not any(audit_manifest["release_actions"].values()), "audit manifest records a release action")
    require(audit_manifest["immutable_tag"] == IMMUTABLE_TAG, "audit immutable tag mismatch")
    require(audit_manifest["immutable_doi"] == IMMUTABLE_DOI, "audit immutable DOI mismatch")

    inventory = read_json(ROOT / "release/v1.3.0/RC1_THEOREM_INVENTORY.json")
    records = inventory["records"]
    theorem_ids = [record["theorem_id"] for record in records]
    require(theorem_ids == expected_theorem_ids(), "theorem inventory is not exactly T121-T156")
    require(inventory["record_count"] == 36 == len(records), "theorem record count is not 36")
    require(len(inventory["source_crosswalks"]) == 6, "source crosswalk count is not 6")

    matrix = read_json(ROOT / "release/v1.3.0/RC1_CLAIM_CLASSIFICATION_MATRIX.json")
    conditional_ranges = {
        item["theorem_range"]
        for item in matrix["range_rules"]
        if item["default_claim_class"] == "CONDITIONAL_THEOREM"
    }
    require(conditional_ranges == {"T140", "T150", "T156"}, "conditional claim classes changed")

    manifest_path = ROOT / "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json"
    closure_manifest = read_json(manifest_path)
    require(closure_manifest["state"] in {CLOSURE_STATE, AUTHORIZED_STATE}, "closure manifest state mismatch")
    require(closure_manifest["audit_merge_commit"] == AUDIT_MERGE_COMMIT, "closure audit baseline mismatch")
    require(no_external_release_action(closure_manifest["release_actions"]), "historical closure manifest mutated")
    require(closure_manifest["tag_target_commit"] == CLOSURE_MERGE_COMMIT, "closure target mismatch")

    if evidence_mode:
        closure = read_json(ROOT / RECORD_PATH)
        frozen_hash = closure["frozen_historical_manifests"][
            "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json"
        ]
        require(sha256_file(manifest_path) == frozen_hash, "frozen release-closure manifest changed")
        expected_state_text = HUMAN_STATE
    else:
        for rel_path, expected_hash in closure_manifest["files"].items():
            path = ROOT / rel_path
            require(path.is_file(), f"manifest target missing: {rel_path}")
            require(sha256_file(path) == expected_hash, f"manifest hash mismatch: {rel_path}")
        expected_state_text = (
            "RC1_TAG_AUTHORIZED / TAG_NOT_CREATED / PRERELEASE_NOT_CREATED"
            if tag_record["state"] == AUTHORIZED_STATE
            else "RC1_CLOSURE_READY / CI_PENDING / TAG_NOT_CREATED"
        )

    for rel_path in ["README.md", "CHANGELOG.md", "docs/status_and_nonclaims.md"]:
        require(
            expected_state_text in (ROOT / rel_path).read_text(encoding="utf-8"),
            f"state absent from {rel_path}",
        )

    workflow = (ROOT / ".github/workflows/rc1-release-closure.yml").read_text(encoding="utf-8")
    require("fetch-depth: 0" in workflow, "closure workflow does not fetch full history")
    require("python -m pytest -q" in workflow, "closure workflow does not use module-mode pytest")
    require("verify_rc1_release_closure.py --require-tags" in workflow, "tag-preservation verification missing")
    require("actions/upload-artifact@v4" in workflow, "clean-room evidence upload missing")
    forbidden = forbidden_release_commands(workflow)
    require(not forbidden, "workflow contains release commands: " + ", ".join(forbidden))

    draft = (ROOT / "release/v1.3.0/RC1_TAG_ANNOTATION_DRAFT.txt").read_text(encoding="utf-8")
    require(
        "DRAFT ONLY" in draft and "TAG CREATION IS NOT AUTHORIZED" in draft,
        "historical tag draft lacks its original hold notice",
    )

    if evidence_mode:
        print(
            "PASS: historical RC1 release-closure snapshot preserved after exact-target "
            "tag and GitHub pre-release creation; no final release authorized."
        )
    else:
        print(
            "PASS: V0 OSAP v1.3.0 RC1 release closure preserved; "
            "exact tag target authorization is recorded, no tag created."
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-tags", action="store_true")
    args = parser.parse_args()
    verify(require_tags=args.require_tags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
