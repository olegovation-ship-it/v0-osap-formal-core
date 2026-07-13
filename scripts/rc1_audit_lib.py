
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

EXPECTED_IDS = [f"T{i}" for i in range(121, 157)]
CONDITIONAL_IDS = {"T140", "T150", "T156"}
IMMUTABLE_TAG = "v1.2.0"
IMMUTABLE_DOI = "10.5281/zenodo.21306969"
ACCEPTED_PARITY = {
    "ACCEPTED_CI_PASS",
    "VERIFIED",
    "STRUCTURAL_RECORD_PARITY_VERIFIED",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def rc1_hash_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "theorem_id": record.get("theorem_id"),
        "canonical_name": record.get("canonical_name"),
        "formal_signature": record.get("formal_signature"),
        "assumptions": record.get("assumptions", []),
        "conclusion": record.get("conclusion"),
        "lean_symbol": record.get("lean_symbol"),
        "coq_symbol": record.get("coq_symbol"),
        "validator_mapping": record.get("validator_mapping"),
        "claim_class": record.get("claim_class"),
        "normative_status": record.get("normative_status"),
        "conditional": record.get("conditional", False),
        "limitation": record.get("limitation"),
    }


def expected_normative_status(theorem_id: str) -> str:
    number = int(theorem_id[1:])
    if number <= 150:
        return "NORMATIVE_V1_1_RESERVED"
    return "POST_V1_1_EXPLICIT_EXTENSION"


def audit_inventory(document: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    records = document.get("records")
    if not isinstance(records, list):
        return ["THEOREM_RECORDS_REQUIRED"]

    ids = [record.get("theorem_id") for record in records if isinstance(record, dict)]
    if ids != EXPECTED_IDS:
        if sorted(set(ids)) != EXPECTED_IDS or len(ids) != len(EXPECTED_IDS):
            diagnostics.append("THEOREM_COVERAGE_MISMATCH")
        elif ids != EXPECTED_IDS:
            diagnostics.append("THEOREM_ORDER_MISMATCH")

    if len(ids) != len(set(ids)):
        diagnostics.append("DUPLICATE_THEOREM_ID")

    for record in records:
        if not isinstance(record, dict):
            diagnostics.append("MALFORMED_THEOREM_RECORD")
            continue
        tid = record.get("theorem_id")
        if tid not in EXPECTED_IDS:
            diagnostics.append("THEOREM_ID_OUTSIDE_RC1_SCOPE")
            continue

        if not record.get("canonical_name"):
            diagnostics.append("CANONICAL_NAME_REQUIRED")
        if not record.get("formal_signature"):
            diagnostics.append("FORMAL_SIGNATURE_REQUIRED")
        if not isinstance(record.get("assumptions"), list):
            diagnostics.append("ASSUMPTION_LIST_REQUIRED")
        if not record.get("conclusion"):
            diagnostics.append("CONCLUSION_REQUIRED")
        if not record.get("lean_symbol"):
            diagnostics.append("LEAN_SYMBOL_REQUIRED")
        if not record.get("coq_symbol"):
            diagnostics.append("COQ_SYMBOL_REQUIRED")
        if not record.get("limitation"):
            diagnostics.append("LIMITATION_REQUIRED")
        if not record.get("positive_fixture"):
            diagnostics.append("POSITIVE_FIXTURE_REQUIRED")
        if not record.get("countermodel_fixture"):
            diagnostics.append("COUNTERMODEL_FIXTURE_REQUIRED")

        if record.get("parity_status") not in ACCEPTED_PARITY:
            diagnostics.append("PARITY_STATUS_NOT_ACCEPTED")

        if record.get("normative_status") != expected_normative_status(tid):
            diagnostics.append("EXTENSION_CLASSIFICATION_MISMATCH")

        required_conditional = tid in CONDITIONAL_IDS
        if bool(record.get("conditional")) != required_conditional:
            diagnostics.append("CONDITIONALITY_FIREWALL_FAILURE")
        if required_conditional and record.get("claim_class") != "CONDITIONAL_THEOREM":
            diagnostics.append("CONDITIONALITY_FIREWALL_FAILURE")

        expected_hash = sha256_json(rc1_hash_payload(record))
        if record.get("rc1_record_sha256") != expected_hash:
            diagnostics.append("RC1_RECORD_HASH_MISMATCH")

    metadata = document.get("release_metadata", {})
    if metadata.get("immutable_tag") != IMMUTABLE_TAG:
        diagnostics.append("IMMUTABLE_TAG_MISMATCH")
    if metadata.get("immutable_doi") != IMMUTABLE_DOI:
        diagnostics.append("IMMUTABLE_DOI_MISMATCH")
    if metadata.get("checker_completeness_claimed") is True:
        diagnostics.append("FORBIDDEN_COMPLETENESS_CLAIM")
    if metadata.get("v1_3_0_released") is True:
        diagnostics.append("PREMATURE_RELEASE_CLAIM")

    return sorted(set(diagnostics))


def apply_mutation(document: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(document)
    kind = mutation["mutation"]
    target = mutation.get("target")
    records = mutated["records"]

    if kind == "missing_theorem_record":
        mutated["records"] = [r for r in records if r["theorem_id"] != target]
    elif kind == "duplicate_theorem_id":
        record = next(r for r in records if r["theorem_id"] == target)
        mutated["records"].insert(records.index(record) + 1, copy.deepcopy(record))
    elif kind == "stale_parity_status":
        next(r for r in records if r["theorem_id"] == target)["parity_status"] = "PATCH_READY_CI_PENDING"
    elif kind == "missing_lean_symbol":
        next(r for r in records if r["theorem_id"] == target)["lean_symbol"] = ""
    elif kind == "missing_coq_symbol":
        next(r for r in records if r["theorem_id"] == target)["coq_symbol"] = ""
    elif kind == "rc1_hash_mismatch":
        next(r for r in records if r["theorem_id"] == target)["rc1_record_sha256"] = "0" * 64
    elif kind == "extension_misclassified_normative":
        next(r for r in records if r["theorem_id"] == target)["normative_status"] = "NORMATIVE_V1_1_RESERVED"
    elif kind == "conditionality_removed":
        record = next(r for r in records if r["theorem_id"] == target)
        record["conditional"] = False
        record["claim_class"] = "PROVED_THEOREM"
        record["rc1_record_sha256"] = sha256_json(rc1_hash_payload(record))
    elif kind == "immutable_doi_changed":
        mutated["release_metadata"]["immutable_doi"] = "10.5281/zenodo.invalid"
    elif kind == "immutable_tag_changed":
        mutated["release_metadata"]["immutable_tag"] = "v1.2.0-moved"
    elif kind == "checker_completeness_claimed":
        mutated["release_metadata"]["checker_completeness_claimed"] = True
    elif kind == "released_flag_true":
        mutated["release_metadata"]["v1_3_0_released"] = True
    else:
        raise ValueError(f"Unknown mutation: {kind}")

    return mutated
