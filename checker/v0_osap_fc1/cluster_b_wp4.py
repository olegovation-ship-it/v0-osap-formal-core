"""Gate 3 Cluster B WP4 dual-backend proof-evidence activation.

This module is additive. It does not mutate WP3 bindings, V0-IPEC v0.1,
canonical theorem records, or any release state.
"""
from __future__ import annotations
import hashlib
import json
from copy import deepcopy
from typing import Any

ACTIVATION_VERSION = "v0-osap-cluster-b-wp4/0.1.0.dev1"
BASELINE = "c90041d3da5b680b574b910de50d8769d32fbfa9"
EXTENSION_THEOREMS = {"T157", "T158", "T159", "T160", "T161", "T162"}
IPEC_OUTCOMES = {
    "BACKEND_PARITY_FAILURE", "REJECTED_BRANCH_PROMOTION",
    "REJECTED_NONELIM_OBSTRUCTION", "REJECTED_LIVE_RESIDUAL",
    "REJECTED_DLE_FAILURE", "REJECTED_GUARD_FAILURE",
    "INCONCLUSIVE_UNSUPPORTED_FRAGMENT", "CERTIFIED"
}
LOCKED_HASHES = {"T157": "4afc76d031b69016587e0ce65ce3e5d06a3ab9dc864828759ccd94c44889efd2", "T158": "1188ecbe6b4e53ebd061be7350c49aa1d06feb4c9cd270f992ec95e0e170449f", "T159": "19478447c22ed4202b7a6c765bf49f019846f209e310a7e18452795d0c46201d", "T160": "7f78c6738c09425a3aaea7560ce5c21aca1bed9341155de64abb7540d0220f37", "T161": "2fcb4a46f4f67bfc71b33f01f8f29d4c39f0b1491c4a620387c50da866c6663e", "T162": "bd9fcaae0841f163733ce3444cfd23407e82de181ffb745b4e434cc00d9bcf4b"}

class ActivationError(ValueError):
    pass

def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ActivationError(message)

def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def _proof_index(proof_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _require(proof_manifest.get("baseline") == BASELINE, "proof manifest baseline mismatch")
    records = proof_manifest.get("theorems")
    _require(isinstance(records, list), "proof manifest theorem list missing")
    index: dict[str, dict[str, Any]] = {}
    for record in records:
        _require(isinstance(record, dict), "malformed proof record")
        theorem_id = record.get("theorem_id")
        _require(theorem_id in EXTENSION_THEOREMS, "undeclared proof theorem")
        _require(theorem_id not in index, "duplicate proof theorem")
        index[theorem_id] = record
    _require(set(index) == EXTENSION_THEOREMS, "proof manifest theorem coverage mismatch")
    return index

def _proof_state(theorem_ids: list[str], index: dict[str, dict[str, Any]]) -> tuple[bool, bool, list[str]]:
    extension = sorted(set(theorem_ids) & EXTENSION_THEOREMS)
    missing: list[str] = []
    parity_failure = False
    for theorem_id in extension:
        record = index[theorem_id]
        if record.get("statement_sha256") != LOCKED_HASHES[theorem_id]:
            parity_failure = True
        if record.get("parity_status") != "PASS":
            parity_failure = True
        for backend in ("lean", "coq"):
            evidence = record.get(backend)
            if not isinstance(evidence, dict) or evidence.get("status") != "PROVED" or not evidence.get("symbol") or not evidence.get("source"):
                missing.append(f"{theorem_id}:{backend}")
    return not missing and not parity_failure, parity_failure, missing

def activate_wp3_binding(binding: dict[str, Any], proof_manifest: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(binding, dict), "binding must be an object")
    theorem_lineage = binding.get("theorem_lineage")
    _require(isinstance(theorem_lineage, list) and theorem_lineage, "nonprocedural binding requires theorem lineage")
    _require(all(isinstance(t, str) and t for t in theorem_lineage), "invalid theorem lineage")
    _require(binding.get("typed_outcome_code") in IPEC_OUTCOMES, "unknown WP3 typed outcome")
    _require(binding.get("candidate_outcome_code") in IPEC_OUTCOMES, "unknown WP3 candidate outcome")
    _require(binding.get("certification_claimed") is False, "WP3 input must retain its no-certification boundary")
    index = _proof_index(proof_manifest)
    ready, parity_failure, missing = _proof_state(theorem_lineage, index)
    source_status = binding.get("source_status")
    candidate = binding["candidate_outcome_code"]
    current = binding["typed_outcome_code"]
    extension = sorted(set(theorem_lineage) & EXTENSION_THEOREMS)

    if parity_failure:
        actual = "BACKEND_PARITY_FAILURE"
        status = "WP4_BACKEND_PARITY_FAILURE"
        certified = False
        basis = ["LOCKED_STATEMENT_HASH_OR_BACKEND_PARITY_FAILURE"]
    elif source_status == "DEFERRED":
        actual = "INCONCLUSIVE_UNSUPPORTED_FRAGMENT"
        status = "WP4_SOURCE_REMAINS_DEFERRED"
        certified = False
        basis = ["SOURCE_RESULT_DEFERRED_OR_UNSUPPORTED"]
    elif not ready and extension:
        actual = "INCONCLUSIVE_UNSUPPORTED_FRAGMENT"
        status = "WP4_PROOF_EVIDENCE_INCOMPLETE"
        certified = False
        basis = ["MISSING_DUAL_BACKEND_EVIDENCE:" + ",".join(missing)]
    elif source_status == "PASS":
        _require(candidate == "CERTIFIED", "PASS candidate must be CERTIFIED")
        actual = "CERTIFIED"
        status = "WP4_DUAL_BACKEND_CERTIFICATION_ACTIVATED"
        certified = True
        basis = ["EXACT_THEOREM_LINEAGE", "LEAN4_PROVED", "COQ_PROVED", "STATEMENT_PARITY_PASS"]
    elif source_status == "REJECT" and extension:
        _require(candidate != "CERTIFIED", "REJECT candidate cannot be CERTIFIED")
        actual = candidate
        status = "WP4_EXTENSION_THEOREM_REJECTION_ACTIVATED"
        certified = False
        basis = ["EXTENSION_THEOREM_DUAL_BACKEND_EVIDENCE", "STATEMENT_PARITY_PASS"]
    else:
        actual = current
        status = "WP4_FROZEN_THEOREM_OUTCOME_PRESERVED"
        certified = False
        basis = ["NO_EXTENSION_PROOF_ACTIVATION_REQUIRED"]

    body = {
        "activation_version": ACTIVATION_VERSION,
        "baseline": BASELINE,
        "source_binding_id": binding.get("binding_id"),
        "source_fixture_id": binding.get("source_fixture_id"),
        "source_status": source_status,
        "theorem_lineage": list(theorem_lineage),
        "extension_theorem_lineage": extension,
        "candidate_outcome_code": candidate,
        "wp3_outcome_code": current,
        "typed_outcome_code": actual,
        "certification_claimed": certified,
        "activation_status": status,
        "resolution_basis": basis,
        "missing_proof_evidence": missing,
        "frozen_wp3_binding_modified": False,
        "frozen_ipec_v0_1_modified": False,
        "release_action_authorized": False,
        "proof_evidence_refs": [
            {
                "theorem_id": theorem_id,
                "statement_sha256": index[theorem_id]["statement_sha256"],
                "lean_symbol": index[theorem_id]["lean"]["symbol"],
                "coq_symbol": index[theorem_id]["coq"]["symbol"],
                "parity_status": index[theorem_id]["parity_status"],
            }
            for theorem_id in extension
        ],
    }
    integrity = hashlib.sha256(_canonical_bytes(body)).hexdigest()
    return {"activation_id": "WP4-ACT-" + integrity[:24], **deepcopy(body), "activation_integrity_sha256": integrity}
