from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str) -> dict:
    return json.loads(text(path))


evidence = load("release/v1.3.0/PHASE5_CI_CLOSURE_EVIDENCE.json")
crosswalk = load("release/v1.3.0/theorem_crosswalk_phase5.json")
report = text("release/v1.3.0/PHASE5_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md")
acceptance = text("release/v1.3.0/PHASE5_ACCEPTANCE_GATES.md")
build_spec = text("release/v1.3.0/PHASE5_BUILD_SPECIFICATION.md")
implementation = text("release/v1.3.0/PHASE5_IMPLEMENTATION_REPORT.md")
readme = text("README.md")
changelog = text("CHANGELOG.md")
status = text("docs/status_and_nonclaims.md")
register = text("docs/theorem_register.md")
workflow = text(".github/workflows/release-readiness.yml")

EXPECTED_IMPLEMENTATION_BASELINE = "2a769d7723470cce59df81262b586abf19b9c750"
EXPECTED_HEAD = "977c5404ebc5cdef9495edd1c46b08d3b0452acb"
EXPECTED_MERGE = "5c689de1a30104aa6c4e3860d5e7c26746e2d797"
EXPECTED_MERGED_AT = "2026-07-12T19:11:41Z"
EXPECTED_DOI = "10.5281/zenodo.21306969"
EXPECTED_STATUS = "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"

assert evidence["status"] == EXPECTED_STATUS
assert evidence["theorem_range"] == "T145-T150"
assert evidence["implementation_baseline_merge_commit"] == EXPECTED_IMPLEMENTATION_BASELINE
assert evidence["pull_request"]["number"] == 8
assert evidence["pull_request"]["base"] == "main"
assert evidence["pull_request"]["head"] == "v1.3.0-development"
assert evidence["pull_request"]["head_sha"] == EXPECTED_HEAD
assert evidence["pull_request"]["merge_commit_sha"] == EXPECTED_MERGE
assert evidence["pull_request"]["merged_at_utc"] == EXPECTED_MERGED_AT
assert evidence["pull_request"]["pr_check_total"] == 8
assert evidence["pull_request"]["pr_check_result"] == "PASS"
assert evidence["pull_request"]["commits"] == 2
assert evidence["pull_request"]["changed_files"] == 54
assert evidence["pull_request"]["additions"] == 2142
assert evidence["pull_request"]["deletions"] == 24

assert evidence["local_validation"]["python_tests"] == 14
assert all(
    value == "PASS"
    for key, value in evidence["local_validation"].items()
    if key != "python_tests"
)

assert len(evidence["workflow_runs"]) == 5
assert all(run["conclusion"] == "success" for run in evidence["workflow_runs"])
release_run = next(run for run in evidence["workflow_runs"] if run["name"] == "Release readiness")
assert release_run["run_id"] == 29205256775
assert set(release_run["jobs"]) == {
    "immutable-v1-2-baseline",
    "v1-3-development-readiness",
}

historical = evidence["historical_preservation"]
assert historical["baseline_tag"] == "v1.2.0"
assert historical["baseline_doi"] == EXPECTED_DOI
assert historical["manifest_verifier_retained"] is True
assert historical["closure_verifier_retained"] is True
for phase in range(1, 5):
    assert historical[f"phase{phase}_record_retained"] is True
assert historical["branch_sync_to_merge_commit"] is True
assert historical["tag_moved_or_retagged"] is False
assert historical["new_doi_created"] is False

assert crosswalk["baseline_merge_commit"] == EXPECTED_IMPLEMENTATION_BASELINE
assert crosswalk["phase1_status"] == "ACCEPTED_CI_PASS"
for phase in range(2, 5):
    assert crosswalk[f"phase{phase}_status"] == "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"
assert crosswalk["phase5_status"] == "ACCEPTED_CI_PASS_MERGED"
assert crosswalk["closure_evidence"] == "release/v1.3.0/PHASE5_CI_CLOSURE_EVIDENCE.json"
assert crosswalk["pull_request"] == 8
assert crosswalk["head_commit"] == EXPECTED_HEAD
assert crosswalk["merge_commit"] == EXPECTED_MERGE
assert crosswalk["merged_at_utc"] == EXPECTED_MERGED_AT
assert crosswalk["github_pr_checks"] == 8
assert crosswalk["python_tests"] == 14
assert crosswalk["historical_preservation"] == "PASS"
assert [row["theorem_id"] for row in crosswalk["records"]] == [f"T{i}" for i in range(145, 151)]
assert all(row["parity_status"] == "ACCEPTED_CI_PASS" for row in crosswalk["records"])

for required in [
    "ACCEPTED / CI_PASS / MERGED / HISTORICALLY_PRESERVED",
    EXPECTED_IMPLEMENTATION_BASELINE,
    EXPECTED_HEAD,
    EXPECTED_MERGE,
    EXPECTED_DOI,
    "14 tests PASS",
    "8/8 PASS",
]:
    assert required in report

for document in [acceptance, build_spec, implementation, readme, changelog, status, register]:
    assert EXPECTED_MERGE in document
    assert EXPECTED_DOI in document

assert "passed 8/8 checks" in readme
assert "14 passing tests" in readme
accepted_boundary = re.search(r"No accepted theorem IDs beyond T(\d+)", status)
assert accepted_boundary is not None
assert int(accepted_boundary.group(1)) >= 150
assert "Phase 5 patch status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`." in register

for command in [
    "python scripts/verify_manifest.py",
    "python scripts/verify_closure.py",
    "python scripts/verify_phase1_alignment.py",
    "python scripts/verify_phase2_expansion.py",
    "python scripts/verify_phase2_ci_closure.py",
    "python scripts/verify_phase3_expansion.py",
    "python scripts/verify_phase3_ci_closure.py",
    "python scripts/verify_phase4_expansion.py",
    "python scripts/verify_phase4_ci_closure.py",
    "python scripts/verify_phase5_expansion.py",
    "python scripts/verify_phase5_ci_closure.py",
]:
    assert command in workflow

for path in [
    "README.md",
    "docs/status_and_nonclaims.md",
    "docs/theorem_register.md",
    "release/v1.3.0/PHASE5_ACCEPTANCE_GATES.md",
    "release/v1.3.0/PHASE5_BUILD_SPECIFICATION.md",
    "release/v1.3.0/PHASE5_IMPLEMENTATION_REPORT.md",
    "release/v1.3.0/theorem_crosswalk_phase5.json",
]:
    body = text(path)
    assert "PHASE 5 T145-T150 CANONICALIZATION, REPLAY, MIGRATION, CORRESPONDENCE, AND SOUNDNESS EXPANSION - BUILD READY / CI PENDING" not in body
    assert '"phase5_status": "BUILD_READY_CI_PENDING"' not in body
    assert '"parity_status": "PATCH_READY_CI_PENDING"' not in body
    assert "Phase 5 remains `BUILD_READY / CI PENDING`" not in body

print(
    "PASS: V0 OSAP v1.3.0 Phase 5 CI closure, merge evidence, "
    "and v1.2.0 historical preservation verified."
)
