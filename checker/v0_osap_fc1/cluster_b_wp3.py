"""Gate 3 Cluster B WP3 — exact V0-IPEC v0.1 typed-outcome binding.

The module consumes locked WP2 result envelopes. It does not mutate WP2, V0-IPEC
v0.1, proof status, or release state. Certification and extension-theorem rejection
remain deferred until WP4 binds required proof evidence.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

BINDING_VERSION = "v0-osap-cluster-b-wp3/0.1.0.dev1"
SOURCE_VERSION = "v0-osap-cluster-b-wp2/0.1.0.dev1"
IPEC_CONTRACT_ID = "V0-IPEC-0.1"
IPEC_FROZEN_COMMIT = "5474a2c6a3e1c274d17f674889d427c1c91572f7"
EXTENSION_THEOREMS = {"T157", "T158", "T159", "T160", "T161", "T162"}

OUTCOME_META = {'BACKEND_PARITY_FAILURE': {'priority': 700, 'logical_verdict': 'VIOLATED'}, 'REJECTED_BRANCH_PROMOTION': {'priority': 650, 'logical_verdict': 'VIOLATED'}, 'REJECTED_NONELIM_OBSTRUCTION': {'priority': 600, 'logical_verdict': 'VIOLATED'}, 'REJECTED_LIVE_RESIDUAL': {'priority': 550, 'logical_verdict': 'VIOLATED'}, 'REJECTED_DLE_FAILURE': {'priority': 500, 'logical_verdict': 'VIOLATED'}, 'REJECTED_GUARD_FAILURE': {'priority': 450, 'logical_verdict': 'VIOLATED'}, 'INCONCLUSIVE_UNSUPPORTED_FRAGMENT': {'priority': 300, 'logical_verdict': 'INCONCLUSIVE'}, 'CERTIFIED': {'priority': 0, 'logical_verdict': 'SATISFIED'}}

CASE_PROFILES = {'DLE_TRANSITION': {'theorem_ids': ['T123', 'T132'], 'role_ids': ['CB-R1']}, 'STRONG_DLE': {'theorem_ids': ['T157'], 'role_ids': ['CB-R1', 'CB-R2']}, 'RESIDUAL_PERSISTENCE': {'theorem_ids': ['T158', 'T162'], 'role_ids': ['CB-R3']}, 'RESIDUAL_TYPE_SEPARATION': {'theorem_ids': ['T159'], 'role_ids': ['CB-R5']}, 'MODEL_PAIR_NONELIMINABILITY': {'theorem_ids': ['T159', 'T160'], 'role_ids': ['CB-R5']}, 'MINIMAL_RESIDUAL_OBSTRUCTION': {'theorem_ids': ['T161'], 'role_ids': ['CB-R4']}, 'HISTORICAL_TOKEN_NONCONVERSION': {'theorem_ids': ['T162'], 'role_ids': ['CB-R3']}, 'ROBUST_OBSTRUCTION': {'theorem_ids': ['T124', 'T135'], 'role_ids': ['CB-R6']}, 'BRANCH_LOCAL_FIREWALL': {'theorem_ids': ['T126', 'T136', 'T142'], 'role_ids': ['CB-R7']}}
RULES = {'T123': {'rule_id': 'IPEC.RULE.DLE.001', 'candidate_violation_outcome': 'REJECTED_DLE_FAILURE', 'rule_class': 'FROZEN_IPEC_V0_1'}, 'T132': {'rule_id': 'IPEC.RULE.DLE.002', 'candidate_violation_outcome': 'REJECTED_DLE_FAILURE', 'rule_class': 'FROZEN_IPEC_V0_1'}, 'T124': {'rule_id': 'IPEC.RULE.RESIDUAL.001', 'candidate_violation_outcome': 'REJECTED_LIVE_RESIDUAL', 'rule_class': 'FROZEN_IPEC_V0_1'}, 'T135': {'rule_id': 'IPEC.RULE.RESIDUAL.003', 'candidate_violation_outcome': 'REJECTED_NONELIM_OBSTRUCTION', 'rule_class': 'FROZEN_IPEC_V0_1'}, 'T126': {'rule_id': 'IPEC.RULE.FIREWALL.001', 'candidate_violation_outcome': 'REJECTED_BRANCH_PROMOTION', 'rule_class': 'FROZEN_IPEC_V0_1'}, 'T136': {'rule_id': 'IPEC.RULE.FIREWALL.002', 'candidate_violation_outcome': 'REJECTED_BRANCH_PROMOTION', 'rule_class': 'FROZEN_IPEC_V0_1'}, 'T142': {'rule_id': 'IPEC.RULE.BRANCH.001', 'candidate_violation_outcome': 'REJECTED_BRANCH_PROMOTION', 'rule_class': 'FROZEN_IPEC_V0_1'}, 'T157': {'rule_id': 'IPEC.EXT.GATE3.CLUSTER_B.RULE.T157', 'candidate_violation_outcome': 'REJECTED_DLE_FAILURE', 'rule_class': 'GATE3_CLUSTER_B_EXTENSION'}, 'T158': {'rule_id': 'IPEC.EXT.GATE3.CLUSTER_B.RULE.T158', 'candidate_violation_outcome': 'REJECTED_LIVE_RESIDUAL', 'rule_class': 'GATE3_CLUSTER_B_EXTENSION'}, 'T159': {'rule_id': 'IPEC.EXT.GATE3.CLUSTER_B.RULE.T159', 'candidate_violation_outcome': 'REJECTED_GUARD_FAILURE', 'rule_class': 'GATE3_CLUSTER_B_EXTENSION'}, 'T160': {'rule_id': 'IPEC.EXT.GATE3.CLUSTER_B.RULE.T160', 'candidate_violation_outcome': 'REJECTED_NONELIM_OBSTRUCTION', 'rule_class': 'GATE3_CLUSTER_B_EXTENSION'}, 'T161': {'rule_id': 'IPEC.EXT.GATE3.CLUSTER_B.RULE.T161', 'candidate_violation_outcome': 'REJECTED_LIVE_RESIDUAL', 'rule_class': 'GATE3_CLUSTER_B_EXTENSION'}, 'T162': {'rule_id': 'IPEC.EXT.GATE3.CLUSTER_B.RULE.T162', 'candidate_violation_outcome': 'REJECTED_GUARD_FAILURE', 'rule_class': 'GATE3_CLUSTER_B_EXTENSION'}}


class BindingError(ValueError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BindingError(message)


def _validate_source(result: dict[str, Any]) -> None:
    required = {"fixture_id", "case_type", "status", "accepted", "theorem_ids", "role_ids", "diagnostics", "diagnostic_codes", "derived", "implementation_version", "proof_claimed", "ipec_binding_claimed", "release_action_authorized"}
    _require(isinstance(result, dict) and set(result) == required, "source result fields do not match the locked WP2 envelope")
    _require(result["implementation_version"] == SOURCE_VERSION, "unexpected WP2 implementation version")
    _require(result["case_type"] in CASE_PROFILES, "undeclared WP2 case type")
    _require(result["status"] in {"PASS", "DEFERRED", "REJECT"}, "invalid WP2 status")
    _require(result["accepted"] is (result["status"] == "PASS"), "accepted/status mismatch")
    _require(result["proof_claimed"] is False and result["ipec_binding_claimed"] is False and result["release_action_authorized"] is False, "source nonclaim boundary violated")
    profile = CASE_PROFILES[result["case_type"]]
    _require(result["theorem_ids"] == profile["theorem_ids"], "exact theorem lineage mismatch")
    _require(result["role_ids"] == profile["role_ids"], "exact role lineage mismatch")
    diagnostics = result["diagnostics"]
    _require(isinstance(diagnostics, list), "diagnostics must be a list")
    _require(result["diagnostic_codes"] == [d.get("code") for d in diagnostics], "diagnostic-code order mismatch")
    for d in diagnostics:
        _require(isinstance(d, dict) and set(d) == {"code", "status", "message", "refs"}, "malformed diagnostic")
        _require(d["status"] in {"DEFERRED", "REJECT"} and isinstance(d["code"], str) and d["code"] and isinstance(d["message"], str) and d["message"] and isinstance(d["refs"], list), "invalid diagnostic")
    if result["status"] == "PASS":
        _require(not diagnostics, "PASS may not carry non-PASS diagnostics")
    else:
        _require(bool(diagnostics), "DEFERRED/REJECT requires diagnostics")
        _require(max((0 if d["status"] == "DEFERRED" else 1) for d in diagnostics) == (0 if result["status"] == "DEFERRED" else 1), "diagnostic/source status mismatch")


def _validate_evidence(result: dict[str, Any], evidence: list[dict[str, Any]]) -> None:
    _require(isinstance(evidence, list) and evidence, "nonprocedural outcome requires evidence lineage")
    ids = []
    source_hash = _sha256(result)
    matched_source = False
    for item in evidence:
        _require(isinstance(item, dict) and set(item) == {"evidence_id", "kind", "uri", "sha256"}, "evidence fields mismatch")
        _require(item["kind"] in {"source_result", "fixture", "certificate", "manifest", "diagnostic"}, "unsupported evidence kind")
        _require(isinstance(item["evidence_id"], str) and item["evidence_id"] and isinstance(item["uri"], str) and item["uri"], "empty evidence identifier or URI")
        _require(isinstance(item["sha256"], str) and len(item["sha256"]) == 64 and all(c in "0123456789abcdef" for c in item["sha256"]), "invalid evidence SHA-256")
        ids.append(item["evidence_id"])
        if item["kind"] == "source_result" and item["sha256"] == source_hash:
            matched_source = True
    _require(len(ids) == len(set(ids)), "duplicate evidence id")
    _require(matched_source, "canonical source-result evidence is missing or mismatched")


def _candidate(result: dict[str, Any]) -> str:
    if result["status"] == "PASS":
        return "CERTIFIED"
    if result["status"] == "DEFERRED":
        return "INCONCLUSIVE_UNSUPPORTED_FRAGMENT"
    codes = [RULES[tid]["candidate_violation_outcome"] for tid in result["theorem_ids"]]
    return max(codes, key=lambda c: OUTCOME_META[c]["priority"])


def bind_wp2_result(result: dict[str, Any], evidence_lineage: list[dict[str, Any]]) -> dict[str, Any]:
    _validate_source(result)
    _validate_evidence(result, evidence_lineage)
    candidate = _candidate(result)
    extension_pending = sorted(set(result["theorem_ids"]) & EXTENSION_THEOREMS)
    if result["status"] == "REJECT" and not extension_pending:
        actual = candidate
        binding_status = "BOUND_FROZEN_THEOREM_REJECTION"
        basis = ["THEOREM_BACKED_VIOLATION_BOUND_TO_FROZEN_IPEC_V0_1"]
    elif result["status"] == "DEFERRED":
        actual = "INCONCLUSIVE_UNSUPPORTED_FRAGMENT"
        binding_status = "INCONCLUSIVE_SOURCE_DEFERRED"
        basis = ["SOURCE_RESULT_DEFERRED_OR_UNSUPPORTED"]
    else:
        actual = "INCONCLUSIVE_UNSUPPORTED_FRAGMENT"
        binding_status = "DEFERRED_TO_WP4_PROOF_ACTIVATION"
        if result["status"] == "PASS":
            basis = ["CERTIFICATION_REQUIRES_WP4_LEAN4_AND_COQ_EVIDENCE"]
        else:
            basis = ["EXTENSION_THEOREM_PROOF_ACTIVATION_PENDING:" + ",".join(extension_pending)]
    rule_lineage = [{"theorem_id": tid, **RULES[tid]} for tid in result["theorem_ids"]]
    body = {
        "binding_version": BINDING_VERSION,
        "ipec_contract_id": IPEC_CONTRACT_ID,
        "ipec_frozen_commit": IPEC_FROZEN_COMMIT,
        "source_semantics_version": SOURCE_VERSION,
        "source_fixture_id": result["fixture_id"],
        "case_type": result["case_type"],
        "source_status": result["status"],
        "typed_outcome_code": actual,
        "candidate_outcome_code": candidate,
        "logical_verdict": OUTCOME_META[actual]["logical_verdict"],
        "certification_claimed": False,
        "outcome_binding_status": binding_status,
        "resolution_basis": basis,
        "theorem_lineage": list(result["theorem_ids"]),
        "rule_lineage": rule_lineage,
        "role_lineage": list(result["role_ids"]),
        "evidence_lineage": deepcopy(evidence_lineage),
        "diagnostic_transport": deepcopy(result["diagnostics"]),
        "derived": deepcopy(result["derived"]),
        "proof_claimed": False,
        "frozen_ipec_v0_1_modified": False,
        "release_action_authorized": False,
    }
    integrity = _sha256(body)
    return {"binding_id": "WP3-BIND-" + integrity[:24], **body, "binding_integrity_sha256": integrity}
