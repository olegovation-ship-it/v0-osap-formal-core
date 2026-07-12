from __future__ import annotations

from typing import Any

from .canonical import CANONICALIZATION_ID, canonical_round_trip, canonical_sha256
from .diagnostics import Diagnostic


def _ids(*values: Any) -> tuple[str, ...]:
    return tuple(str(value) for value in values if value is not None)


def phase5_diagnostics(claim: dict[str, Any], path: str = "/claims") -> list[Diagnostic]:
    """Return diagnostics for the T145-T150 Phase 5 audit claim family."""
    diagnostics: list[Diagnostic] = []
    kind = claim.get("kind")
    claim_id = claim.get("claim_id")

    if kind == "canonical_serialization_audit":
        if claim.get("canonicalization") != CANONICALIZATION_ID:
            diagnostics.append(Diagnostic(
                "CANONICALIZATION_PROFILE_MISMATCH",
                "REJECT",
                76,
                "Canonical serialization must use V0-OSAP-CJ-1.",
                path,
                _ids(claim_id, claim.get("canonicalization")),
            ))
        expected = str(claim.get("expected_canonical_sha256") or "")
        actual = canonical_sha256(claim.get("canonical_payload"))
        if expected != actual:
            diagnostics.append(Diagnostic(
                "CANONICAL_SERIALIZATION_HASH_MISMATCH",
                "REJECT",
                75,
                "The declared canonical hash disagrees with the unique V0-OSAP-CJ-1 bytes.",
                path,
                _ids(claim_id, expected, actual),
            ))

    elif kind == "round_trip_audit":
        payload = claim.get("canonical_payload")
        declared = claim.get("declared_round_trip_payload")
        actual = canonical_round_trip(payload)
        if declared != actual:
            diagnostics.append(Diagnostic(
                "ROUND_TRIP_IDENTITY_MISMATCH",
                "REJECT",
                74,
                "Canonical serialize/parse must preserve the well-formed FC-1 object.",
                path,
                _ids(claim_id),
            ))

    elif kind == "replay_determinism_audit":
        pinned = [
            str(claim.get("proof_hash") or ""),
            str(claim.get("registry_hash") or ""),
            str(claim.get("ruleset_hash") or ""),
        ]
        if any(len(value) != 64 for value in pinned):
            diagnostics.append(Diagnostic(
                "REPLAY_INPUTS_NOT_PINNED",
                "REJECT",
                74,
                "Replay determinism requires pinned proof, registry, and ruleset hashes.",
                path,
                _ids(claim_id, *pinned),
            ))
        first = canonical_sha256(claim.get("first_replay_result"))
        second = canonical_sha256(claim.get("second_replay_result"))
        if first != second:
            diagnostics.append(Diagnostic(
                "REPLAY_NONDETERMINISTIC_RESULT",
                "REJECT",
                73,
                "Pinned replay inputs must produce one canonical replay result.",
                path,
                _ids(claim_id, first, second),
            ))

    elif kind == "schema_migration_audit":
        changed = (
            claim.get("from_schema_version") != claim.get("to_schema_version")
            or claim.get("from_semantic_version") != claim.get("to_semantic_version")
        )
        if changed and claim.get("parser_coercion") is True:
            diagnostics.append(Diagnostic(
                "HIDDEN_SCHEMA_MIGRATION_COERCION",
                "REJECT",
                76,
                "A schema or semantic-version change cannot be hidden as parser coercion.",
                path,
                _ids(
                    claim_id,
                    claim.get("from_schema_version"),
                    claim.get("to_schema_version"),
                    claim.get("from_semantic_version"),
                    claim.get("to_semantic_version"),
                ),
            ))
        if changed and not claim.get("migration_record_id"):
            diagnostics.append(Diagnostic(
                "SCHEMA_MIGRATION_RECORD_REQUIRED",
                "REJECT",
                75,
                "A visible schema or semantic migration requires an explicit migration record.",
                path,
                _ids(claim_id),
            ))

    elif kind == "backend_statement_mapping":
        canonical = str(claim.get("canonical_statement_hash") or "")
        lean_hash = str(claim.get("lean_statement_hash") or "")
        coq_hash = str(claim.get("coq_statement_hash") or "")
        if (
            len(canonical) != 64
            or canonical != lean_hash
            or canonical != coq_hash
            or not claim.get("lean_symbol")
            or not claim.get("coq_symbol")
        ):
            diagnostics.append(Diagnostic(
                "BACKEND_STATEMENT_HASH_MISMATCH",
                "REJECT",
                77,
                "Mapped Lean and Coq theorem entries must share the canonical statement hash.",
                path,
                _ids(claim_id, claim.get("theorem_id"), canonical, lean_hash, coq_hash),
            ))

    elif kind == "accepted_fragment_soundness_audit":
        if claim.get("checker_status") == "PASS":
            premises = (
                claim.get("rule_lemmas_proved") is True
                and claim.get("implementation_invariants_hold") is True
            )
            if not premises:
                diagnostics.append(Diagnostic(
                    "CHECKER_SOUNDNESS_PREMISES_UNPROVED",
                    "DEFERRED",
                    76,
                    "Checker soundness remains conditional until rule lemmas and implementation invariants are proved.",
                    path,
                    _ids(claim_id, claim.get("accepted_fragment_id")),
                ))
            elif claim.get("semantic_obligations_hold") is not True:
                diagnostics.append(Diagnostic(
                    "CHECKER_PASS_VIOLATES_ACCEPTED_FRAGMENT_SOUNDNESS",
                    "REJECT",
                    78,
                    "Under proved premises, checker PASS must imply the accepted FC-1 semantic obligations.",
                    path,
                    _ids(claim_id, claim.get("accepted_fragment_id")),
                ))

    return diagnostics
