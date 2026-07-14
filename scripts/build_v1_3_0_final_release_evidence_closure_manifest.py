from v1_3_0_final_release_evidence_closure_lib import (
    EVIDENCE_PATH,
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
    repository_root,
    sha256_file,
    write_json,
)

ROOT = repository_root()
FILES = [
    "README.md",
    "CHANGELOG.md",
    "docs/status_and_nonclaims.md",
    "pyproject.toml",
    "CITATION.cff",
    "release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_EVIDENCE.json",
    "artifacts/v1_3_0_github_final_release_evidence.json",
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_RECORD.json",
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md",
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_ACCEPTANCE_GATES.md",
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_MANIFEST.json",
    "release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_RECORD.json",
    "release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json",
    "release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_RECORD.json",
    "scripts/v1_3_0_final_release_evidence_closure_lib.py",
    "scripts/build_v1_3_0_final_release_evidence_closure_manifest.py",
    "scripts/verify_v1_3_0_final_release_evidence_closure.py",
    "scripts/build_v1_3_0_final_release_authorization_manifest.py",
    "scripts/verify_v1_3_0_final_release_authorization.py",
    "tests/test_v1_3_0_final_release_evidence_closure.py",
    ".github/workflows/v1-3-0-final-release-evidence-closure.yml",
    ".github/workflows/v1-3-0-final-release-authorization.yml",
]

missing = [rel for rel in FILES if not (ROOT / rel).is_file()]
if missing:
    raise SystemExit("ERROR: missing manifest inputs: " + ", ".join(missing))

evidence = read_json(ROOT / EVIDENCE_PATH)
record = read_json(ROOT / RECORD_PATH)
manifest = {
    "artifact_id": "V0_OSAP_V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST",
    "version": "0.1",
    "date": "2026-07-13",
    "state": MACHINE_STATE,
    "human_state": HUMAN_STATE,
    "repository": REPOSITORY,
    "final_release_authorization_merge_commit": FINAL_AUTHORIZATION_MERGE_COMMIT,
    "stable_tag": FINAL_TAG,
    "exact_stable_target": FINAL_TARGET,
    "rc1_tag": RC1_TAG,
    "rc1_target": RC1_TARGET,
    "immutable_history": {
        "tag": IMMUTABLE_TAG,
        "target_commit": IMMUTABLE_TARGET,
        "doi": IMMUTABLE_DOI,
    },
    "github_final_release": evidence["release"],
    "frozen_historical_artifacts_sha256": record["authorization_basis"][
        "frozen_historical_artifacts_sha256"
    ],
    "files": {rel: sha256_file(ROOT / rel) for rel in FILES},
    "release_actions": record["release_actions"],
    "claim_boundary": record["claim_boundary"],
}
write_json(ROOT / MANIFEST_PATH, manifest)
print(
    "PASS: v1.3.0 final-release evidence-closure manifest generated "
    f"with {len(FILES)} hashed files."
)
