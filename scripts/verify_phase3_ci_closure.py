from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str) -> dict:
    return json.loads(text(path))


evidence = load("release/v1.3.0/PHASE3_CI_CLOSURE_EVIDENCE.json")
crosswalk = load("release/v1.3.0/theorem_crosswalk_phase3.json")
report = text(
    "release/v1.3.0/PHASE3_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md"
)
acceptance = text("release/v1.3.0/PHASE3_ACCEPTANCE_GATES.md")
build_spec = text("release/v1.3.0/PHASE3_BUILD_SPECIFICATION.md")
implementation = text("release/v1.3.0/PHASE3_IMPLEMENTATION_REPORT.md")
readme = text("README.md")
changelog = text("CHANGELOG.md")
status = text("docs/status_and_nonclaims.md")
register = text("docs/theorem_register.md")
workflow = text(".github/workflows/release-readiness.yml")

EXPECTED_HEAD = "2172591ed8a5ab3c1fa31f2a3a6575536f161fe4"
EXPECTED_MERGE = "c02b05f667b82aa31ac8865c31219b94b1fc74d2"
EXPECTED_DOI = "10.5281/zenodo.21306969"
EXPECTED_STATUS = "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"

assert evidence["status"] == EXPECTED_STATUS
assert evidence["theorem_range"] == "T133-T138"
assert evidence["pull_request"]["number"] == 4
assert evidence["pull_request"]["base"] == "main"
assert evidence["pull_request"]["head"] == "v1.3.0-development"
assert evidence["pull_request"]["head_sha"] == EXPECTED_HEAD
assert evidence["pull_request"]["merge_commit_sha"] == EXPECTED_MERGE
assert evidence["pull_request"]["pr_check_total"] == 8
assert evidence["pull_request"]["pr_check_result"] == "PASS"
assert evidence["pull_request"]["changed_files"] == 50
assert evidence["pull_request"]["additions"] == 1848
assert evidence["pull_request"]["deletions"] == 20
assert evidence["local_validation"]["python_tests"] == 112
assert all(
    value == "PASS"
    for key, value in evidence["local_validation"].items()
    if key != "python_tests"
)
assert evidence["historical_preservation"]["baseline_tag"] == "v1.2.0"
assert evidence["historical_preservation"]["baseline_doi"] == EXPECTED_DOI
assert evidence["historical_preservation"]["manifest_verifier_retained"] is True
assert evidence["historical_preservation"]["closure_verifier_retained"] is True
assert evidence["historical_preservation"]["phase1_record_retained"] is True
assert evidence["historical_preservation"]["phase2_record_retained"] is True
assert evidence["historical_preservation"]["branch_sync_to_merge_commit"] is True
assert evidence["historical_preservation"]["tag_moved_or_retagged"] is False
assert evidence["historical_preservation"]["new_doi_created"] is False

assert crosswalk["phase1_status"] == "ACCEPTED_CI_PASS"
assert crosswalk["phase2_status"] == "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"
assert crosswalk["phase3_status"] == "ACCEPTED_CI_PASS_MERGED"
assert crosswalk["closure_evidence"] == (
    "release/v1.3.0/PHASE3_CI_CLOSURE_EVIDENCE.json"
)
assert crosswalk["pull_request"] == 4
assert crosswalk["head_commit"] == EXPECTED_HEAD
assert crosswalk["merge_commit"] == EXPECTED_MERGE
assert crosswalk["github_pr_checks"] == 8
assert crosswalk["python_tests"] == 112
assert crosswalk["historical_preservation"] == "PASS"
assert all(row["parity_status"] == "ACCEPTED_CI_PASS" for row in crosswalk["records"])
assert all(
    row["claim_limitations"] == ["finite accepted fragment only"]
    for row in crosswalk["records"]
)

for required in [
    "ACCEPTED / CI_PASS / MERGED / HISTORICALLY_PRESERVED",
    EXPECTED_HEAD,
    EXPECTED_MERGE,
    EXPECTED_DOI,
    "112 tests PASS",
    "8/8 PASS",
]:
    assert required in report

for document in [
    acceptance,
    build_spec,
    implementation,
    readme,
    changelog,
    status,
    register,
]:
    assert EXPECTED_MERGE in document
    assert EXPECTED_DOI in document

assert "passed 8/8 checks" in readme
assert "112 passing tests" in readme
assert "No accepted theorem IDs beyond T138" in status
assert "CI pending" not in register
assert "Actions pending" not in register

for command in [
    "python scripts/verify_manifest.py",
    "python scripts/verify_closure.py",
    "python scripts/verify_phase1_alignment.py",
    "python scripts/verify_phase2_expansion.py",
    "python scripts/verify_phase2_ci_closure.py",
    "python scripts/verify_phase3_expansion.py",
    "python scripts/verify_phase3_ci_closure.py",
]:
    assert command in workflow

for path in [
    "README.md",
    "docs/status_and_nonclaims.md",
    "docs/theorem_register.md",
    "release/v1.3.0/PHASE3_ACCEPTANCE_GATES.md",
    "release/v1.3.0/PHASE3_BUILD_SPECIFICATION.md",
    "release/v1.3.0/PHASE3_IMPLEMENTATION_REPORT.md",
    "release/v1.3.0/theorem_crosswalk_phase3.json",
]:
    body = text(path)
    assert "PHASE 3 T133-T138 FIREWALL EXPANSION - BUILD READY / CI PENDING" not in body
    assert '"phase3_status": "BUILD_READY_CI_PENDING"' not in body
    assert '"parity_status": "PATCH_READY_CI_PENDING"' not in body
    assert "CI acceptance pending" not in body

print(
    "PASS: V0 OSAP v1.3.0 Phase 3 CI closure, merge evidence, and v1.2.0 historical preservation verified."
)
