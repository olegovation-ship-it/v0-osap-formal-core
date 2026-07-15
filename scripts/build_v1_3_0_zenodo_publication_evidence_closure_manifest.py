from v1_3_0_zenodo_publication_evidence_closure_lib import (
    EVIDENCE_PATH,
    FINAL_RELEASE_EVIDENCE_MERGE_COMMIT,
    FINAL_TAG,
    FINAL_TARGET,
    FROZEN_PREDECESSORS,
    HUMAN_STATE,
    IMMUTABLE_DOI,
    IMMUTABLE_TAG,
    IMMUTABLE_TARGET,
    MACHINE_STATE,
    MANIFEST_PATH,
    RECORD_PATH,
    REPOSITORY,
    ZENODO_DOI,
    ZENODO_RECORD_ID,
    ZENODO_TITLE,
    ZENODO_URL,
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
    "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE.json",
    "artifacts/v1_3_0_zenodo_publication_evidence.json",
    "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_RECORD.json",
    "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_AND_DOI_FINALIZATION_REPORT.md",
    "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_ACCEPTANCE_GATES.md",
    "scripts/v1_3_0_zenodo_publication_evidence_closure_lib.py",
    "scripts/build_v1_3_0_zenodo_publication_evidence_closure_manifest.py",
    "scripts/verify_v1_3_0_zenodo_publication_evidence_closure.py",
    "tests/test_v1_3_0_zenodo_publication_evidence_closure.py",
    ".github/workflows/v1-3-0-zenodo-publication-evidence-closure.yml",
    *FROZEN_PREDECESSORS,
]

missing = [rel for rel in FILES if not (ROOT / rel).is_file()]
if missing:
    raise SystemExit("ERROR: missing manifest inputs: " + ", ".join(missing))

evidence = read_json(ROOT / EVIDENCE_PATH)
record = read_json(ROOT / RECORD_PATH)
manifest = {
    "artifact_id": "V0_OSAP_V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_MANIFEST",
    "version": "0.1",
    "date": "2026-07-14",
    "state": MACHINE_STATE,
    "human_state": HUMAN_STATE,
    "repository": REPOSITORY,
    "final_release_evidence_merge_commit": FINAL_RELEASE_EVIDENCE_MERGE_COMMIT,
    "stable_tag": FINAL_TAG,
    "exact_stable_target": FINAL_TARGET,
    "zenodo": {
        "record_id": ZENODO_RECORD_ID,
        "doi": ZENODO_DOI,
        "url": ZENODO_URL,
        "title": ZENODO_TITLE,
    },
    "immutable_history": {
        "tag": IMMUTABLE_TAG,
        "target_commit": IMMUTABLE_TARGET,
        "doi": IMMUTABLE_DOI,
    },
    "publication_evidence": evidence["zenodo_record"],
    "frozen_predecessor_artifacts_sha256": record[
        "frozen_predecessor_artifacts_sha256"
    ],
    "files": {rel: sha256_file(ROOT / rel) for rel in FILES},
    "release_actions": record["release_actions"],
    "claim_boundary": record["claim_boundary"],
}
write_json(ROOT / MANIFEST_PATH, manifest)
print(
    "PASS: v1.3.0 Zenodo publication-evidence closure manifest generated "
    f"with {len(FILES)} hashed files."
)
