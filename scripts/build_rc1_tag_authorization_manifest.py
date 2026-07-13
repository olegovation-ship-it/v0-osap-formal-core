from __future__ import annotations

from rc1_tag_release_lib import (
    CANDIDATE_TAG,
    CLOSURE_MERGE_COMMIT,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TAG_TARGET,
    read_json,
    repository_root,
    sha256_file,
    write_json,
)

ROOT = repository_root()
OUTPUT = ROOT / "release/v1.3.0/RC1_TAG_AUTHORIZATION_MANIFEST.json"

TARGETS = [
    "README.md",
    "CHANGELOG.md",
    "docs/status_and_nonclaims.md",
    "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json",
    "release/v1.3.0/RC1_TAG_AUTHORIZATION_AND_GITHUB_PRERELEASE_SPECIFICATION.md",
    "release/v1.3.0/RC1_TAG_AUTHORIZATION_GATES.md",
    "release/v1.3.0/RC1_TAG_AUTHORIZATION_RECORD.json",
    "release/v1.3.0/RC1_ANNOTATED_TAG_MESSAGE.txt",
    "release/v1.3.0/RC1_GITHUB_PRERELEASE_NOTES.md",
    "release/v1.3.0/RC1_GITHUB_PRERELEASE_METADATA.json",
    "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json",
    "scripts/rc1_release_closure_lib.py",
    "scripts/build_rc1_release_closure_manifest.py",
    "scripts/verify_rc1_release_closure.py",
    "scripts/rc1_tag_release_lib.py",
    "scripts/build_rc1_tag_authorization_manifest.py",
    "scripts/verify_rc1_tag_authorization.py",
    "scripts/create_rc1_annotated_tag.py",
    "scripts/create_rc1_github_prerelease.py",
    "tests/test_rc1_release_closure.py",
    "tests/test_rc1_tag_authorization.py",
    ".github/workflows/rc1-tag-authorization.yml",
]


def main() -> int:
    missing = [path for path in TARGETS if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("Missing tag-authorization manifest targets: " + ", ".join(missing))

    record = read_json(ROOT / "release/v1.3.0/RC1_TAG_AUTHORIZATION_RECORD.json")
    preparation = read_json(ROOT / "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json")

    payload = {
        "artifact_id": "V0_OSAP_V1_3_0_RC1_TAG_AUTHORIZATION_MANIFEST",
        "version": "0.1",
        "date": "2026-07-13",
        "state": "RC1_TAG_AUTHORIZED_TAG_NOT_CREATED_PRERELEASE_NOT_CREATED",
        "candidate_tag_name": CANDIDATE_TAG,
        "authorized_tag_target_commit": CLOSURE_MERGE_COMMIT,
        "immutable_tag": IMMUTABLE_TAG,
        "immutable_tag_target_commit": IMMUTABLE_TAG_TARGET,
        "immutable_doi": IMMUTABLE_DOI,
        "authorization_record_sha256": sha256_file(ROOT / "release/v1.3.0/RC1_TAG_AUTHORIZATION_RECORD.json"),
        "tag_preparation_record_sha256": sha256_file(ROOT / "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json"),
        "release_actions": preparation["release_actions"],
        "authorization_scope": record["authorization_scope"],
        "files": {path: sha256_file(ROOT / path) for path in TARGETS},
    }
    write_json(OUTPUT, payload)
    print(f"PASS: RC1 tag-authorization manifest generated with {len(TARGETS)} hashed files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
