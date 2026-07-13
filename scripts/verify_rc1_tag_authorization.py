from __future__ import annotations

import argparse

from rc1_release_closure_lib import forbidden_release_commands
from rc1_tag_release_lib import (
    AUTHORIZED_STATE,
    CANDIDATE_TAG,
    CLOSURE_MERGE_COMMIT,
    FINAL_TAG,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TAG_TARGET,
    commit_exists,
    git,
    is_ancestor,
    local_tag_exists,
    read_json,
    repository_root,
    sha256_file,
)
from rc1_evidence_closure_lib import HUMAN_STATE, RECORD_PATH, tag_object_type

ROOT = repository_root()
HISTORICAL_SNAPSHOT_COMMIT = "13bf095688bcabd5b090f188e9bd28a16237edeb"


def historical_text(rel_path: str) -> str:
    return git(
        "show",
        f"{HISTORICAL_SNAPSHOT_COMMIT}:{rel_path}",
    ).stdout


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"RC1 tag-authorization verification failed: {message}")


def verify(require_tags: bool = False) -> None:
    require(commit_exists(CLOSURE_MERGE_COMMIT), "authorized closure commit is unavailable")
    require(is_ancestor(CLOSURE_MERGE_COMMIT), "authorized closure commit is not an ancestor of HEAD")
    final_present = local_tag_exists(FINAL_TAG)
    if final_present:
        target = git("rev-list", "-n", "1", FINAL_TAG).stdout.strip()
        require(
            target == HISTORICAL_SNAPSHOT_COMMIT,
            "final tag target mismatch",
        )
        require(
            tag_object_type(FINAL_TAG) == "tag",
            "final tag is not annotated",
        )

    evidence_mode = (ROOT / RECORD_PATH).is_file()
    candidate_present = local_tag_exists(CANDIDATE_TAG)
    if evidence_mode:
        if require_tags:
            require(candidate_present, f"candidate tag {CANDIDATE_TAG} is unavailable")
        if candidate_present:
            target = git("rev-list", "-n", "1", CANDIDATE_TAG).stdout.strip()
            require(target == CLOSURE_MERGE_COMMIT, "candidate tag target mismatch")
            require(tag_object_type(CANDIDATE_TAG) == "tag", "candidate tag is not annotated")
    else:
        require(not candidate_present, f"candidate tag {CANDIDATE_TAG} already exists")

    if require_tags:
        require(local_tag_exists(IMMUTABLE_TAG), f"historical tag {IMMUTABLE_TAG} is unavailable")
    if local_tag_exists(IMMUTABLE_TAG):
        target = git("rev-list", "-n", "1", IMMUTABLE_TAG).stdout.strip()
        require(target == IMMUTABLE_TAG_TARGET, "historical v1.2.0 target changed")

    auth = read_json(ROOT / "release/v1.3.0/RC1_TAG_AUTHORIZATION_RECORD.json")
    prep = read_json(ROOT / "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json")
    metadata = read_json(ROOT / "release/v1.3.0/RC1_GITHUB_PRERELEASE_METADATA.json")
    manifest_path = ROOT / "release/v1.3.0/RC1_TAG_AUTHORIZATION_MANIFEST.json"
    manifest = read_json(manifest_path)

    require(auth["state"] == AUTHORIZED_STATE, "historical authorization record state mismatch")
    require(auth["closure_merge_commit"] == CLOSURE_MERGE_COMMIT, "closure merge mismatch")
    require(auth["authorized_tag_name"] == CANDIDATE_TAG, "authorized tag name mismatch")
    require(auth["authorized_tag_target_commit"] == CLOSURE_MERGE_COMMIT, "authorized target mismatch")
    require(auth["authorization_is_target_specific"] is True, "authorization is not target-specific")
    require(auth["post_merge_ci_evidence"]["overall_status"] == "PASS", "post-merge CI is not recorded PASS")
    require(auth["release_actions"]["tag_target_authorized"] is True, "target authorization is not true")
    require(not auth["release_actions"]["rc1_tag_created"], "historical authorization record was mutated")
    require(not auth["release_actions"]["github_prerelease_created"], "historical authorization record was mutated")
    require(not auth["final_tag_authorized"], "final tag is improperly authorized")
    require(not auth["zenodo_version_authorized"], "Zenodo version is improperly authorized")
    require(not auth["doi_change_authorized"], "DOI change is improperly authorized")

    require(prep["state"] == AUTHORIZED_STATE, "historical tag-preparation state mismatch")
    require(prep["tag_target_commit"] == CLOSURE_MERGE_COMMIT, "tag-preparation target mismatch")
    require(prep["release_actions"]["tag_target_authorized"] is True, "tag-preparation authorization missing")
    for key in [
        "rc1_tag_created",
        "final_tag_created",
        "github_release_created",
        "github_prerelease_created",
        "zenodo_version_created",
        "doi_changed",
    ]:
        require(not prep["release_actions"][key], f"historical preparation record mutated: {key}")

    require(metadata["tag_name"] == CANDIDATE_TAG, "pre-release metadata tag mismatch")
    require(metadata["target_commit"] == CLOSURE_MERGE_COMMIT, "pre-release metadata target mismatch")
    require(metadata["prerelease"] is True and metadata["draft"] is False, "pre-release flags mismatch")
    require(metadata["make_latest"] is False, "RC1 must not be latest stable")
    require(metadata["zenodo_action"] == "NOT_AUTHORIZED", "Zenodo action mismatch")
    require(metadata["doi_action"] == "NOT_AUTHORIZED", "DOI action mismatch")

    tag_message = (ROOT / "release/v1.3.0/RC1_ANNOTATED_TAG_MESSAGE.txt").read_text(encoding="utf-8")
    require(tag_message.startswith("V0 OSAP v1.3.0-rc1\n"), "annotated tag title mismatch")
    require(CLOSURE_MERGE_COMMIT in tag_message, "annotated tag message lacks exact target")
    require("DRAFT ONLY" not in tag_message, "annotated tag message is still marked draft")
    require(IMMUTABLE_DOI in tag_message, "annotated tag message lacks immutable DOI")

    notes = (ROOT / "release/v1.3.0/RC1_GITHUB_PRERELEASE_NOTES.md").read_text(encoding="utf-8")
    require(CLOSURE_MERGE_COMMIT in notes, "pre-release notes lack exact target")
    require("T140, T150, and T156 remain conditional" in notes, "conditionality statement missing")
    require(IMMUTABLE_DOI in notes, "pre-release notes lack immutable DOI")

    if evidence_mode:
        closure = read_json(ROOT / RECORD_PATH)
        frozen_hash = closure["frozen_historical_manifests"][
            "release/v1.3.0/RC1_TAG_AUTHORIZATION_MANIFEST.json"
        ]
        require(sha256_file(manifest_path) == frozen_hash, "frozen tag-authorization manifest changed")
        expected_state = HUMAN_STATE
    else:
        for rel_path, expected_hash in manifest["files"].items():
            path = ROOT / rel_path
            require(path.is_file(), f"authorization-manifest target missing: {rel_path}")
            require(sha256_file(path) == expected_hash, f"authorization-manifest hash mismatch: {rel_path}")
        expected_state = "RC1_TAG_AUTHORIZED / TAG_NOT_CREATED / PRERELEASE_NOT_CREATED"

    require(manifest["authorized_tag_target_commit"] == CLOSURE_MERGE_COMMIT, "manifest target mismatch")

    for rel_path in ["README.md", "CHANGELOG.md", "docs/status_and_nonclaims.md"]:
        body = (
            historical_text(rel_path)
            if evidence_mode
            else (ROOT / rel_path).read_text(encoding="utf-8")
        )
        require(
            expected_state in body,
            f"lifecycle state absent from {rel_path}",
        )

    workflow = (
        historical_text(".github/workflows/rc1-tag-authorization.yml")
        if evidence_mode
        else (ROOT / ".github/workflows/rc1-tag-authorization.yml").read_text(
            encoding="utf-8"
        )
    )
    require("fetch-depth: 0" in workflow, "authorization workflow lacks full history")
    require("verify_rc1_tag_authorization.py --require-tags" in workflow, "authorization verifier missing")
    require("create_rc1_annotated_tag.py" not in workflow, "workflow invokes tag creation script")
    require("create_rc1_github_prerelease.py" not in workflow, "workflow invokes pre-release script")
    forbidden = forbidden_release_commands(workflow)
    require(not forbidden, "authorization workflow contains release commands: " + ", ".join(forbidden))

    if evidence_mode:
        print(
            "PASS: historical exact-target RC1 authorization preserved after annotated "
            "tag and GitHub pre-release creation; final release remains unauthorized."
        )
    else:
        print(
            "PASS: RC1 exact-target tag authorization verified; "
            "tag and GitHub pre-release remain uncreated."
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-tags", action="store_true")
    args = parser.parse_args()
    verify(require_tags=args.require_tags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
