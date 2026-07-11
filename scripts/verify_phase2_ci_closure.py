from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str) -> dict:
    return json.loads(text(path))


evidence = load("release/v1.3.0/PHASE2_CI_CLOSURE_EVIDENCE.json")
crosswalk = load("release/v1.3.0/theorem_crosswalk_phase2.json")
report = text(
    "release/v1.3.0/PHASE2_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md"
)
acceptance = text("release/v1.3.0/PHASE2_ACCEPTANCE_GATES.md")
implementation = text("release/v1.3.0/PHASE2_IMPLEMENTATION_REPORT.md")
readme = text("README.md")
changelog = text("CHANGELOG.md")
status = text("docs/status_and_nonclaims.md")
register = text("docs/theorem_register.md")
workflow = text(".github/workflows/release-readiness.yml")

EXPECTED_HEAD = "90865cca5fafde161254b7e313621d369ae5efc5"
EXPECTED_MERGE = "f494cd9401e2b9ff91d87de77e11f4eb2468726c"
EXPECTED_DOI = "10.5281/zenodo.21306969"
EXPECTED_STATUS = "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"

assert evidence["status"] == EXPECTED_STATUS
assert evidence["theorem_range"] == "T127-T132"
assert evidence["pull_request"]["number"] == 2
assert evidence["pull_request"]["base"] == "main"
assert evidence["pull_request"]["head"] == "v1.3.0-development"
assert evidence["pull_request"]["head_sha"] == EXPECTED_HEAD
assert evidence["pull_request"]["merge_commit_sha"] == EXPECTED_MERGE
assert evidence["pull_request"]["pr_check_total"] == 8
assert evidence["pull_request"]["pr_check_result"] == "PASS"
assert evidence["local_validation"]["python_tests"] == 111
assert all(
    value == "PASS"
    for key, value in evidence["local_validation"].items()
    if key != "python_tests"
)
assert evidence["historical_preservation"]["baseline_tag"] == "v1.2.0"
assert evidence["historical_preservation"]["baseline_doi"] == EXPECTED_DOI
assert evidence["historical_preservation"]["manifest_verifier_retained"] is True
assert evidence["historical_preservation"]["closure_verifier_retained"] is True
assert evidence["historical_preservation"]["tag_moved_or_retagged"] is False
assert evidence["historical_preservation"]["new_doi_created"] is False

assert crosswalk["phase1_status"] == "ACCEPTED_CI_PASS"
assert crosswalk["phase2_status"] == "ACCEPTED_CI_PASS_MERGED"
assert crosswalk["closure_evidence"] == (
    "release/v1.3.0/PHASE2_CI_CLOSURE_EVIDENCE.json"
)
assert crosswalk["pull_request"] == 2
assert crosswalk["head_commit"] == EXPECTED_HEAD
assert crosswalk["merge_commit"] == EXPECTED_MERGE
assert crosswalk["github_pr_checks"] == 8
assert crosswalk["python_tests"] == 111
assert all(row["parity_status"] == "ACCEPTED_CI_PASS" for row in crosswalk["records"])

for required in [
    "ACCEPTED / CI_PASS / MERGED / HISTORICALLY_PRESERVED",
    EXPECTED_HEAD,
    EXPECTED_MERGE,
    EXPECTED_DOI,
    "111 tests PASS",
    "8/8 PASS",
]:
    assert required in report

for document in [acceptance, implementation, readme, changelog, status, register]:
    assert EXPECTED_MERGE in document
    assert EXPECTED_DOI in document or document in [implementation, register]

assert "passed 8/8 checks" in readme
assert "111 passing tests" in readme
assert "No accepted theorem IDs beyond T132" in status
assert "CI pending" not in register

for command in [
    "python scripts/verify_manifest.py",
    "python scripts/verify_closure.py",
    "python scripts/verify_phase1_alignment.py",
    "python scripts/verify_phase2_expansion.py",
    "python scripts/verify_phase2_ci_closure.py",
]:
    assert command in workflow

for path in [
    "README.md",
    "docs/status_and_nonclaims.md",
    "docs/theorem_register.md",
    "release/v1.3.0/PHASE2_ACCEPTANCE_GATES.md",
    "release/v1.3.0/PHASE2_IMPLEMENTATION_REPORT.md",
    "release/v1.3.0/theorem_crosswalk_phase2.json",
]:
    body = text(path)
    assert "PHASE 2 T127-T132 EXPANSION - PATCH READY / CI PENDING" not in body
    assert '"phase2_status": "BUILD_READY_CI_PENDING"' not in body
    assert '"parity_status": "PATCH_READY_CI_PENDING"' not in body

print(
    "PASS: V0 OSAP v1.3.0 Phase 2 CI closure, merge evidence, and v1.2.0 historical preservation verified."
)
