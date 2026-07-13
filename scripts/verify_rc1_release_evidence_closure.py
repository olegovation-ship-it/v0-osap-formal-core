from __future__ import annotations

import argparse

from rc1_evidence_closure_lib import (
    AUTHORIZATION_MERGE_COMMIT,
    CANDIDATE_TAG,
    CANDIDATE_TARGET,
    EVIDENCE_PATH,
    EXPECTED_PUBLISHED_AT,
    EXPECTED_RELEASE_NAME,
    EXPECTED_RELEASE_URL,
    FINAL_TAG,
    HUMAN_STATE,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TAG_TARGET,
    MACHINE_STATE,
    MANIFEST_PATH,
    RECORD_PATH,
    commit_exists,
    is_ancestor,
    local_tag_exists,
    local_tag_target,
    read_json,
    repository_root,
    sha256_file,
    tag_object_type,
)
from rc1_release_closure_lib import forbidden_release_commands

ROOT = repository_root()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            f"RC1 release-evidence closure verification failed: {message}"
        )


def verify(require_tags: bool = False) -> None:
    require(
        commit_exists(AUTHORIZATION_MERGE_COMMIT),
        "authorization merge commit is unavailable",
    )
    require(
        is_ancestor(AUTHORIZATION_MERGE_COMMIT),
        "authorization merge commit is not an ancestor of HEAD",
    )

    candidate_present = local_tag_exists(CANDIDATE_TAG)
    if require_tags:
        require(candidate_present, f"candidate tag {CANDIDATE_TAG} is unavailable")
    if candidate_present:
        require(
            local_tag_target(CANDIDATE_TAG) == CANDIDATE_TARGET,
            "candidate tag target mismatch",
        )
        require(
            tag_object_type(CANDIDATE_TAG) == "tag",
            "candidate tag is not an annotated tag object",
        )

    require(not local_tag_exists(FINAL_TAG), f"final tag {FINAL_TAG} exists prematurely")

    historical_present = local_tag_exists(IMMUTABLE_TAG)
    if require_tags:
        require(historical_present, f"historical tag {IMMUTABLE_TAG} is unavailable")
    if historical_present:
        require(
            local_tag_target(IMMUTABLE_TAG) == IMMUTABLE_TAG_TARGET,
            "historical v1.2.0 target changed",
        )

    evidence = read_json(ROOT / EVIDENCE_PATH)
    record = read_json(ROOT / RECORD_PATH)
    manifest = read_json(ROOT / MANIFEST_PATH)

    release = evidence["release"]
    require(
        evidence["artifact_id"]
        == "V0_OSAP_V1_3_0_RC1_GITHUB_PRERELEASE_EVIDENCE",
        "evidence artifact id mismatch",
    )
    require(
        evidence["authorized_target_commit"] == CANDIDATE_TARGET,
        "evidence target mismatch",
    )
    require(release["tagName"] == CANDIDATE_TAG, "pre-release tag mismatch")
    require(release["name"] == EXPECTED_RELEASE_NAME, "pre-release name mismatch")
    require(release["url"] == EXPECTED_RELEASE_URL, "pre-release URL mismatch")
    require(
        release["publishedAt"] == EXPECTED_PUBLISHED_AT,
        "pre-release publication timestamp mismatch",
    )
    require(release["isPrerelease"] is True, "release is not marked pre-release")
    require(release["isDraft"] is False, "release is still a draft")

    require(record["state"] == MACHINE_STATE, "closure-record state mismatch")
    require(record["human_state"] == HUMAN_STATE, "closure-record human state mismatch")
    require(
        record["authorization_merge_commit"] == AUTHORIZATION_MERGE_COMMIT,
        "authorization merge commit mismatch",
    )
    require(
        record["tag_evidence"]["target_commit"] == CANDIDATE_TARGET,
        "recorded tag target mismatch",
    )
    require(
        record["github_prerelease_evidence"] == release,
        "closure record and GitHub evidence differ",
    )
    require(
        record["release_actions"]["rc1_tag_created"] is True,
        "RC1 tag creation is not recorded",
    )
    require(
        record["release_actions"]["github_prerelease_created"] is True,
        "GitHub pre-release creation is not recorded",
    )
    for key in [
        "final_tag_created",
        "github_final_release_created",
        "zenodo_version_created",
        "doi_changed",
    ]:
        require(
            record["release_actions"][key] is False,
            f"unauthorized final action recorded: {key}",
        )

    frozen = record["frozen_historical_manifests"]
    for rel_path, expected_hash in frozen.items():
        path = ROOT / rel_path
        require(path.is_file(), f"frozen historical manifest missing: {rel_path}")
        require(
            sha256_file(path) == expected_hash,
            f"frozen historical manifest changed: {rel_path}",
        )

    require(manifest["state"] == MACHINE_STATE, "evidence manifest state mismatch")
    require(
        manifest["candidate_tag_target_commit"] == CANDIDATE_TARGET,
        "evidence manifest target mismatch",
    )
    for rel_path, expected_hash in manifest["files"].items():
        path = ROOT / rel_path
        require(path.is_file(), f"evidence-manifest target missing: {rel_path}")
        require(
            sha256_file(path) == expected_hash,
            f"evidence-manifest hash mismatch: {rel_path}",
        )

    for rel_path in ["README.md", "CHANGELOG.md", "docs/status_and_nonclaims.md"]:
        body = (ROOT / rel_path).read_text(encoding="utf-8")
        require(HUMAN_STATE in body, f"evidence-closure state absent from {rel_path}")
        require(IMMUTABLE_DOI in body, f"immutable DOI absent from {rel_path}")
        require(
            "T140" in body and "T150" in body and "T156" in body,
            f"conditional theorem boundary absent from {rel_path}",
        )

    workflows = [
        ".github/workflows/rc1-release-closure.yml",
        ".github/workflows/rc1-tag-authorization.yml",
        ".github/workflows/rc1-release-evidence-closure.yml",
    ]
    for rel_path in workflows:
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        require("fetch-depth: 0" in text, f"full history missing from {rel_path}")
        require(
            forbidden_release_commands(text) == [],
            f"release command found in validation workflow {rel_path}",
        )
        require(
            "create_rc1_annotated_tag.py" not in text,
            f"tag creation script invoked by {rel_path}",
        )
        require(
            "create_rc1_github_prerelease.py" not in text,
            f"pre-release creation script invoked by {rel_path}",
        )

    print(
        "PASS: RC1 annotated tag and GitHub pre-release evidence are closed, "
        "the exact target is preserved, and no final v1.3.0 or Zenodo action is recorded."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-tags", action="store_true")
    args = parser.parse_args()
    verify(require_tags=args.require_tags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
