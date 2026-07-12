from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str) -> dict:
    return json.loads(text(path))


evidence = load("release/v1.3.0/PHASE4_CI_CLOSURE_EVIDENCE.json")
crosswalk = load("release/v1.3.0/theorem_crosswalk_phase4.json")
report = text(
    "release/v1.3.0/PHASE4_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md"
)
acceptance = text("release/v1.3.0/PHASE4_ACCEPTANCE_GATES.md")
build_spec = text("release/v1.3.0/PHASE4_BUILD_SPECIFICATION.md")
implementation = text("release/v1.3.0/PHASE4_IMPLEMENTATION_REPORT.md")
readme = text("README.md")
changelog = text("CHANGELOG.md")
status = text("docs/status_and_nonclaims.md")
register = text("docs/theorem_register.md")
workflow = text(".github/workflows/release-readiness.yml")

EXPECTED_IMPLEMENTATION_BASELINE = "24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30"
EXPECTED_HEAD = "9cec516c8ab026ce8d63fd2303f72ec5c1d36351"
EXPECTED_MERGE = "417866ec94fb24891c00bdfc2e522095777532bf"
EXPECTED_DOI = "10.5281/zenodo.21306969"
EXPECTED_STATUS = "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"

assert evidence["status"] == EXPECTED_STATUS
assert evidence["theorem_range"] == "T139-T144"
assert evidence["implementation_baseline_merge_commit"] == EXPECTED_IMPLEMENTATION_BASELINE
assert evidence["pull_request"]["number"] == 6
assert evidence["pull_request"]["base"] == "main"
assert evidence["pull_request"]["head"] == "v1.3.0-development"
assert evidence["pull_request"]["head_sha"] == EXPECTED_HEAD
assert evidence["pull_request"]["merge_commit_sha"] == EXPECTED_MERGE
assert evidence["pull_request"]["merged_at_utc"] == "2026-07-12T11:04:10Z"
assert evidence["pull_request"]["pr_check_total"] == 8
assert evidence["pull_request"]["pr_check_result"] == "PASS"
assert evidence["pull_request"]["commits"] == 3
assert evidence["pull_request"]["changed_files"] == 53
assert evidence["pull_request"]["additions"] == 2481
assert evidence["pull_request"]["deletions"] == 25

assert evidence["local_validation"]["python_tests"] == 113
assert all(
    value == "PASS"
    for key, value in evidence["local_validation"].items()
    if key != "python_tests"
)

assert len(evidence["workflow_runs"]) == 5
assert all(run["conclusion"] == "success" for run in evidence["workflow_runs"])
release_run = next(run for run in evidence["workflow_runs"] if run["name"] == "Release readiness")
assert release_run["run_id"] == 29190051466
assert set(release_run["jobs"]) == {
    "immutable-v1-2-baseline",
    "v1-3-development-readiness",
}

historical = evidence["historical_preservation"]
assert historical["baseline_tag"] == "v1.2.0"
assert historical["baseline_doi"] == EXPECTED_DOI
assert historical["manifest_verifier_retained"] is True
assert historical["closure_verifier_retained"] is True
assert historical["phase1_record_retained"] is True
assert historical["phase2_record_retained"] is True
assert historical["phase3_record_retained"] is True
assert historical["branch_sync_to_merge_commit"] is True
assert historical["tag_moved_or_retagged"] is False
assert historical["new_doi_created"] is False

assert crosswalk["baseline_merge_commit"] == EXPECTED_IMPLEMENTATION_BASELINE
assert crosswalk["phase1_status"] == "ACCEPTED_CI_PASS"
assert crosswalk["phase2_status"] == "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"
assert crosswalk["phase3_status"] == "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"
assert crosswalk["phase4_status"] == "ACCEPTED_CI_PASS_MERGED"
assert crosswalk["closure_evidence"] == (
    "release/v1.3.0/PHASE4_CI_CLOSURE_EVIDENCE.json"
)
assert crosswalk["pull_request"] == 6
assert crosswalk["head_commit"] == EXPECTED_HEAD
assert crosswalk["merge_commit"] == EXPECTED_MERGE
assert crosswalk["merged_at_utc"] == "2026-07-12T11:04:10Z"
assert crosswalk["github_pr_checks"] == 8
assert crosswalk["python_tests"] == 113
assert crosswalk["historical_preservation"] == "PASS"
assert [row["theorem_id"] for row in crosswalk["records"]] == [
    f"T{i}" for i in range(139, 145)
]
assert all(row["parity_status"] == "ACCEPTED_CI_PASS" for row in crosswalk["records"])

for required in [
    "ACCEPTED / CI_PASS / MERGED / HISTORICALLY_PRESERVED",
    EXPECTED_IMPLEMENTATION_BASELINE,
    EXPECTED_HEAD,
    EXPECTED_MERGE,
    EXPECTED_DOI,
    "113 tests PASS",
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
assert "113 passing tests" in readme
accepted_boundary = re.search(
    r"No accepted theorem IDs beyond T(\d+)",
    status,
)
assert accepted_boundary is not None
assert int(accepted_boundary.group(1)) >= 144
assert (
    "Phase 4 patch status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`."
    in register
)

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
]:
    assert command in workflow

for path in [
    "README.md",
    "docs/status_and_nonclaims.md",
    "docs/theorem_register.md",
    "release/v1.3.0/PHASE4_ACCEPTANCE_GATES.md",
    "release/v1.3.0/PHASE4_BUILD_SPECIFICATION.md",
    "release/v1.3.0/PHASE4_IMPLEMENTATION_REPORT.md",
    "release/v1.3.0/theorem_crosswalk_phase4.json",
]:
    body = text(path)
    assert (
        "PHASE 4 T139-T144 ARCHIVE, BRANCH, CARDINALITY, AND DIAGNOSTIC "
        "EXPANSION - BUILD READY / CI PENDING"
    ) not in body
    assert '"phase4_status": "BUILD_READY_CI_PENDING"' not in body
    assert '"parity_status": "PATCH_READY_CI_PENDING"' not in body
    assert "CI acceptance pending" not in body

print(
    "PASS: V0 OSAP v1.3.0 Phase 4 CI closure, merge evidence, "
    "and v1.2.0 historical preservation verified."
)
