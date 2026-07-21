"""Executable Gate 3 Cluster B WP2 semantics.

This module implements bounded finite-record semantics for the contracts locked by
WP1.  It is intentionally independent of Validator/IPEC bindings (WP3) and formal
proof modules (WP4).  It does not change the archived checker release version.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

IMPLEMENTATION_VERSION = "v0-osap-cluster-b-wp2/0.1.0.dev1"

RESIDUAL_TYPES = (
    "TARGET_PRESENCE",
    "HISTORICAL",
    "MEMORY",
    "SIGNAL",
    "CAUSAL",
    "INFORMATION",
    "GENERIC_TRACE",
)

STATUS_RANK = {"PASS": 0, "DEFERRED": 1, "REJECT": 2}


def _diag(code: str, status: str, message: str, *refs: object) -> dict[str, Any]:
    return {
        "code": code,
        "status": status,
        "message": message,
        "refs": [str(ref) for ref in refs if ref not in (None, "")],
    }


def _result(
    *,
    case_type: str,
    theorem_ids: list[str],
    role_ids: list[str],
    diagnostics: list[dict[str, Any]],
    derived: dict[str, Any],
) -> dict[str, Any]:
    status = "PASS"
    if diagnostics:
        status = max((item["status"] for item in diagnostics), key=STATUS_RANK.__getitem__)
    return {
        "case_type": case_type,
        "status": status,
        "accepted": status == "PASS",
        "theorem_ids": theorem_ids,
        "role_ids": role_ids,
        "diagnostics": diagnostics,
        "diagnostic_codes": [item["code"] for item in diagnostics],
        "derived": derived,
        "implementation_version": IMPLEMENTATION_VERSION,
        "proof_claimed": False,
        "ipec_binding_claimed": False,
        "release_action_authorized": False,
    }


def _nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_transition_provenance(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    return (
        value.get("kind") == "DLE"
        and _nonempty_text(value.get("transition_id"))
        and _nonempty_text(value.get("source_state_id"))
        and _nonempty_text(value.get("target_state_id"))
        and _nonempty_text(value.get("target_id"))
        and value.get("deterministic") is True
    )


def evaluate_dle_transition(data: dict[str, Any]) -> dict[str, Any]:
    before = data.get("before_state", {})
    after = data.get("after_state", {})
    provenance = data.get("transition_provenance")
    diagnostics: list[dict[str, Any]] = []

    before_live = bool(before.get("target_license_live")) and bool(before.get("current_live_token_ids"))
    after_exhausted = after.get("target_license_status") == "EXHAUSTED"
    after_no_live = not bool(after.get("current_live_token_ids"))
    provenance_valid = _valid_transition_provenance(provenance)

    if not before_live:
        diagnostics.append(_diag(
            "DLE_SOURCE_LIVE_STATE_MISSING", "REJECT",
            "A DLE transition requires a source state with a live target license and at least one current live token.",
            before.get("state_id"),
        ))
    if not after_exhausted or not after_no_live:
        diagnostics.append(_diag(
            "DLE_TARGET_NOT_EXHAUSTED", "REJECT",
            "The target state must have an exhausted target license and no current live token.",
            after.get("state_id"),
        ))
    if not provenance_valid:
        diagnostics.append(_diag(
            "DLE_TRANSITION_PROVENANCE_MISSING", "REJECT",
            "Typed deterministic DLE transition provenance is required.",
            (provenance or {}).get("transition_id") if isinstance(provenance, dict) else None,
        ))

    transition_valid = before_live and after_exhausted and after_no_live and provenance_valid
    return _result(
        case_type="DLE_TRANSITION",
        theorem_ids=["T123", "T132"],
        role_ids=["CB-R1"],
        diagnostics=diagnostics,
        derived={
            "source_live": before_live,
            "target_exhausted": after_exhausted,
            "target_no_live": after_no_live,
            "provenance_valid": provenance_valid,
            "dle_transition_valid": transition_valid,
        },
    )


def evaluate_strong_dle(data: dict[str, Any]) -> dict[str, Any]:
    transition = evaluate_dle_transition(data)
    witness = data.get("historical_live_witness", {})
    diagnostics = deepcopy(transition["diagnostics"])

    history_valid = (
        isinstance(witness, dict)
        and witness.get("was_live") is True
        and _nonempty_text(witness.get("token_id"))
        and witness.get("target_id") == (data.get("transition_provenance") or {}).get("target_id")
    )
    if not history_valid:
        diagnostics.append(_diag(
            "STRONG_DLE_HISTORY_MISSING", "REJECT",
            "StrongDLE requires a typed historical live witness for the same target.",
            witness.get("token_id") if isinstance(witness, dict) else None,
        ))

    after = data.get("after_state", {})
    current_no_live = (
        after.get("target_license_status") == "EXHAUSTED"
        and not bool(after.get("current_live_token_ids"))
    )
    if not current_no_live and "DLE_TARGET_NOT_EXHAUSTED" not in transition["diagnostic_codes"]:
        diagnostics.append(_diag(
            "STRONG_DLE_CURRENT_STATE_CONFLICT", "REJECT",
            "StrongDLE requires current no-live/no-license status.",
            after.get("state_id"),
        ))

    provenance_valid = transition["derived"]["provenance_valid"]
    if not provenance_valid and "DLE_TRANSITION_PROVENANCE_MISSING" not in transition["diagnostic_codes"]:
        diagnostics.append(_diag(
            "STRONG_DLE_PROVENANCE_MISSING", "REJECT",
            "StrongDLE requires explicit transition provenance.",
        ))

    strong_dle = history_valid and current_no_live and transition["derived"]["dle_transition_valid"]
    return _result(
        case_type="STRONG_DLE",
        theorem_ids=["T157"],
        role_ids=["CB-R1", "CB-R2"],
        diagnostics=diagnostics,
        derived={
            "was_live": history_valid,
            "current_no_live": current_no_live,
            "transition_provenance_valid": provenance_valid,
            "strong_dle": strong_dle,
        },
    )


def evaluate_residual_persistence(data: dict[str, Any]) -> dict[str, Any]:
    before = data.get("before_residual", {})
    after = data.get("after_residual", {})
    transition = data.get("transition", {})
    certificate = data.get("non_interference_certificate", {})
    diagnostics: list[dict[str, Any]] = []

    premise_live = before.get("live") is True and _nonempty_text(before.get("residual_id"))
    deterministic = transition.get("deterministic") is True
    certificate_valid = (
        certificate.get("present") is True
        and certificate.get("residual_id") == before.get("residual_id")
        and set(certificate.get("forbidden_effects", [])) >= {
            "DELETE", "REWRITE", "RETYPE", "IDENTITY_CHANGE"
        }
    )
    effect = transition.get("residual_effect")

    if not premise_live or not deterministic or not certificate_valid:
        diagnostics.append(_diag(
            "RESIDUAL_PERSISTENCE_PREMISE_MISSING", "DEFERRED",
            "Persistence is conditional on a live source residual, deterministic application, and an explicit non-interference certificate.",
            before.get("residual_id"),
        ))

    if effect in {"DELETE", "REWRITE", "RETYPE", "IDENTITY_CHANGE"}:
        diagnostics.append(_diag(
            "DLE_RESIDUAL_INTERFERENCE_DETECTED", "REJECT",
            "The DLE transition interferes with the residual register.",
            before.get("residual_id"), effect,
        ))

    identity_preserved = (
        before.get("residual_id") == after.get("residual_id")
        and before.get("residual_type") == after.get("residual_type")
    )
    if premise_live and not identity_preserved:
        diagnostics.append(_diag(
            "RESIDUAL_IDENTITY_CHANGED", "REJECT",
            "A persistent residual must preserve identity and residual type.",
            before.get("residual_id"), after.get("residual_id"),
        ))

    conclusion_live = after.get("live") is True
    if premise_live and certificate_valid and deterministic and effect == "PRESERVE" and identity_preserved and not conclusion_live:
        diagnostics.append(_diag(
            "RESIDUAL_PERSISTENCE_CONCLUSION_FAILED", "REJECT",
            "A certified non-interfering deterministic transition must preserve residual liveness.",
            before.get("residual_id"),
        ))

    applicable = premise_live and deterministic and certificate_valid and effect == "PRESERVE"
    persists = applicable and identity_preserved and conclusion_live
    return _result(
        case_type="RESIDUAL_PERSISTENCE",
        theorem_ids=["T158", "T162"],
        role_ids=["CB-R3"],
        diagnostics=diagnostics,
        derived={
            "premises_satisfied": applicable,
            "identity_preserved": identity_preserved,
            "residual_live_after": conclusion_live,
            "residual_persists": persists,
        },
    )


def evaluate_residual_type_separation(data: dict[str, Any]) -> dict[str, Any]:
    left = data.get("left_residual", {})
    right = data.get("right_residual", {})
    translation = data.get("translation_map", {})
    diagnostics: list[dict[str, Any]] = []

    left_type = left.get("residual_type")
    right_type = right.get("residual_type")
    if left_type not in RESIDUAL_TYPES or right_type not in RESIDUAL_TYPES:
        diagnostics.append(_diag(
            "RESIDUAL_TYPE_COLLAPSE", "REJECT",
            "Residual classes must use the canonical WP1 residual-type vocabulary.",
            left_type, right_type,
        ))

    distinct = left_type != right_type
    translation_status = translation.get("status", "ABSENT")
    admissible_translation = (
        translation_status == "ADMISSIBLE"
        and translation.get("source_type") == left_type
        and translation.get("target_type") == right_type
        and translation.get("preservation_obligations_met") is True
    )
    claimed_interchangeable = data.get("claimed_interchangeable") is True

    if distinct and not admissible_translation and claimed_interchangeable:
        diagnostics.append(_diag(
            "UNDECLARED_RESIDUAL_TRANSLATION", "REJECT",
            "Distinct residual classes cannot be treated as interchangeable without an admissible translation map.",
            left.get("residual_id"), right.get("residual_id"),
        ))

    not_interchangeable = distinct and not admissible_translation
    return _result(
        case_type="RESIDUAL_TYPE_SEPARATION",
        theorem_ids=["T159"],
        role_ids=["CB-R5"],
        diagnostics=diagnostics,
        derived={
            "types_distinct": distinct,
            "admissible_translation": admissible_translation,
            "not_interchangeable": not_interchangeable,
        },
    )


def evaluate_model_pair_noneliminability(data: dict[str, Any]) -> dict[str, Any]:
    left = data.get("model_left", {})
    right = data.get("model_right", {})
    pair = data.get("pair_certificate", {})
    diagnostics: list[dict[str, Any]] = []

    schema_valid = left.get("schema_valid") is True and right.get("schema_valid") is True
    basis = pair.get("distinctness_basis")
    distinctness_valid = (
        basis not in (None, "", "LABEL_ONLY")
        and bool(pair.get("distinctness_evidence_ids"))
        and pair.get("non_circular") is True
    )
    if not distinctness_valid:
        diagnostics.append(_diag(
            "MODEL_PAIR_DISTINCTNESS_UNSUPPORTED", "REJECT",
            "An admissible model pair requires a non-label-only, evidence-bearing, non-circular distinctness basis.",
            basis,
        ))

    shared_symbols = pair.get("shared_symbols", [])
    left_fragment = left.get("shared_fragment", {})
    right_fragment = right.get("shared_fragment", {})
    agree = bool(shared_symbols) and all(left_fragment.get(symbol) == right_fragment.get(symbol) for symbol in shared_symbols)
    if not agree:
        diagnostics.append(_diag(
            "MODEL_PAIR_SHARED_FRAGMENT_MISMATCH", "REJECT",
            "The two models must agree on every symbol in the declared shared fragment.",
            *shared_symbols,
        ))

    residual_id = pair.get("target_residual_id")
    left_residual = next((item for item in left.get("residuals", []) if item.get("residual_id") == residual_id), None)
    right_residual = next((item for item in right.get("residuals", []) if item.get("residual_id") == residual_id), None)
    typed = (
        isinstance(left_residual, dict)
        and isinstance(right_residual, dict)
        and left_residual.get("residual_type") in RESIDUAL_TYPES
        and right_residual.get("residual_type") in RESIDUAL_TYPES
        and left_residual.get("residual_type") == right_residual.get("residual_type")
    )
    residual_difference = typed and left_residual.get("live") != right_residual.get("live")
    if not residual_difference:
        diagnostics.append(_diag(
            "MODEL_PAIR_TYPED_RESIDUAL_DIFFERENCE_MISSING", "DEFERRED",
            "The model-pair witness requires a typed live-residual difference.",
            residual_id,
        ))

    admissible = schema_valid and distinctness_valid
    witness = admissible and agree and residual_difference
    if witness:
        # An informational PASS code is represented in the derived record rather than as a diagnostic,
        # preserving diagnostics as non-PASS conditions only.
        pass

    return _result(
        case_type="MODEL_PAIR_NONELIMINABILITY",
        theorem_ids=["T159", "T160"],
        role_ids=["CB-R5"],
        diagnostics=diagnostics,
        derived={
            "admissible_model_pair": admissible,
            "agree_on_shared_fragment": agree,
            "typed_residual_difference": residual_difference,
            "non_eliminable_from_shared_fragment": witness,
        },
    )


def evaluate_minimal_residual_obstruction(data: dict[str, Any]) -> dict[str, Any]:
    residual = data.get("residual", {})
    diagnostics: list[dict[str, Any]] = []
    declared = residual.get("declared") is True and _nonempty_text(residual.get("residual_id"))
    residual_type = residual.get("residual_type")
    if declared and residual_type not in RESIDUAL_TYPES:
        diagnostics.append(_diag(
            "RESIDUAL_TYPE_COLLAPSE", "REJECT",
            "A declared residual must use a canonical residual type.",
            residual_type,
        ))
    live = residual.get("live") is True
    witness = declared and live and residual_type in RESIDUAL_TYPES
    return _result(
        case_type="MINIMAL_RESIDUAL_OBSTRUCTION",
        theorem_ids=["T161"],
        role_ids=["CB-R4"],
        diagnostics=diagnostics,
        derived={
            "declared_residual": declared,
            "live_residual": live,
            "minimal_obstruction_witness": witness,
            "raw_relative_v0_blocked": witness,
            "converse_claimed": False,
            "completeness_claimed": False,
        },
    )


def evaluate_historical_token_nonconversion(data: dict[str, Any]) -> dict[str, Any]:
    historical = data.get("historical_token", {})
    current_tokens = data.get("current_tokens", [])
    activations = data.get("fresh_activations", [])
    diagnostics: list[dict[str, Any]] = []

    historical_valid = historical.get("historical") is True and _nonempty_text(historical.get("token_id"))
    source_id = historical.get("token_id")
    valid_activations = {
        (item.get("source_historical_token_id"), item.get("new_token_id")): item
        for item in activations
        if isinstance(item, dict)
        and item.get("typed") is True
        and _nonempty_text(item.get("activation_id"))
        and item.get("new_token_id") != item.get("source_historical_token_id")
    }

    current_live_ids: list[str] = []
    properly_activated_ids: list[str] = []
    for token in current_tokens:
        if not isinstance(token, dict) or token.get("live_guard") is not True:
            continue
        token_id = token.get("token_id")
        current_live_ids.append(str(token_id))
        if token_id == source_id:
            diagnostics.append(_diag(
                "HISTORICAL_TOKEN_CURRENT_CONVERSION", "REJECT",
                "The historical token itself cannot be exported as a current live token.",
                source_id,
            ))
            continue
        if token.get("source_historical_token_id") == source_id:
            activation = valid_activations.get((source_id, token_id))
            if activation is None or token.get("activation_id") != activation.get("activation_id"):
                diagnostics.append(_diag(
                    "FRESH_ACTIVATION_WITNESS_REQUIRED", "REJECT",
                    "A new current token derived from a historical source requires a matching typed fresh-activation witness.",
                    source_id, token_id,
                ))
            else:
                properly_activated_ids.append(str(token_id))

    original_converted = str(source_id) in current_live_ids
    return _result(
        case_type="HISTORICAL_TOKEN_NONCONVERSION",
        theorem_ids=["T162"],
        role_ids=["CB-R3"],
        diagnostics=diagnostics,
        derived={
            "historical_token_valid": historical_valid,
            "historical_token_became_current": original_converted,
            "freshly_activated_current_token_ids": sorted(properly_activated_ids),
            "historical_nonconversion_preserved": historical_valid and not original_converted and not diagnostics,
        },
    )


def evaluate_robust_obstruction(data: dict[str, Any]) -> dict[str, Any]:
    residual = data.get("residual", {})
    diagnostics: list[dict[str, Any]] = []
    typed = residual.get("residual_type") in RESIDUAL_TYPES
    declared = residual.get("declared") is True
    live = residual.get("live") is True
    non_eliminable = residual.get("non_eliminable") is True
    if declared and not typed:
        diagnostics.append(_diag(
            "RESIDUAL_TYPE_COLLAPSE", "REJECT",
            "Robust obstruction requires a canonically typed residual.",
            residual.get("residual_type"),
        ))
    witness = typed and declared and live and non_eliminable
    return _result(
        case_type="ROBUST_OBSTRUCTION",
        theorem_ids=["T124", "T135"],
        role_ids=["CB-R6"],
        diagnostics=diagnostics,
        derived={
            "robust_obstruction_witness": witness,
            "robust_relative_v0_blocked": witness,
        },
    )


def evaluate_branch_local_firewall(data: dict[str, Any]) -> dict[str, Any]:
    diagnostics: list[dict[str, Any]] = []
    evidence_scope = data.get("evidence_scope")
    promotion_target = data.get("promotion_target")
    basis = data.get("distinctness_basis")
    claimed_distinct = data.get("claimed_distinct") is True

    forbidden_promotion = evidence_scope in {"RELATIVE", "BRANCH_LOCAL"} and promotion_target == "ABSOLUTE_V0"
    if forbidden_promotion:
        diagnostics.append(_diag(
            "RELATIVE_TO_ABSOLUTE_PROMOTION_FORBIDDEN", "REJECT",
            "Relative or branch-local evidence cannot be promoted to absolute V0.",
            evidence_scope, promotion_target,
        ))
    if basis == "LABEL_ONLY" and claimed_distinct:
        diagnostics.append(_diag(
            "BRANCH_LABELS_DO_NOT_PROVE_DISTINCTNESS", "REJECT",
            "Different labels alone do not prove branch distinctness.",
        ))

    return _result(
        case_type="BRANCH_LOCAL_FIREWALL",
        theorem_ids=["T126", "T136", "T142"],
        role_ids=["CB-R7"],
        diagnostics=diagnostics,
        derived={
            "relative_to_absolute_promotion_blocked": forbidden_promotion,
            "label_only_distinctness_blocked": basis == "LABEL_ONLY" and claimed_distinct,
            "firewall_respected": not diagnostics,
        },
    )


EVALUATORS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "DLE_TRANSITION": evaluate_dle_transition,
    "STRONG_DLE": evaluate_strong_dle,
    "RESIDUAL_PERSISTENCE": evaluate_residual_persistence,
    "RESIDUAL_TYPE_SEPARATION": evaluate_residual_type_separation,
    "MODEL_PAIR_NONELIMINABILITY": evaluate_model_pair_noneliminability,
    "MINIMAL_RESIDUAL_OBSTRUCTION": evaluate_minimal_residual_obstruction,
    "HISTORICAL_TOKEN_NONCONVERSION": evaluate_historical_token_nonconversion,
    "ROBUST_OBSTRUCTION": evaluate_robust_obstruction,
    "BRANCH_LOCAL_FIREWALL": evaluate_branch_local_firewall,
}


def evaluate_fixture(document: dict[str, Any]) -> dict[str, Any]:
    case_type = document.get("case_type")
    evaluator = EVALUATORS.get(str(case_type))
    if evaluator is None:
        return _result(
            case_type=str(case_type),
            theorem_ids=[],
            role_ids=[],
            diagnostics=[_diag(
                "WP2_UNKNOWN_CASE_TYPE", "REJECT",
                "The fixture case type is not supported by the bounded WP2 evaluator.",
                case_type,
            )],
            derived={},
        )
    result = evaluator(document.get("input", {}))
    result["fixture_id"] = document.get("fixture_id")
    return result
