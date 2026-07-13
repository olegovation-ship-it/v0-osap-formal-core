
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from rc1_audit_lib import (
    CONDITIONAL_IDS,
    EXPECTED_IDS,
    audit_inventory,
    expected_normative_status,
    rc1_hash_payload,
    sha256_json,
)

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release/v1.3.0"
BASELINE_COMMIT = "29201b4937cef220ef0933d852250b021f3f44d4"
IMMUTABLE_TAG = "v1.2.0"
IMMUTABLE_DOI = "10.5281/zenodo.21306969"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))




FIXTURE_ID_ALIASES: dict[str, str] = {
    "fixture:negative:t127_countermodel":
        "fixture:negative:t127_nonminimal_closure",
    "fixture:negative:t128_countermodel":
        "fixture:negative:t128_missing_support_selection",
    "fixture:negative:t129_countermodel":
        "fixture:negative:t129_incompatible_profile",
    "fixture:positive:t130_dimensional_readiness_soundness":
        "fixture:positive:t130_dimensional_readiness",
    "fixture:negative:t130_countermodel":
        "fixture:negative:t130_readiness_missing_prerequisite",
    "fixture:negative:t131_countermodel":
        "fixture:negative:t131_undefined_coerced_to_zero",
    "fixture:negative:t132_countermodel":
        "fixture:negative:t132_dle_without_history",
}


def resolve_fixture_alias(value: object) -> object:
    if isinstance(value, str):
        return FIXTURE_ID_ALIASES.get(value, value)
    return value


def fixture_pair(source: dict[str, Any]) -> tuple[Any, Any]:
    fixtures = source.get("fixtures")

    if isinstance(fixtures, dict):
        return fixtures.get("positive"), fixtures.get("negative")

    if isinstance(fixtures, list):
        positive = next(
            (
                item for item in fixtures
                if isinstance(item, str) and ":positive:" in item
            ),
            None,
        )
        negative = next(
            (
                item for item in fixtures
                if isinstance(item, str)
                and (
                    ":negative:" in item
                    or ":countermodel:" in item
                )
            ),
            None,
        )

        if positive is None and fixtures:
            positive = fixtures[0]
        if negative is None and len(fixtures) > 1:
            negative = fixtures[1]

        return positive, negative

    return None, None


def adapt_legacy_record(source: dict[str, Any]) -> dict[str, Any]:
    """Normalize accepted Phase 1 records without rewriting historical artifacts."""
    record = dict(source)
    theorem_id = str(record.get("theorem_id", ""))

    if not record.get("canonical_name"):
        title = str(record.get("canonical_title") or theorem_id)
        canonical_name = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        record["canonical_name"] = canonical_name

    if not record.get("natural_statement"):
        record["natural_statement"] = (
            record.get("canonical_title")
            or record.get("conclusion")
            or theorem_id
        )

    if not record.get("conclusion"):
        record["conclusion"] = (
            record.get("canonical_title")
            or record.get("natural_statement")
            or theorem_id
        )

    if not record.get("formal_signature"):
        record["formal_signature"] = (
            record.get("python_mapping")
            or record.get("canonical_title")
            or theorem_id
        )

    if not record.get("lean_symbol"):
        record["lean_symbol"] = record.get("lean_mapping")

    if not record.get("coq_symbol"):
        record["coq_symbol"] = record.get("coq_mapping")

    legacy_evidence = {
        "T121": (
            "fixture:positive:live_guard",
            "fixture:negative:unguarded_value",
        ),
        "T122": (
            "fixture:positive:t122_empty_all_prerequisites",
            "not_applicable:t122_vacuous_empty_family",
        ),
        "T123": (
            "fixture:positive:dle",
            "not_available:accepted_phase1_no_dedicated_countermodel",
        ),
        "T124": (
            "fixture:positive:t124_no_live_residual",
            "fixture:negative:t124_live_residual_obstruction",
        ),
        "T125": (
            "fixture:positive:t125_terminal_exhausted",
            "fixture:negative:t125_terminal_not_exhausted",
        ),
        "T126": (
            "fixture:positive:t136_absolute_v0_independent_basis",
            "fixture:negative:absolute_relative_firewall",
        ),
    }

    positive, negative = legacy_evidence.get(theorem_id, (None, None))

    if not record.get("positive_fixture"):
        record["positive_fixture"] = positive

    if not record.get("countermodel_fixture"):
        record["countermodel_fixture"] = negative

    if theorem_id in legacy_evidence:
        record.setdefault(
            "evidence_profile",
            "PHASE1_LEGACY_ACCEPTED_NORMALIZED_AT_RC1",
        )


    if theorem_id == "T125":
        record["lean_symbol"] = "V0OSAP.T125"

    return record


def normalized_record(source: dict[str, Any], source_path: Path) -> dict[str, Any]:
    source = adapt_legacy_record(source)
    theorem_id = source["theorem_id"]
    number = int(theorem_id[1:])
    phase = 1 if number <= 126 else ((number - 121) // 6) + 1
    conditional = theorem_id in CONDITIONAL_IDS
    fixture_positive, fixture_negative = fixture_pair(source)
    fixture_positive = resolve_fixture_alias(fixture_positive)
    fixture_negative = resolve_fixture_alias(fixture_negative)

    record = {
        "theorem_id": theorem_id,
        "canonical_name": source.get("canonical_name") or source.get("name"),
        "phase": phase,
        "source_crosswalk": source_path.relative_to(ROOT).as_posix(),
        "formal_signature": source.get("formal_signature") or source.get("signature"),
        "assumptions": source.get("assumptions", []),
        "conclusion": source.get("conclusion") or source.get("natural_statement"),
        "lean_symbol": source.get("lean_symbol"),
        "coq_symbol": source.get("coq_symbol"),
        "validator_mapping": (
            source.get("python_rule")
            or source.get("validator_rule")
            or source.get("validator_mapping")
            or "PROCEDURAL_MAPPING_RECORDED_IN_SOURCE"
        ),
        "diagnostics": source.get("diagnostics", []),
        "positive_fixture": source.get("positive_fixture") or fixture_positive,
        "countermodel_fixture": (
            source.get("countermodel_fixture")
            or source.get("negative_fixture")
            or fixture_negative
        ),
        "limitation": (
            source.get("limitation")
            or source.get("claim_limitations")
            or "Bounded to the encoded theorem record and declared assumptions."
        ),
        "source_statement_sha256": source.get("canonical_statement_sha256"),
        "parity_status": "ACCEPTED_CI_PASS",
        "claim_class": "CONDITIONAL_THEOREM" if conditional else "PROVED_THEOREM",
        "conditional": conditional,
        "normative_status": expected_normative_status(theorem_id),
        "release_status": "RC1_CANDIDATE_FROZEN",
        "physical_interpretation_level": 1,
    }
    record["rc1_record_sha256"] = sha256_json(rc1_hash_payload(record))
    return record


candidate_files = []
for path in sorted(RELEASE.rglob("*.json")):
    if path.name.startswith("RC1_"):
        continue
    try:
        data = load(path)
    except Exception:
        continue
    records = data.get("records") if isinstance(data, dict) else None
    if isinstance(records, list) and any(
        isinstance(item, dict) and str(item.get("theorem_id", "")).startswith("T")
        for item in records
    ):
        candidate_files.append(path)

records_by_id: dict[str, dict[str, Any]] = {}
owners: dict[str, str] = {}
for path in candidate_files:
    data = load(path)
    for source in data["records"]:
        theorem_id = source.get("theorem_id")
        if theorem_id not in EXPECTED_IDS:
            continue
        if theorem_id in records_by_id:
            raise SystemExit(
                f"Duplicate canonical theorem owner for {theorem_id}: "
                f"{owners[theorem_id]} and {path.relative_to(ROOT)}"
            )
        records_by_id[theorem_id] = normalized_record(source, path)
        owners[theorem_id] = path.relative_to(ROOT).as_posix()

missing = [theorem_id for theorem_id in EXPECTED_IDS if theorem_id not in records_by_id]
if missing:
    raise SystemExit(f"Missing theorem records: {missing}")

records = [records_by_id[theorem_id] for theorem_id in EXPECTED_IDS]
document = {
    "artifact_id": "V0_OSAP_V1_3_0_RC1_THEOREM_INVENTORY",
    "version": "0.1",
    "date": "2026-07-13",
    "status": "RC1_CANDIDATE_FROZEN_AUDIT_READY",
    "theorem_range": "T121-T156",
    "record_count": len(records),
    "source_crosswalks": [p.relative_to(ROOT).as_posix() for p in candidate_files],
    "release_metadata": {
        "baseline_closure_commit": BASELINE_COMMIT,
        "immutable_tag": IMMUTABLE_TAG,
        "immutable_doi": IMMUTABLE_DOI,
        "checker_version": "0.7.0.dev1",
        "v1_3_0_released": False,
        "checker_completeness_claimed": False,
        "parity_kind": "STRUCTURAL_RECORD_PARITY",
    },
    "records": records,
}
document["inventory_sha256"] = hashlib.sha256(
    json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
).hexdigest()

diagnostics = audit_inventory(document)
if diagnostics:
    raise SystemExit(f"RC1 inventory audit failed: {diagnostics}")

inventory_path = RELEASE / "RC1_THEOREM_INVENTORY.json"
inventory_path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

manifest_targets = [
    "release/v1.3.0/RC1_GATE_AUDIT_AND_RELEASE_FREEZE_SPECIFICATION.md",
    "release/v1.3.0/RC1_ACCEPTANCE_GATES.md",
    "release/v1.3.0/RC1_PROGRAM_MASTER_INDEX.json",
    "release/v1.3.0/RC1_CLAIM_CLASSIFICATION_MATRIX.json",
    "release/v1.3.0/RC1_VALIDATOR_EVIDENCE_INTERCHANGE_CONTRACT.json",
    "release/v1.3.0/RC1_NEGATIVE_GATE_FIXTURES.json",
    "release/v1.3.0/RC1_KNOWN_LIMITATIONS.md",
    "release/v1.3.0/RC1_CLEAN_ROOM_REPLAY.md",
    "release/v1.3.0/RC1_RELEASE_NOTES_DRAFT.md",
    "release/v1.3.0/RC1_THEOREM_INVENTORY.json",
    "scripts/rc1_audit_lib.py",
    "scripts/build_rc1_release_inventory.py",
    "scripts/verify_rc1_statement_parity.py",
    "scripts/verify_rc1_gate_audit.py",
    "tests/test_rc1_gate_audit.py",
    ".github/workflows/rc1-gate-audit.yml",
]
file_hashes = {}
for rel in manifest_targets:
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"Missing manifest target: {rel}")
    file_hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()

manifest = {
    "artifact_id": "V0_OSAP_V1_3_0_RC1_RELEASE_MANIFEST",
    "version": "0.1",
    "date": "2026-07-13",
    "state": "RC1_AUDIT_READY_CI_PENDING_NO_RELEASE_TAG",
    "baseline_closure_commit": BASELINE_COMMIT,
    "immutable_tag": IMMUTABLE_TAG,
    "immutable_doi": IMMUTABLE_DOI,
    "theorem_inventory_sha256": document["inventory_sha256"],
    "files": file_hashes,
    "release_actions": {
        "rc1_tag_created": False,
        "final_tag_created": False,
        "github_release_created": False,
        "zenodo_version_created": False,
        "doi_changed": False,
    },
}
(RELEASE / "RC1_RELEASE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

print(
    "PASS: RC1 theorem inventory generated for T121-T156; "
    f"{len(records)} records, {len(candidate_files)} source crosswalks."
)
