from __future__ import annotations

from collections import Counter
from typing import Any

from .canonical import canonical_sha256
from .diagnostics import Diagnostic

PHASE6_THEOREM_IDS = [f"T{i}" for i in range(151, 157)]
PHASE6_BASE_THEOREM_CEILING = 150


def _ids(*values: Any) -> tuple[str, ...]:
    return tuple(str(value) for value in values if value is not None)


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def phase6_diagnostics(claim: dict[str, Any], path: str = "/claims") -> list[Diagnostic]:
    """Return diagnostics for the T151-T156 explicit extension-governance family."""
    diagnostics: list[Diagnostic] = []
    kind = claim.get("kind")
    claim_id = claim.get("claim_id")

    if kind == "theorem_extension_provenance_audit":
        record_id = str(claim.get("extension_record_id") or "")
        namespace = str(claim.get("extension_namespace") or "")
        if not record_id or not namespace:
            diagnostics.append(Diagnostic(
                "EXTENSION_PROVENANCE_RECORD_REQUIRED",
                "REJECT",
                82,
                "A post-v1.1 theorem target requires an explicit extension record and namespace.",
                path,
                _ids(claim_id, record_id, namespace),
            ))
        if claim.get("base_theorem_ceiling") != PHASE6_BASE_THEOREM_CEILING:
            diagnostics.append(Diagnostic(
                "EXTENSION_BASE_CEILING_MISMATCH",
                "REJECT",
                81,
                "The Phase 6 extension must preserve the normative v1.1 theorem ceiling T150.",
                path,
                _ids(claim_id, claim.get("base_theorem_ceiling")),
            ))
        theorem_ids = [str(item) for item in claim.get("extension_theorem_ids", [])]
        if theorem_ids != PHASE6_THEOREM_IDS:
            diagnostics.append(Diagnostic(
                "EXTENSION_THEOREM_RANGE_MISMATCH",
                "REJECT",
                80,
                "The declared Phase 6 extension range must be exactly T151-T156 in canonical order.",
                path,
                _ids(claim_id, *theorem_ids),
            ))

    elif kind == "claim_vocabulary_closure_audit":
        observed = {str(item) for item in claim.get("observed_claim_kinds", [])}
        declared = {str(item) for item in claim.get("declared_claim_kinds", [])}
        undeclared = sorted(observed - declared)
        if undeclared:
            diagnostics.append(Diagnostic(
                "UNDECLARED_EXTENSION_CLAIM_KIND",
                "REJECT",
                79,
                "Every observed extension claim kind must belong to the declared Phase 6 vocabulary.",
                path,
                _ids(claim_id, *undeclared),
            ))

    elif kind == "diagnostic_envelope_determinism_audit":
        pinned = [
            str(claim.get("diagnostic_input_hash") or ""),
            str(claim.get("diagnostic_ruleset_hash") or ""),
        ]
        if any(len(value) != 64 for value in pinned):
            diagnostics.append(Diagnostic(
                "DIAGNOSTIC_REPLAY_INPUTS_NOT_PINNED",
                "REJECT",
                79,
                "Diagnostic-envelope replay requires pinned input and ruleset hashes.",
                path,
                _ids(claim_id, *pinned),
            ))
        first = canonical_sha256(claim.get("first_diagnostic_envelope"))
        second = canonical_sha256(claim.get("second_diagnostic_envelope"))
        if first != second:
            diagnostics.append(Diagnostic(
                "DIAGNOSTIC_ENVELOPE_NONDETERMINISTIC",
                "REJECT",
                78,
                "Pinned diagnostic evaluation must produce one canonical diagnostic envelope.",
                path,
                _ids(claim_id, first, second),
            ))

    elif kind == "evidence_provenance_acyclicity_audit":
        path_ids = [str(item) for item in claim.get("provenance_path_ids", [])]
        duplicates = _duplicates(path_ids)
        if duplicates:
            diagnostics.append(Diagnostic(
                "EVIDENCE_PROVENANCE_CYCLE",
                "REJECT",
                80,
                "A repeated identifier in an explicit finite provenance path witnesses a cycle.",
                path,
                _ids(claim_id, *duplicates),
            ))

    elif kind == "version_lock_coherence_audit":
        lock_id = str(claim.get("version_lock_id") or "")
        if not lock_id:
            diagnostics.append(Diagnostic(
                "VERSION_LOCK_RECORD_REQUIRED",
                "REJECT",
                80,
                "A compatibility assertion requires an explicit version-lock record.",
                path,
                _ids(claim_id),
            ))
        expected = (
            str(claim.get("expected_schema_version") or ""),
            str(claim.get("expected_language_version") or ""),
            str(claim.get("expected_checker_version") or ""),
            str(claim.get("expected_semantic_version") or ""),
        )
        current = (
            str(claim.get("current_schema_version") or ""),
            str(claim.get("current_language_version") or ""),
            str(claim.get("current_checker_version") or ""),
            str(claim.get("current_semantic_version") or ""),
        )
        if expected != current:
            diagnostics.append(Diagnostic(
                "VERSION_LOCK_TUPLE_MISMATCH",
                "REJECT",
                79,
                "The current schema/language/checker/semantic tuple must equal the declared lock tuple.",
                path,
                _ids(claim_id, *expected, *current),
            ))

    elif kind == "conservative_extension_audit":
        if claim.get("baseline_only_input") is True:
            premises = (
                claim.get("extension_handlers_isolated") is True
                and claim.get("baseline_rules_overridden") is False
            )
            if not premises:
                diagnostics.append(Diagnostic(
                    "CONSERVATIVE_EXTENSION_PREMISES_UNPROVED",
                    "DEFERRED",
                    79,
                    "Conservative non-interference remains conditional on handler isolation and no baseline override.",
                    path,
                    _ids(claim_id),
                ))
            else:
                baseline_hash = str(claim.get("baseline_result_hash") or "")
                extended_hash = str(claim.get("extended_result_hash") or "")
                if (
                    len(baseline_hash) != 64
                    or len(extended_hash) != 64
                    or baseline_hash != extended_hash
                ):
                    diagnostics.append(Diagnostic(
                        "BASELINE_RESULT_CHANGED_BY_EXTENSION",
                        "REJECT",
                        81,
                        "Under the stated isolation premises, a baseline-only result must be unchanged by Phase 6.",
                        path,
                        _ids(claim_id, baseline_hash, extended_hash),
                    ))

    return diagnostics
