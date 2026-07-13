from __future__ import annotations

from rc1_release_closure_lib import (
    AUDIT_MERGE_COMMIT,
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
OUTPUT = ROOT / "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json"

TARGETS = [
    "README.md",
    "CHANGELOG.md",
    "docs/status_and_nonclaims.md",
    "release/v1.3.0/RC1_RELEASE_CLOSURE_AND_TAG_PREPARATION_SPECIFICATION.md",
    "release/v1.3.0/RC1_RELEASE_CLOSURE_ACCEPTANCE_GATES.md",
    "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json",
    "release/v1.3.0/RC1_TAG_ANNOTATION_DRAFT.txt",
    "release/v1.3.0/RC1_RELEASE_MANIFEST.json",
    "release/v1.3.0/RC1_THEOREM_INVENTORY.json",
    "release/v1.3.0/RC1_STATEMENT_PARITY_EVIDENCE.json",
    "release/v1.3.0/RC1_CLAIM_CLASSIFICATION_MATRIX.json",
    "scripts/rc1_release_closure_lib.py",
    "scripts/build_rc1_release_closure_manifest.py",
    "scripts/verify_rc1_release_closure.py",
    "scripts/capture_rc1_clean_room_evidence.py",
    "tests/test_rc1_release_closure.py",
    ".github/workflows/rc1-release-closure.yml",
]


def main() -> int:
    missing = [path for path in TARGETS if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("Missing closure-manifest targets: " + ", ".join(missing))

    audit_manifest_path = ROOT / "release/v1.3.0/RC1_RELEASE_MANIFEST.json"
    theorem_inventory_path = ROOT / "release/v1.3.0/RC1_THEOREM_INVENTORY.json"
    tag_record_path = ROOT / "release/v1.3.0/RC1_TAG_PREPARATION_RECORD.json"

    audit_manifest = read_json(audit_manifest_path)
    inventory = read_json(theorem_inventory_path)
    tag_record = read_json(tag_record_path)

    authorized = bool(tag_record["release_actions"].get("tag_target_authorized"))
    state = (
        "RC1_TAG_AUTHORIZED_TAG_NOT_CREATED_PRERELEASE_NOT_CREATED"
        if authorized
        else "RC1_CLOSURE_READY_CI_PENDING_TAG_NOT_CREATED"
    )
    target = CLOSURE_MERGE_COMMIT if authorized else None

    payload = {
        "artifact_id": "V0_OSAP_V1_3_0_RC1_RELEASE_CLOSURE_MANIFEST",
        "version": "0.2" if authorized else "0.1",
        "date": "2026-07-13",
        "state": state,
        "audit_merge_commit": AUDIT_MERGE_COMMIT,
        "closure_merge_commit": CLOSURE_MERGE_COMMIT if authorized else None,
        "candidate_tag_name": CANDIDATE_TAG,
        "tag_target_commit": target,
        "tag_target_policy": tag_record["tag_target_policy"],
        "immutable_tag": IMMUTABLE_TAG,
        "immutable_tag_target_commit": IMMUTABLE_TAG_TARGET,
        "immutable_doi": IMMUTABLE_DOI,
        "theorem_range": inventory["theorem_range"],
        "record_count": inventory["record_count"],
        "source_crosswalk_count": len(inventory["source_crosswalks"]),
        "audit_manifest_sha256": sha256_file(audit_manifest_path),
        "theorem_inventory_sha256": sha256_file(theorem_inventory_path),
        "files": {path: sha256_file(ROOT / path) for path in TARGETS},
        "preserved_audit_release_actions": audit_manifest["release_actions"],
        "release_actions": tag_record["release_actions"],
    }
    write_json(OUTPUT, payload)
    print(f"PASS: RC1 release-closure manifest generated with {len(TARGETS)} hashed files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
