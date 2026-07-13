from __future__ import annotations

import argparse
from pathlib import Path

from rc1_release_closure_lib import (
    AUDIT_MERGE_COMMIT,
    CANDIDATE_TAG,
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

ROOT = repository_root()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"RC1 release-closure verification failed: {message}")


def verify(require_tags: bool = False) -> None:
    require(commit_exists(AUDIT_MERGE_COMMIT), "audit merge commit is unavailable")
    require(is_ancestor(AUDIT_MERGE_COMMIT), "audit merge commit is not an ancestor of HEAD")

    require(not tag_exists(CANDIDATE_TAG), f"candidate tag {CANDIDATE_TAG} already exists")
    require(not tag_exists(FINAL_TAG), f"final tag {FINAL_TAG} already exists")

    historical_tag_present = tag_exists(IMMUTABLE_TAG)
    if require_tags:
        require(historical_tag_present, f"historical tag {IMMUTABLE_TAG} is unavailable")
    if historical_tag_present:
        target = git("rev-list", "-n", "1", IMMUTABLE_TAG).stdout.strip()
        require(target == IMMUTABLE_TAG_TARGET, "immutable v1.2.0 tag target changed")

    tag_record = read_json(ROOT / "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json")
    require(tag_record["state"] == "RC1_CLOSURE_READY_CI_PENDING_TAG_NOT_CREATED", "tag-record state mismatch")
    require(tag_record["audit_merge_commit"] == AUDIT_MERGE_COMMIT, "audit baseline mismatch")
    require(tag_record["candidate_tag_name"] == CANDIDATE_TAG, "candidate tag name mismatch")
    require(tag_record["tag_target_commit"] is None, "tag target was resolved prematurely")
    require(tag_record["immutable_tag_target_commit"] == IMMUTABLE_TAG_TARGET, "immutable target mismatch")
    require(tag_record["immutable_doi"] == IMMUTABLE_DOI, "immutable DOI mismatch")
    require(tag_record["conditional_theorems"] == ["T140", "T150", "T156"], "conditional theorem ledger changed")
    require(not any(tag_record["release_actions"].values()), "a release action is marked true")

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
    require(closure_manifest["state"] == "RC1_CLOSURE_READY_CI_PENDING_TAG_NOT_CREATED", "closure manifest state mismatch")
    require(closure_manifest["audit_merge_commit"] == AUDIT_MERGE_COMMIT, "closure audit baseline mismatch")
    require(closure_manifest["tag_target_commit"] is None, "closure manifest resolves tag target prematurely")
    require(not any(closure_manifest["release_actions"].values()), "closure manifest records a release action")
    for rel_path, expected_hash in closure_manifest["files"].items():
        path = ROOT / rel_path
        require(path.is_file(), f"manifest target missing: {rel_path}")
        require(sha256_file(path) == expected_hash, f"manifest hash mismatch: {rel_path}")

    expected_state_text = "RC1_CLOSURE_READY / CI_PENDING / TAG_NOT_CREATED"
    for rel_path in ["README.md", "CHANGELOG.md", "docs/status_and_nonclaims.md"]:
        require(expected_state_text in (ROOT / rel_path).read_text(encoding="utf-8"), f"closure state absent from {rel_path}")

    workflow = (ROOT / ".github/workflows/rc1-release-closure.yml").read_text(encoding="utf-8")
    require("fetch-depth: 0" in workflow, "closure workflow does not fetch full history")
    require("python -m pytest -q" in workflow, "closure workflow does not use module-mode pytest")
    require("build_rc1_release_closure_manifest.py" in workflow, "closure manifest replay missing")
    require("verify_rc1_release_closure.py --require-tags" in workflow, "tag-preservation verification missing")
    require("actions/upload-artifact@v4" in workflow, "clean-room evidence upload missing")
    forbidden = forbidden_release_commands(workflow)
    require(not forbidden, "workflow contains release commands: " + ", ".join(forbidden))

    draft = (ROOT / "release/v1.3.0/RC1_TAG_ANNOTATION_DRAFT.txt").read_text(encoding="utf-8")
    require("DRAFT ONLY" in draft and "TAG CREATION IS NOT AUTHORIZED" in draft, "tag draft lacks hold notice")

    print("PASS: V0 OSAP v1.3.0 RC1 release closure and tag preparation verified; no tag authorized.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-tags", action="store_true")
    args = parser.parse_args()
    verify(require_tags=args.require_tags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
