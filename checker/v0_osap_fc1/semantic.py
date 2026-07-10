from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .diagnostics import Diagnostic, aggregate_status, sort_diagnostics


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


def check_registry(registry: dict[str, Any]) -> dict[str, Any]:
    diagnostics: list[Diagnostic] = []
    declarations = registry.get("declarations", [])
    tokens = registry.get("tokens", [])
    families = registry.get("prerequisite_families", [])
    claims = registry.get("claims", [])
    evidence = registry.get("evidence_objects", [])
    contexts = set(registry.get("contexts", []))

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
            satisfied = all(presence) if family.get("mode") == "all_of" else any(presence)
            if not satisfied:
                diagnostics.append(Diagnostic(
                    "MISSING_PREREQUISITE", "REJECT", 90,
                    f"Live target register {target} lacks its enabled {family.get('mode')} support family.",
                    path,
                    tuple(str(x) for x in [family.get("family_id"), carrier, target, context]),
                    tuple(str(x) for x in family.get("evidence_ids", [])),
                ))

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

        elif kind == "absolute_v0":
            source_id = claim.get("source_claim_id")
            source = claims_by_id.get(source_id)
            if source and source.get("kind") in {"relative_v0", "dle", "approximation_v0", "heuristic_v0"}:
                diagnostics.append(Diagnostic(
                    "ABSOLUTE_RELATIVE_FIREWALL", "REJECT", 92,
                    "A relative, DLE, approximation, or heuristic claim cannot directly license absolute V0.",
                    path, tuple(str(x) for x in [claim.get("claim_id"), source_id])
                ))

        elif kind == "observer_terminal_self_certificate":
            external = claim.get("external_evidence_ids", [])
            independence = claim.get("independence_group_ids", [])
            if not external or not independence:
                diagnostics.append(Diagnostic(
                    "OBSERVER_SELF_CERTIFICATION_LIMIT", "REJECT", 87,
                    "A terminal self-certificate requires externally preserved evidence and an independence group.",
                    path, (str(claim.get("claim_id")),), tuple(str(x) for x in external)
                ))

    diagnostics = sort_diagnostics(diagnostics)
    return {
        "registry_state_id": registry.get("registry_state_id"),
        "status": aggregate_status(diagnostics),
        "diagnostics": [d.to_dict() for d in diagnostics],
        "implementation_version": "v0-osap-fc1/0.1.0",
    }
