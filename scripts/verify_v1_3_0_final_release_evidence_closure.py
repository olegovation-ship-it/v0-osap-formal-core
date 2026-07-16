from __future__ import annotations

import argparse
import hashlib
import json
import subprocess

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
    remote_tag_map,
    repository_root,
    run,
    tag_exists,
    tag_object_sha,
    tag_object_type,
    tag_target,
)

ROOT = repository_root()
HISTORICAL_SNAPSHOT = "7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8"
ZENODO_DOI = "10.5281/zenodo.21346728"
POST_MERGE_RECORD = (
    ROOT
    / "release/v1.3.0/"
    "V1_3_0_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json"
)
POST_MERGE_MACHINE_STATE = (
    "POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED_MAIN_DEVELOPMENT_SYNCHRONIZED_"
    "ZENODO_LIFECYCLE_REPLAY_COMPATIBLE_RELEASE_IMMUTABLE"
)
POST_MERGE_MARKER = "POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED"
POST_MERGE_COMPANION_MARKERS = (
    "MAIN_DEVELOPMENT_SYNCHRONIZED",
    "ZENODO_LIFECYCLE_REPLAY_COMPATIBLE",
    "RELEASE_IMMUTABLE",
)
SUCCESSOR_MARKERS = (
    "ZENODO_PUBLICATION_AUTHORIZED",
    "ZENODO_PUBLICATION_EVIDENCE_CLOSED",
    "DOI_FINALIZED",
    POST_MERGE_MARKER,
)


def req(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("historical lifecycle replay failed: " + message)


def blob(rel: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{HISTORICAL_SNAPSHOT}:{rel}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def historical_json(rel: str) -> dict:
    return json.loads(blob(rel).decode("utf-8"))


def historical_text(rel: str) -> str:
    return blob(rel).decode("utf-8")


def historical_sha256(rel: str) -> str:
    return hashlib.sha256(blob(rel)).hexdigest()


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def verify(require_tags: bool = False, verify_live: bool = False) -> None:
    for commit in (FINAL_AUTHORIZATION_MERGE_COMMIT, HISTORICAL_SNAPSHOT):
        req(
            run(
                "git",
                "merge-base",
                "--is-ancestor",
                commit,
                "HEAD",
                check=False,
            ).returncode
            == 0,
            f"{commit} not ancestor of HEAD",
        )

    if require_tags:
        for tag, target in (
            (IMMUTABLE_TAG, IMMUTABLE_TARGET),
            (RC1_TAG, RC1_TARGET),
            (FINAL_TAG, FINAL_TARGET),
        ):
            req(tag_exists(tag) and tag_target(tag) == target, f"tag mismatch: {tag}")

    req(tag_object_type(FINAL_TAG) == "tag", "stable tag not annotated")
    object_sha = tag_object_sha(FINAL_TAG)
    remote = remote_tag_map(FINAL_TAG)
    req(
        remote.get(f"refs/tags/{FINAL_TAG}") == object_sha,
        "remote tag object mismatch",
    )
    req(
        remote.get(f"refs/tags/{FINAL_TAG}^{{}}") == FINAL_TARGET,
        "remote peeled target mismatch",
    )

    evidence = historical_json(EVIDENCE_PATH.as_posix())
    record = historical_json(RECORD_PATH.as_posix())
    manifest = historical_json(MANIFEST_PATH.as_posix())

    for rel in (EVIDENCE_PATH, RECORD_PATH, MANIFEST_PATH):
        path = ROOT / rel
        req(path.is_file(), f"missing {rel}")
        req(
            path.read_bytes() == blob(rel.as_posix()),
            f"historical artifact mutated: {rel}",
        )

    stable_tag = evidence["stable_tag"]
    release = evidence["release"]
    req(
        stable_tag["tagName"] == FINAL_TAG
        and stable_tag["peeledTargetCommit"] == FINAL_TARGET,
        "stable tag evidence mismatch",
    )
    req(
        release["tagName"] == FINAL_TAG
        and release["name"] == EXPECTED_RELEASE_NAME,
        "release identity mismatch",
    )
    req(
        release["url"] == EXPECTED_RELEASE_URL
        and release["publishedAt"] == EXPECTED_PUBLISHED_AT,
        "release metadata mismatch",
    )
    req(
        release["isDraft"] is False
        and release["isPrerelease"] is False
        and release["isLatest"] is True,
        "release state mismatch",
    )

    notes = normalize(
        historical_text("release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_NOTES.md")
    )
    req(
        hashlib.sha256(notes.encode()).hexdigest()
        == release["normalizedBodySha256"],
        "historical notes hash mismatch",
    )
    req(
        record["state"] == MACHINE_STATE
        and record["human_state"] == HUMAN_STATE,
        "record state mismatch",
    )
    for rel, expected in record["authorization_basis"][
        "frozen_historical_artifacts_sha256"
    ].items():
        req(
            historical_sha256(rel) == expected,
            f"frozen predecessor changed: {rel}",
        )
    req(
        manifest["state"] == MACHINE_STATE
        and manifest["exact_stable_target"] == FINAL_TARGET,
        "manifest state mismatch",
    )
    for rel, expected in manifest["files"].items():
        req(
            historical_sha256(rel) == expected,
            f"manifest replay mismatch: {rel}",
        )

    post_merge_seen = False
    for rel in ("README.md", "docs/status_and_nonclaims.md"):
        current = (ROOT / rel).read_text(encoding="utf-8")
        req(
            any(marker in current for marker in SUCCESSOR_MARKERS),
            f"successor state absent from {rel}",
        )
        req(
            ZENODO_DOI in current and FINAL_TARGET in current,
            f"current publication metadata absent from {rel}",
        )
        if POST_MERGE_MARKER in current:
            post_merge_seen = True
            req(
                all(
                    marker in current
                    for marker in POST_MERGE_COMPANION_MARKERS
                ),
                f"incomplete post-merge lifecycle state in {rel}",
            )
            req(
                IMMUTABLE_DOI in current,
                f"historical DOI absent from post-merge surface {rel}",
            )
            req(
                all(theorem in current for theorem in ("T140", "T150", "T156")),
                f"conditional theorem boundary absent from {rel}",
            )

    if post_merge_seen:
        req(POST_MERGE_RECORD.is_file(), "post-merge closeout record missing")
        post_merge = json.loads(
            POST_MERGE_RECORD.read_text(encoding="utf-8")
        )
        req(
            post_merge["state"] == POST_MERGE_MACHINE_STATE,
            "post-merge closeout state mismatch",
        )
        req(
            post_merge["merge_closeout"]["merge_commit"]
            == "53dcd231aa7d5208a2360d737f01bc2e95e9450b",
            "post-merge synchronization baseline mismatch",
        )
        req(
            post_merge["release_state"]["stable_tag_peeled_target"]
            == FINAL_TARGET,
            "post-merge stable target mismatch",
        )
        req(
            post_merge["release_state"]["zenodo_version_doi"]
            == ZENODO_DOI,
            "post-merge DOI mismatch",
        )
        req(
            post_merge["immutable_history"]["doi"] == IMMUTABLE_DOI,
            "post-merge historical DOI mismatch",
        )
        req(
            post_merge["candidate_scope"]["checker_component_version"]
            == "0.7.0.dev1",
            "checker component changed",
        )
        req(
            post_merge["candidate_scope"]["conditional_theorems"]
            == ["T140", "T150", "T156"],
            "conditional theorem ledger changed",
        )
        req(
            all(value is False for value in post_merge["non_actions"].values()),
            "post-merge record contains a forbidden release action",
        )

    req(
        'version = "0.7.0.dev1"'
        in (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
        "checker version changed",
    )
    req(
        ZENODO_DOI in (ROOT / "CITATION.cff").read_text(encoding="utf-8"),
        "current DOI missing from CITATION.cff",
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
                (
                    "tagName,name,isDraft,isPrerelease,publishedAt,url,"
                    "targetCommitish,body"
                ),
            ).stdout
        )
        req(
            live["url"] == EXPECTED_RELEASE_URL
            and live["publishedAt"] == EXPECTED_PUBLISHED_AT,
            "live release mismatch",
        )
        req(normalize(live["body"]) == notes, "live release notes differ")

    print(
        f"PASS: pre-Zenodo final-release evidence replayed from "
        f"{HISTORICAL_SNAPSHOT}; finalized publication and guarded post-merge "
        "successor states accepted without predecessor mutation."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-tags", action="store_true")
    parser.add_argument("--verify-live", action="store_true")
    args = parser.parse_args()
    verify(args.require_tags, args.verify_live)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
