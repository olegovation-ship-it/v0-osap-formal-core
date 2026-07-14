from __future__ import annotations

import argparse
import hashlib
import json

from v1_3_0_final_release_evidence_closure_lib import (
    EVIDENCE_PATH,
    EXPECTED_PUBLISHED_AT,
    EXPECTED_RELEASE_NAME,
    EXPECTED_RELEASE_URL,
    FINAL_AUTHORIZATION_MERGE_COMMIT,
    FINAL_TAG,
    FINAL_TARGET,
    HUMAN_STATE,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TARGET,
    MACHINE_STATE,
    MANIFEST_PATH,
    RC1_TAG,
    RC1_TARGET,
    RECORD_PATH,
    REPOSITORY,
    read_json,
    remote_tag_map,
    repository_root,
    run,
    sha256_file,
    tag_exists,
    tag_object_sha,
    tag_object_type,
    tag_target,
)

ROOT = repository_root()

def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "v1.3.0 final-release evidence-closure verification failed: "
            + message
        )

def normalized_body(value: str) -> str:
    return value.replace("\r\n", "\n").strip()

def verify(require_tags: bool = False, verify_live: bool = False) -> None:
    require(
        run(
            "git",
            "merge-base",
            "--is-ancestor",
            FINAL_AUTHORIZATION_MERGE_COMMIT,
            "HEAD",
            check=False,
        ).returncode == 0,
        "final authorization merge commit is not an ancestor of HEAD",
    )

    if require_tags:
        for tag, target in (
            (IMMUTABLE_TAG, IMMUTABLE_TARGET),
            (RC1_TAG, RC1_TARGET),
            (FINAL_TAG, FINAL_TARGET),
        ):
            require(tag_exists(tag), f"required tag missing: {tag}")
            require(tag_target(tag) == target, f"tag target mismatch: {tag}")

    require(tag_object_type(FINAL_TAG) == "tag", "stable tag is not annotated")
    local_object_sha = tag_object_sha(FINAL_TAG)
    remote = remote_tag_map(FINAL_TAG)
    require(
        remote.get(f"refs/tags/{FINAL_TAG}") == local_object_sha,
        "remote stable-tag object SHA mismatch",
    )
    require(
        remote.get(f"refs/tags/{FINAL_TAG}^{{}}") == FINAL_TARGET,
        "remote stable-tag peeled target mismatch",
    )

    evidence = read_json(ROOT / EVIDENCE_PATH)
    record = read_json(ROOT / RECORD_PATH)
    manifest = read_json(ROOT / MANIFEST_PATH)

    require(
        evidence["artifact_id"]
        == "V0_OSAP_V1_3_0_GITHUB_FINAL_RELEASE_EVIDENCE",
        "evidence artifact id mismatch",
    )
    tag = evidence["stable_tag"]
    release = evidence["release"]
    require(tag["tagName"] == FINAL_TAG, "evidence tag mismatch")
    require(tag["objectType"] == "tag", "evidence tag type mismatch")
    require(tag["localObjectSha"] == local_object_sha, "local object SHA mismatch")
    require(tag["peeledTargetCommit"] == FINAL_TARGET, "peeled target mismatch")
    require(
        tag["remotePeeledTargetCommit"] == FINAL_TARGET,
        "remote peeled target mismatch",
    )

    require(release["tagName"] == FINAL_TAG, "release tag mismatch")
    require(release["name"] == EXPECTED_RELEASE_NAME, "release name mismatch")
    require(release["url"] == EXPECTED_RELEASE_URL, "release URL mismatch")
    require(
        release["publishedAt"] == EXPECTED_PUBLISHED_AT,
        "publication timestamp mismatch",
    )
    require(release["isDraft"] is False, "release is a draft")
    require(release["isPrerelease"] is False, "release is a pre-release")
    require(release["isLatest"] is True, "release is not Latest")
    require(release["targetCommitish"] == "main", "targetCommitish mismatch")

    notes = normalized_body(
        (ROOT / "release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_NOTES.md")
        .read_text(encoding="utf-8")
    )
    require(
        hashlib.sha256(notes.encode("utf-8")).hexdigest()
        == release["normalizedBodySha256"],
        "authorized release-notes hash mismatch",
    )

    require(record["state"] == MACHINE_STATE, "record state mismatch")
    require(record["human_state"] == HUMAN_STATE, "record human state mismatch")
    require(record["stable_tag_evidence"] == tag, "record/tag evidence differ")
    require(
        record["github_final_release_evidence"] == release,
        "record/release evidence differ",
    )
    for key in ("stable_tag_created", "github_final_release_created"):
        require(record["release_actions"][key] is True, f"{key} not recorded")
    for key in (
        "zenodo_version_authorized",
        "zenodo_version_created",
        "doi_changed",
    ):
        require(
            record["release_actions"][key] is False,
            f"unauthorized Zenodo/DOI action recorded: {key}",
        )

    for rel, expected_hash in record["authorization_basis"][
        "frozen_historical_artifacts_sha256"
    ].items():
        require((ROOT / rel).is_file(), f"frozen artifact missing: {rel}")
        require(
            sha256_file(ROOT / rel) == expected_hash,
            f"frozen artifact changed: {rel}",
        )

    require(manifest["state"] == MACHINE_STATE, "manifest state mismatch")
    require(
        manifest["exact_stable_target"] == FINAL_TARGET,
        "manifest target mismatch",
    )
    for rel, expected_hash in manifest["files"].items():
        require((ROOT / rel).is_file(), f"manifest input missing: {rel}")
        require(
            sha256_file(ROOT / rel) == expected_hash,
            f"manifest hash mismatch: {rel}",
        )

    for rel in ("README.md", "CHANGELOG.md", "docs/status_and_nonclaims.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        require(HUMAN_STATE in text, f"closure state missing from {rel}")
        require(FINAL_TARGET in text, f"stable target missing from {rel}")
        require(EXPECTED_RELEASE_URL in text, f"release URL missing from {rel}")
        require(IMMUTABLE_DOI in text, f"immutable DOI missing from {rel}")
        require(
            all(item in text for item in ("T140", "T150", "T156")),
            f"conditional theorem boundary missing from {rel}",
        )

    require(
        'version = "0.7.0.dev1"'
        in (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
        "embedded checker component version changed",
    )
    require(
        IMMUTABLE_DOI in (ROOT / "CITATION.cff").read_text(encoding="utf-8"),
        "historical DOI missing from CITATION.cff",
    )

    for rel in (
        ".github/workflows/v1-3-0-final-release-authorization.yml",
        ".github/workflows/v1-3-0-final-release-evidence-closure.yml",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        require("fetch-depth: 0" in text, f"full history absent from {rel}")
        for forbidden in ("gh release create", "git tag -a", "--execute"):
            require(forbidden not in text, f"mutation command in {rel}: {forbidden}")

    historical_builder = (
        ROOT / "scripts/build_v1_3_0_final_release_authorization_manifest.py"
    ).read_text(encoding="utf-8")
    historical_verifier = (
        ROOT / "scripts/verify_v1_3_0_final_release_authorization.py"
    ).read_text(encoding="utf-8")
    require(
        FINAL_AUTHORIZATION_MERGE_COMMIT in historical_builder,
        "final-authorization builder is not historical",
    )
    require(
        FINAL_AUTHORIZATION_MERGE_COMMIT in historical_verifier,
        "final-authorization verifier is not historical",
    )

    if verify_live:
        live = json.loads(
            run(
                "gh",
                "release",
                "view",
                FINAL_TAG,
                "--repo",
                REPOSITORY,
                "--json",
                "tagName,name,isDraft,isPrerelease,publishedAt,url,targetCommitish,body",
            ).stdout
        )
        rows = json.loads(
            run(
                "gh",
                "release",
                "list",
                "--repo",
                REPOSITORY,
                "--limit",
                "100",
                "--json",
                "tagName,isLatest",
            ).stdout
        )
        row = [item for item in rows if item["tagName"] == FINAL_TAG]
        require(
            len(row) == 1 and row[0]["isLatest"] is True,
            "live release is not Latest",
        )
        require(live["url"] == EXPECTED_RELEASE_URL, "live URL mismatch")
        require(
            live["publishedAt"] == EXPECTED_PUBLISHED_AT,
            "live timestamp mismatch",
        )
        require(live["isDraft"] is False, "live release is draft")
        require(live["isPrerelease"] is False, "live release is prerelease")
        require(
            normalized_body(live["body"]) == notes,
            "live release notes differ from authorized notes",
        )

    print(
        "PASS: V0 OSAP v1.3.0 stable tag and GitHub final-release "
        "evidence are closed and historically preserved; no Zenodo "
        "publication or DOI mutation is authorized."
    )

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-tags", action="store_true")
    parser.add_argument("--verify-live", action="store_true")
    args = parser.parse_args()
    verify(require_tags=args.require_tags, verify_live=args.verify_live)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
