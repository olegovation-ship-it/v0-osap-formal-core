from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .diagnostics import STATUS_RANK, Diagnostic, aggregate_status, sort_diagnostics
from .phase5 import phase5_diagnostics
from .phase6 import phase6_diagnostics


def _duplicates(values: Iterable[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _token_matches(token: dict[str, Any], carrier: str, register: str, context: str) -> bool:
    return (
        token.get("carrier_id") == carrier
        and token.get("register_id") == register
        and token.get("context_id") == context
    )


def _has_partition(
    tokens: list[dict[str, Any]], carrier: str, register: str, context: str, partitions: set[str]
) -> bool:
    return any(_token_matches(t, carrier, register, context) and t.get("partition") in partitions for t in tokens)


def _live_residual_registers(
    tokens: list[dict[str, Any]], carrier: str, context: str, residual_registers: Iterable[str]
) -> list[str]:
    return sorted({
        str(register)
        for register in residual_registers
        if _has_partition(tokens, carrier, str(register), context, {"live"})
    })


# V0_OSAP_PHASE2_T127_T132
def _enabled_family_map(families: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(family.get("family_id")): family
        for family in families
        if isinstance(family, dict) and family.get("enabled", False) and family.get("family_id")
    }


def _least_prerequisite_closure(
    seed_register_ids: Iterable[str],
    families: list[dict[str, Any]],
    selected_by_family: dict[str, str],
) -> list[str]:
    closure = {str(register) for register in seed_register_ids}
    changed = True
    while changed:
        changed = False
        for family in families:
            if not isinstance(family, dict) or not family.get("enabled", False):
                continue
            target = str(family.get("target_register_id"))
            if target not in closure:
                continue
            if family.get("mode") == "all_of":
                additions = [str(item) for item in family.get("prerequisite_register_ids", [])]
            elif family.get("mode") == "one_of":
                selected = selected_by_family.get(str(family.get("family_id")))
                additions = [selected] if selected else []
            else:
                additions = []
            before = len(closure)
            closure.update(item for item in additions if item)
            changed = changed or len(closure) != before
    return sorted(closure)


def _matching_live_token(
    tokens: list[dict[str, Any]], carrier: str, register: str, context: str
) -> bool:
    return _has_partition(tokens, carrier, register, context, {"live"})


def check_registry(registry: dict[str, Any]) -> dict[str, Any]:
    diagnostics: list[Diagnostic] = []
    declarations = registry.get("declarations", [])
    tokens = registry.get("tokens", [])
    families = registry.get("prerequisite_families", [])
    claims = registry.get("claims", [])
    evidence = registry.get("evidence_objects", [])
    contexts = set(registry.get("contexts", []))
    compatibility_constraints = registry.get("compatibility_constraints", [])
    protocols = registry.get("protocols", [])

    declaration_ids = {d.get("id") for d in declarations if isinstance(d, dict)}
    evidence_ids = {e.get("evidence_id") for e in evidence if isinstance(e, dict)}
    declaration_sorts = {d.get("id"): d.get("sort") for d in declarations if isinstance(d, dict)}

    for duplicate in _duplicates([str(d.get("id")) for d in declarations if isinstance(d, dict)]):
        diagnostics.append(Diagnostic(
            "DUPLICATE_DECLARATION_ID", "REJECT", 100,
            f"Declaration ID is repeated: {duplicate}", "/declarations", (duplicate,)
        ))
    for duplicate in _duplicates([str(t.get("token_id")) for t in tokens if isinstance(t, dict)]):
        diagnostics.append(Diagnostic(
            "DUPLICATE_TOKEN_ID", "REJECT", 100,
            f"Token ID is repeated: {duplicate}", "/tokens", (duplicate,)
        ))
    for duplicate in _duplicates([str(f.get("family_id")) for f in families if isinstance(f, dict)]):
        diagnostics.append(Diagnostic(
            "DUPLICATE_FAMILY_ID", "REJECT", 100,
            f"Prerequisite family ID is repeated: {duplicate}", "/prerequisite_families", (duplicate,)
        ))
    claim_ids = [str(c.get("claim_id")) for c in claims if isinstance(c, dict) and c.get("claim_id")]
    for duplicate in _duplicates(claim_ids):
        diagnostics.append(Diagnostic(
            "DUPLICATE_CLAIM_ID", "REJECT", 100,
            f"Claim ID is repeated: {duplicate}", "/claims", (duplicate,)
        ))

    for i, token in enumerate(tokens):
        if not isinstance(token, dict):
            continue
        path = f"/tokens/{i}"
        for field, expected_sort in (
            ("carrier_id", {"Sector", "Observer", "Branch", "NullMark"}),
            ("register_id", {"Register"}),
        ):
            identifier = token.get(field)
            if identifier not in declaration_ids:
                diagnostics.append(Diagnostic(
                    "UNRESOLVED_TOKEN_REFERENCE", "REJECT", 95,
                    f"{field} does not resolve: {identifier}", path, (str(identifier),)
                ))
            elif declaration_sorts.get(identifier) not in expected_sort:
                diagnostics.append(Diagnostic(
                    "TOKEN_REFERENCE_SORT_MISMATCH", "REJECT", 94,
                    f"{field} has incompatible sort: {identifier}", path, (str(identifier),)
                ))
        context = token.get("context_id")
        if context not in contexts:
            diagnostics.append(Diagnostic(
                "UNRESOLVED_CONTEXT_REFERENCE", "REJECT", 95,
                f"Token context does not resolve: {context}", path, (str(context),)
            ))
        source = token.get("source_evidence_id")
        if source not in evidence_ids:
            diagnostics.append(Diagnostic(
                "UNRESOLVED_EVIDENCE_REFERENCE", "REJECT", 95,
                f"Token source evidence does not resolve: {source}", path, (str(source),)
            ))

    for i, family in enumerate(families):
        if not isinstance(family, dict) or not family.get("enabled", False):
            continue
        path = f"/prerequisite_families/{i}"
        target = family.get("target_register_id")
        prerequisites = family.get("prerequisite_register_ids", [])
        for register in [target, *prerequisites]:
            if register not in declaration_ids or declaration_sorts.get(register) != "Register":
                diagnostics.append(Diagnostic(
                    "UNRESOLVED_PREREQUISITE_REGISTER", "REJECT", 93,
                    f"Prerequisite register does not resolve as Register: {register}", path, (str(register),)
                ))
        for evid in family.get("evidence_ids", []):
            if evid not in evidence_ids:
                diagnostics.append(Diagnostic(
                    "UNRESOLVED_EVIDENCE_REFERENCE", "REJECT", 93,
                    f"Prerequisite evidence does not resolve: {evid}", path, (str(evid),)
                ))

        target_tokens = [t for t in tokens if t.get("partition") == "live" and t.get("register_id") == target]
        for target_token in target_tokens:
            carrier = target_token.get("carrier_id")
            context = target_token.get("context_id")
            presence = [
                _has_partition(tokens, carrier, prereq, context, {"live"})
                for prereq in prerequisites
            ]
            # T122 is represented exactly: an empty all_of family is vacuously satisfied.
            if family.get("mode") == "all_of":
                satisfied = all(presence)
            else:
                satisfied = any(presence)
            if not satisfied:
                diagnostics.append(Diagnostic(
                    "MISSING_PREREQUISITE", "REJECT", 90,
                    f"Live target register {target} lacks its enabled {family.get('mode')} support family.",
                    path,
                    tuple(str(x) for x in [family.get("family_id"), carrier, target, context]),
                    tuple(str(x) for x in family.get("evidence_ids", [])),
                ))


    # Phase 2: T127-T132 theorem expansion.
    family_map = _enabled_family_map(families)
    protocol_map = {
        str(protocol.get("protocol_id")): protocol
        for protocol in protocols
        if isinstance(protocol, dict) and protocol.get("enabled", False) and protocol.get("protocol_id")
    }

    selection_claims = [
        claim for claim in claims
        if isinstance(claim, dict) and claim.get("kind") == "one_of_support_selection"
    ]
    selected_by_family: dict[str, str] = {}
    selection_keys: set[tuple[str, str, str]] = set()
    for claim in selection_claims:
        family_id = str(claim.get("family_id"))
        selected = str(claim.get("selected_register_id"))
        carrier = str(claim.get("carrier_id"))
        context = str(claim.get("context_id"))
        family = family_map.get(family_id)
        valid = (
            family is not None
            and family.get("mode") == "one_of"
            and selected in [str(item) for item in family.get("prerequisite_register_ids", [])]
            and _matching_live_token(tokens, carrier, selected, context)
        )
        if not valid:
            diagnostics.append(Diagnostic(
                "INVALID_ALTERNATIVE_SUPPORT_SELECTION", "REJECT", 90,
                "A one_of selection must name a live member of an enabled one_of family.",
                "/claims", tuple(str(x) for x in [claim.get("claim_id"), family_id, selected, carrier, context]),
            ))
        else:
            selected_by_family[family_id] = selected
            selection_keys.add((family_id, carrier, context))

    for family in family_map.values():
        if family.get("mode") != "one_of":
            continue
        family_id = str(family.get("family_id"))
        target = str(family.get("target_register_id"))
        for token in tokens:
            if not isinstance(token, dict) or token.get("partition") != "live":
                continue
            if str(token.get("register_id")) != target:
                continue
            carrier = str(token.get("carrier_id"))
            context = str(token.get("context_id"))
            if (family_id, carrier, context) not in selection_keys:
                diagnostics.append(Diagnostic(
                    "ALTERNATIVE_SUPPORT_SELECTION_REQUIRED", "REJECT", 89,
                    "A live enabled one_of obligation requires an explicit selected support member.",
                    "/prerequisite_families", (family_id, carrier, target, context),
                ))

    for claim in claims:
        if not isinstance(claim, dict):
            continue
        kind = claim.get("kind")
        path = "/claims"
        if kind == "prerequisite_closure":
            expected = _least_prerequisite_closure(claim.get("seed_register_ids", []), families, selected_by_family)
            declared = sorted({str(item) for item in claim.get("computed_closure_register_ids", [])})
            if declared != expected:
                diagnostics.append(Diagnostic(
                    "PREREQUISITE_CLOSURE_NOT_LEAST", "REJECT", 90,
                    "The declared prerequisite closure differs from the least generated closure.",
                    path, tuple(str(x) for x in [claim.get("claim_id"), *declared, *expected]),
                ))
        elif kind == "activation_profile":
            carrier = str(claim.get("carrier_id"))
            context = str(claim.get("context_id"))
            active = {str(item) for item in claim.get("active_register_ids", [])}
            for register in sorted(active):
                if not _matching_live_token(tokens, carrier, register, context):
                    diagnostics.append(Diagnostic(
                        "ACTIVE_PROFILE_REGISTER_NOT_LIVE", "REJECT", 84,
                        "Every register declared active must have a matching live token.",
                        path, (str(claim.get("claim_id")), carrier, register, context),
                    ))
            for constraint in compatibility_constraints:
                if not isinstance(constraint, dict) or not constraint.get("enabled", False):
                    continue
                if constraint.get("relation") != "incompatible":
                    continue
                left = str(constraint.get("left_register_id"))
                right = str(constraint.get("right_register_id"))
                if left in active and right in active:
                    diagnostics.append(Diagnostic(
                        "COMPATIBILITY_CONSTRAINT_VIOLATION", "REJECT", 90,
                        "An activation profile jointly activates an incompatible register pair.",
                        path, tuple(str(x) for x in [claim.get("claim_id"), constraint.get("constraint_id"), left, right]),
                    ))
        elif kind == "protocol_readiness" and claim.get("readiness_status") == "READY_VALUE":
            protocol_id = str(claim.get("protocol_id"))
            protocol = protocol_map.get(protocol_id)
            carrier = str(claim.get("carrier_id"))
            context = str(claim.get("context_id"))
            missing = [protocol_id] if protocol is None else [
                str(register) for register in protocol.get("prerequisite_register_ids", [])
                if not _matching_live_token(tokens, carrier, str(register), context)
            ]
            if missing:
                diagnostics.append(Diagnostic(
                    "PROTOCOL_READY_WITHOUT_LIVE_PREREQUISITES", "REJECT", 90,
                    "READY_VALUE requires every protocol prerequisite to be live.",
                    path, tuple(str(x) for x in [claim.get("claim_id"), protocol_id, *missing]),
                ))
        elif kind == "dimension_result":
            status = claim.get("dimension_status")
            has_numeric = "numeric_value" in claim
            if status == "UNDEFINED_DOMAIN" and has_numeric:
                diagnostics.append(Diagnostic(
                    "UNDEFINED_DOMAIN_COERCED_TO_NUMERIC", "REJECT", 90,
                    "UNDEFINED_DOMAIN cannot carry a numeric value, including zero.",
                    path, (str(claim.get("claim_id")), str(claim.get("protocol_id"))),
                ))
            elif status == "READY_VALUE" and not has_numeric:
                diagnostics.append(Diagnostic(
                    "READY_VALUE_MISSING_NUMERIC", "REJECT", 85,
                    "READY_VALUE requires an explicit numeric result.",
                    path, (str(claim.get("claim_id")), str(claim.get("protocol_id"))),
                ))

    # Phase 3: T133-T138 reactivation, residual, promotion, identity, and self-certification firewall.
    tokens_by_id = {
        str(token.get("token_id")): token
        for token in tokens
        if isinstance(token, dict) and token.get("token_id")
    }
    phase3_claims_by_id = {
        str(claim.get("claim_id")): claim
        for claim in claims
        if isinstance(claim, dict) and claim.get("claim_id")
    }
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        kind = claim.get("kind")
        path = "/claims"
        if kind == "reactivation":
            prior_id = str(claim.get("prior_token_id"))
            reactivated_id = str(claim.get("reactivated_token_id"))
            if prior_id == reactivated_id:
                diagnostics.append(Diagnostic(
                    "REACTIVATION_TOKEN_ID_REUSED", "REJECT", 94,
                    "Reactivation must allocate a token identifier distinct from the historical or retired token.",
                    path, (str(claim.get("claim_id")), prior_id),
                ))
                continue
            prior = tokens_by_id.get(prior_id)
            reactivated = tokens_by_id.get(reactivated_id)
            if prior is None or prior.get("partition") not in {"historical", "retired"}:
                diagnostics.append(Diagnostic(
                    "REACTIVATION_PRIOR_TOKEN_INVALID", "REJECT", 92,
                    "The prior reactivation token must resolve and be historical or retired.",
                    path, (str(claim.get("claim_id")), prior_id),
                ))
            if reactivated is None or reactivated.get("partition") != "live":
                diagnostics.append(Diagnostic(
                    "REACTIVATION_TARGET_NOT_LIVE", "REJECT", 92,
                    "The reactivated token must resolve as live.",
                    path, (str(claim.get("claim_id")), reactivated_id),
                ))
            if prior is not None and reactivated is not None:
                coordinates = ("carrier_id", "register_id", "context_id")
                if any(prior.get(field) != reactivated.get(field) for field in coordinates):
                    diagnostics.append(Diagnostic(
                        "REACTIVATION_COORDINATES_MISMATCH", "REJECT", 90,
                        "Reactivation must preserve carrier, register, and context coordinates.",
                        path, (str(claim.get("claim_id")), prior_id, reactivated_id),
                    ))
        elif kind == "raw_relative_v0":
            carrier = str(claim.get("carrier_id"))
            context = str(claim.get("context_id"))
            offenders = _live_residual_registers(
                tokens, carrier, context, claim.get("residual_register_ids", [])
            )
            if offenders:
                diagnostics.append(Diagnostic(
                    "LIVE_RESIDUAL_OBSTRUCTS_RAW_RELATIVE_V0", "REJECT", 92,
                    "Any live residual blocks raw relative nullity.",
                    path, tuple(str(x) for x in [claim.get("claim_id"), *offenders]),
                ))
        elif kind == "robust_relative_v0_noneliminable":
            carrier = str(claim.get("carrier_id"))
            context = str(claim.get("context_id"))
            offenders = _live_residual_registers(
                tokens, carrier, context, claim.get("non_eliminable_residual_register_ids", [])
            )
            if offenders:
                diagnostics.append(Diagnostic(
                    "LIVE_NONELIMINABLE_RESIDUAL_OBSTRUCTS_ROBUST_RELATIVE_V0", "REJECT", 93,
                    "A live non-eliminable residual blocks robust relative nullity.",
                    path, tuple(str(x) for x in [claim.get("claim_id"), *offenders]),
                ))
        elif kind == "v0_identity":
            source_id = str(claim.get("source_claim_id"))
            source = phase3_claims_by_id.get(source_id)
            if source is not None and source.get("kind") == "approximation_v0":
                diagnostics.append(Diagnostic(
                    "APPROXIMATION_DOES_NOT_ENTAIL_V0_IDENTITY", "REJECT", 94,
                    "An approximation certificate does not entail V0 identity.",
                    path, (str(claim.get("claim_id")), source_id),
                ))
        elif kind == "terminal_exhaustion_certificate":
            support_state = str(claim.get("support_state_id"))
            certification_state = str(claim.get("certification_state_id"))
            if support_state == certification_state:
                diagnostics.append(Diagnostic(
                    "SAME_STATE_SELF_CERTIFICATION_FORBIDDEN", "REJECT", 94,
                    "Same-state exhausted support cannot certify its own total exhaustion.",
                    path, (str(claim.get("claim_id")), support_state),
                ))


    # Phase 4: T139-T144 archive, witness, branch, cardinality, and diagnostic precedence.
    evidence_by_id = {
        str(item.get("evidence_id")): item
        for item in evidence
        if isinstance(item, dict) and item.get("evidence_id")
    }
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        kind = claim.get("kind")
        path = "/claims"

        if kind == "archive_guard_export":
            if claim.get("exports_current_guard") is True:
                diagnostics.append(Diagnostic(
                    "ARCHIVE_CANNOT_EXPORT_CURRENT_GUARD", "REJECT", 86,
                    "An archive preserves evidence but cannot export a current observer guard.",
                    path, tuple(str(x) for x in [
                        claim.get("claim_id"), claim.get("archive_id"), claim.get("observer_id")
                    ]),
                ))

        elif kind == "external_witness_certificate":
            external = [str(item) for item in claim.get("external_evidence_ids", [])]
            independence = [str(item) for item in claim.get("independence_group_ids", [])]
            admissible = (
                claim.get("policy_compliant") is True
                and claim.get("non_circular") is True
                and claim.get("identity_verified") is True
                and claim.get("evidence_verified") is True
                and bool(external)
                and bool(independence)
                and all(item in evidence_ids for item in external)
            )
            if not admissible:
                diagnostics.append(Diagnostic(
                    "INDEPENDENT_WITNESS_CERTIFICATE_UNSUPPORTED", "REJECT", 85,
                    "An external witness certificate requires policy compliance, non-circularity, verified identity/evidence, external evidence, and an independence group.",
                    path, tuple(str(x) for x in [
                        claim.get("claim_id"), claim.get("observer_id"), claim.get("witness_id")
                    ]), tuple(external),
                ))

        elif kind == "v0_branch_containment":
            container = str(claim.get("container_id"))
            branch = str(claim.get("contained_branch_id"))
            if declaration_sorts.get(container) != "NullMark" or declaration_sorts.get(branch) != "Branch":
                diagnostics.append(Diagnostic(
                    "CONTAINMENT_REFERENCE_SORT_MISMATCH", "REJECT", 82,
                    "V0 containment audit requires a NullMark container reference and a Branch target reference.",
                    path, (str(claim.get("claim_id")), container, branch),
                ))
            elif claim.get("containment_mode") == "ordinary":
                diagnostics.append(Diagnostic(
                    "V0_ORDINARY_CONTAINS_FORBIDDEN", "REJECT", 81,
                    "V0 has no ordinary Contains relation to a branch in FC-1.",
                    path, (str(claim.get("claim_id")), container, branch),
                ))

        elif kind == "branch_distinctness":
            basis = claim.get("distinctness_basis")
            proof_evidence = [str(item) for item in claim.get("evidence_ids", [])]
            if basis == "label_only":
                diagnostics.append(Diagnostic(
                    "BRANCH_LABELS_DO_NOT_PROVE_DISTINCTNESS", "REJECT", 80,
                    "Different branch labels do not prove branch distinctness.",
                    path, tuple(str(x) for x in [
                        claim.get("claim_id"), claim.get("left_branch_id"),
                        claim.get("right_branch_id"), claim.get("left_label"), claim.get("right_label")
                    ]),
                ))
            elif not proof_evidence or not all(item in evidence_ids for item in proof_evidence):
                diagnostics.append(Diagnostic(
                    "BRANCH_DISTINCTNESS_EVIDENCE_REQUIRED", "DEFERRED", 79,
                    "A non-label branch-distinctness basis requires resolved evidence.",
                    path, tuple(str(x) for x in [
                        claim.get("claim_id"), claim.get("left_branch_id"), claim.get("right_branch_id")
                    ]), tuple(proof_evidence),
                ))

        elif kind == "branch_cardinality":
            cardinality_kind = claim.get("cardinality_kind")
            if cardinality_kind != "finite_enumerated":
                meta_index_id = str(claim.get("meta_index_id") or "")
                meta_index = evidence_by_id.get(meta_index_id)
                proof_evidence = [str(item) for item in claim.get("evidence_ids", [])]
                licensed = (
                    meta_index is not None
                    and meta_index.get("evidence_type") == "meta_index_certificate"
                    and bool(proof_evidence)
                    and all(item in evidence_ids for item in proof_evidence)
                )
                if not licensed:
                    diagnostics.append(Diagnostic(
                        "DEFERRED_CARDINALITY_CERT", "DEFERRED", 78,
                        "A non-finite cardinality claim requires a typed meta-index and proof evidence.",
                        path, tuple(str(x) for x in [
                            claim.get("claim_id"), cardinality_kind, meta_index_id
                        ]), tuple(proof_evidence),
                    ))

        elif kind == "diagnostic_precedence_audit":
            statuses = [str(item) for item in claim.get("diagnostic_statuses", [])]
            primary = max(statuses, key=lambda item: STATUS_RANK[item]) if statuses else "PASS"
            if str(claim.get("expected_primary_status")) != primary:
                diagnostics.append(Diagnostic(
                    "DIAGNOSTIC_PRIMARY_STATUS_MISMATCH", "REJECT", 77,
                    "The declared primary status disagrees with the fixed diagnostic precedence.",
                    path, tuple(str(x) for x in [
                        claim.get("claim_id"), claim.get("expected_primary_status"), primary
                    ]),
                ))

    # Phase 5: T145-T150 canonicalization, replay, migration, correspondence, and soundness audits.
    for claim in claims:
        if isinstance(claim, dict):
            diagnostics.extend(phase5_diagnostics(claim))

    # Phase 6: T151-T156 explicit extension-governance audits.
    for claim in claims:
        if isinstance(claim, dict):
            diagnostics.extend(phase6_diagnostics(claim))

    claims_by_id = {c.get("claim_id"): c for c in claims if isinstance(c, dict) and c.get("claim_id")}
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        path = f"/claims/{i}"
        kind = claim.get("kind")
        carrier = claim.get("carrier_id")
        register = claim.get("register_id")
        context = claim.get("context_id")

        if kind == "has_value":
            if not _has_partition(tokens, carrier, register, context, {"live"}):
                diagnostics.append(Diagnostic(
                    "UNGUARDED_VALUE_CLAIM", "REJECT", 88,
                    "A value claim requires a matching live guard token.",
                    path,
                    tuple(str(x) for x in [claim.get("claim_id"), carrier, register, context]),
                ))

        elif kind == "dle":
            was_live = _has_partition(tokens, carrier, register, context, {"historical", "retired"})
            currently_live = _has_partition(tokens, carrier, register, context, {"live"})
            if not was_live:
                diagnostics.append(Diagnostic(
                    "DLE_WITHOUT_HISTORICAL_SOURCE", "REJECT", 88,
                    "DLE requires a historical or retired source token.", path,
                    tuple(str(x) for x in [claim.get("claim_id"), carrier, register, context]),
                ))
            if currently_live:
                diagnostics.append(Diagnostic(
                    "DLE_CONFLICTS_WITH_LIVE_TOKEN", "REJECT", 89,
                    "DLE cannot be certified while a matching token remains live.", path,
                    tuple(str(x) for x in [claim.get("claim_id"), carrier, register, context]),
                ))

        elif kind == "robust_relative_v0":
            residual_registers = claim.get("residual_register_ids", [])
            offenders = _live_residual_registers(tokens, carrier, context, residual_registers)
            if offenders:
                evidence_for_offenders = sorted({
                    str(token.get("source_evidence_id"))
                    for token in tokens
                    if token.get("partition") == "live"
                    and token.get("carrier_id") == carrier
                    and token.get("context_id") == context
                    and str(token.get("register_id")) in offenders
                    and token.get("source_evidence_id")
                })
                diagnostics.append(Diagnostic(
                    "LIVE_RESIDUAL_OBSTRUCTS_ROBUST_RELATIVE_V0", "REJECT", 91,
                    "A robust relative-V0 claim is obstructed by a live token in its declared residual family.",
                    path,
                    tuple(str(x) for x in [claim.get("claim_id"), carrier, register, context, *offenders]),
                    tuple(evidence_for_offenders),
                ))

        elif kind == "absolute_v0":
            source_id = claim.get("source_claim_id")
            source = claims_by_id.get(source_id)
            if source and source.get("kind") in {
                "relative_v0", "raw_relative_v0", "robust_relative_v0",
                "robust_relative_v0_noneliminable", "dle", "approximation_v0", "heuristic_v0"
            }:
                diagnostics.append(Diagnostic(
                    "ABSOLUTE_RELATIVE_FIREWALL", "REJECT", 92,
                    "A relative, DLE, approximation, or heuristic claim cannot directly license absolute V0.",
                    path, tuple(str(x) for x in [claim.get("claim_id"), source_id])
                ))

        elif kind == "observer_terminal_self_certificate":
            internal = claim.get("internal_support_ids", [])
            external = claim.get("external_evidence_ids", [])
            if internal or external:
                diagnostics.append(Diagnostic(
                    "TERMINAL_SELF_CERTIFICATE_NOT_EXHAUSTED", "REJECT", 87,
                    "T125 terminal self-certification requires both internal support and external evidence to be exhausted.",
                    path,
                    tuple(str(x) for x in [claim.get("claim_id"), *internal, *external]),
                    tuple(str(x) for x in external),
                ))

        elif kind == "observer_admissible_certificate":
            external = claim.get("external_evidence_ids", [])
            independence = claim.get("independence_group_ids", [])
            if not external or not independence:
                diagnostics.append(Diagnostic(
                    "OBSERVER_CERTIFICATION_SUPPORT_REQUIRED", "REJECT", 86,
                    "An admissible observer certificate requires externally preserved evidence and an independence group.",
                    path, (str(claim.get("claim_id")),), tuple(str(x) for x in external)
                ))

    diagnostics = sort_diagnostics(diagnostics)
    return {
        "registry_state_id": registry.get("registry_state_id"),
        "status": aggregate_status(diagnostics),
        "diagnostics": [d.to_dict() for d in diagnostics],
        "implementation_version": "v0-osap-fc1/0.7.0.dev1",
    }
