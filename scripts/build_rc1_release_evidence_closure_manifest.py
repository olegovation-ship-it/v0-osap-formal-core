from __future__ import annotations

from rc1_evidence_closure_lib import (
    AUTHORIZATION_MERGE_COMMIT,
    CANDIDATE_TAG,
    CANDIDATE_TARGET,
    FINAL_TAG,
    HUMAN_STATE,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TAG_TARGET,
    MACHINE_STATE,
    MANIFEST_PATH,
    RECORD_PATH,
    EVIDENCE_PATH,
    read_json,
    repository_root,
    sha256_file,
    write_json,
)

ROOT = repository_root()
OUTPUT = ROOT / MANIFEST_PATH

TARGETS = [
    "README.md",
    "CHANGELOG.md",
    "docs/status_and_nonclaims.md",
    "release/v1.3.0/RC1_GITHUB_PRERELEASE_EVIDENCE.json",
    "release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_RECORD.json",
    "release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_ACCEPTANCE_GATES.md",
    "release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md",
    "release/v1.3.0/RC1_RELEASE_CLOSURE_MANIFEST.json",
    "release/v1.3.0/RC1_TAG_AUTHORIZATION_MANIFEST.json",
    "release/v1.3.0/RC1_GATE_AUDIT_EVIDENCE.json",
    "scripts/rc1_evidence_closure_lib.py",
    "scripts/build_rc1_release_evidence_closure_manifest.py",
    "scripts/verify_rc1_release_evidence_closure.py",
    "scripts/verify_rc1_gate_audit.py",
    "scripts/verify_rc1_release_closure.py",
    "scripts/verify_rc1_tag_authorization.py",
    "tests/test_rc1_gate_audit.py",
    "tests/test_rc1_release_closure.py",
    "tests/test_rc1_tag_authorization.py",
    "tests/test_rc1_release_evidence_closure.py",
    ".github/workflows/rc1-release-closure.yml",
    ".github/workflows/rc1-tag-authorization.yml",
    ".github/workflows/rc1-release-evidence-closure.yml",
]


def main() -> int:
    missing = [rel for rel in TARGETS if not (ROOT / rel).is_file()]
    if missing:
        raise SystemExit(
            "Missing RC1 evidence-closure manifest targets: " + ", ".join(missing)
        )

    record = read_json(ROOT / RECORD_PATH)
    evidence = read_json(ROOT / EVIDENCE_PATH)

    payload = {
        "artifact_id": "V0_OSAP_V1_3_0_RC1_RELEASE_EVIDENCE_CLOSURE_MANIFEST",
        "version": "0.1",
        "date": "2026-07-13",
        "state": MACHINE_STATE,
        "human_state": HUMAN_STATE,
        "authorization_merge_commit": AUTHORIZATION_MERGE_COMMIT,
        "candidate_tag_name": CANDIDATE_TAG,
        "candidate_tag_target_commit": CANDIDATE_TARGET,
        "final_tag_name": FINAL_TAG,
        "immutable_tag": IMMUTABLE_TAG,
        "immutable_tag_target_commit": IMMUTABLE_TAG_TARGET,
        "immutable_doi": IMMUTABLE_DOI,
        "github_prerelease_url": evidence["release"]["url"],
        "github_prerelease_published_at": evidence["release"]["publishedAt"],
        "frozen_historical_manifests": record["frozen_historical_manifests"],
        "files": {rel: sha256_file(ROOT / rel) for rel in TARGETS},
        "release_actions": record["release_actions"],
        "claim_boundary": record["claim_boundary"],
    }
    write_json(OUTPUT, payload)
    print(
        "PASS: RC1 release-evidence closure manifest generated with "
        f"{len(TARGETS)} hashed files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
