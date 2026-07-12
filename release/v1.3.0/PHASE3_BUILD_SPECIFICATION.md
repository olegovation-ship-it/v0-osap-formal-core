# V0 OSAP v1.3.0 Phase 3 Build Specification and Implementation Patch v0.1

**Artifact ID:** `V0_OSAP_v1_3_0_PHASE3_T133_T138`
**Date:** 2026-07-11
**Target branch:** `v1.3.0-development`
**Baseline:** Phase 2 accepted, CI-closed, merged, and historically preserved; immutable `v1.2.0` remains unchanged
**Implementation state:** `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`
**Phase 2 closure integration:** PR `#3`, merge commit `6f279860121c92e322e55271092f7ba05f483366`
**Phase 3 implementation integration:** PR `#4`, head commit `2172591ed8a5ab3c1fa31f2a3a6575536f161fe4`, merge commit `c02b05f667b82aa31ac8865c31219b94b1fc74d2`
**Author:** Dmytro Panasenko, Independent Researcher

## 1. Decision summary

Phase 3 expands the executable and dual-backend development cluster from T121-T132 to T133-T138. It creates no v1.3.0 release and does not enlarge the archived v1.2.0 claim.

| ID | Canonical theorem target | Executable obligation |
|---|---|---|
| T133 | Fresh-token reactivation | Reactivation references a historical/retired token and a distinct live token with matching carrier/register/context coordinates. |
| T134 | Raw residual obstruction | Every declared residual register must be non-live for raw relative nullity. |
| T135 | Robust residual obstruction | Every declared non-eliminable residual register must be non-live for robust relative nullity. |
| T136 | Relative-to-absolute non-promotion | Absolute V0 cannot cite a relative, DLE, approximation, or heuristic source claim. |
| T137 | Approximation non-identity | V0 identity cannot cite an approximation certificate as its source. |
| T138 | Terminal self-certification limit | Terminal exhaustion requires distinct support and certification state identifiers. |

## 2. Authority and source discipline

The theorem IDs, canonical names, and natural statements are inherited from V0 OSAP v1.1. Phase 3 does not rename prior targets, weaken Phase 1 or Phase 2 semantics, or reinterpret the archived v1.2.0 proof status.

## 3. Machine-readable records

Phase 3 adds claim fields `prior_token_id`, `reactivated_token_id`, `non_eliminable_residual_register_ids`, `support_state_id`, and `certification_state_id`. New claim kinds are `reactivation`, `raw_relative_v0`, `robust_relative_v0_noneliminable`, `v0_identity`, and `terminal_exhaustion_certificate`.

## 4. Diagnostics

- `REACTIVATION_TOKEN_ID_REUSED`
- `REACTIVATION_PRIOR_TOKEN_INVALID`
- `REACTIVATION_TARGET_NOT_LIVE`
- `REACTIVATION_COORDINATES_MISMATCH`
- `LIVE_RESIDUAL_OBSTRUCTS_RAW_RELATIVE_V0`
- `LIVE_NONELIMINABLE_RESIDUAL_OBSTRUCTS_ROBUST_RELATIVE_V0`
- existing `ABSOLUTE_RELATIVE_FIREWALL`, extended to Phase 3 relative claim kinds
- `APPROXIMATION_DOES_NOT_ENTAIL_V0_IDENTITY`
- `SAME_STATE_SELF_CERTIFICATION_FORBIDDEN`

## 5. Backend implementation contract

A new Lean 4 module `V0OSAP.Phase3` and matching Coq module `Phase3.v` formalize T133-T138 with finite records and explicit hypotheses. Root imports and aggregation modules include the Phase 3 cluster. Compilation remains bounded evidence, not proof-term identity or semantic equivalence.

## 6. Fixture and crosswalk contract

Each target has one positive fixture and one decisive countermodel. The statement-hash crosswalk records theorem ID, canonical name, formal signature, assumptions, conclusion, backend symbols, validator rule, diagnostic, fixtures, limitations, and SHA-256 statement hash.

## 7. Acceptance gates

1. Full Python test suite passes.
2. Schema bundle validation passes.
3. Deterministic replay of all fixtures passes.
4. Proof-hole scan passes.
5. Phase 1 preservation verifier passes.
6. Phase 2 expansion verifier passes.
7. Phase 2 CI-closure verifier passes.
8. Phase 3 expansion verifier passes.
9. Lean 4 build passes.
10. Coq build passes.
11. `git diff --check` passes.
12. GitHub Actions returns an all-green matrix before acceptance or merge.

All gates passed for PR #4. The implementation is accepted, merged, and historically preserved. The machine-readable record is `PHASE3_CI_CLOSURE_EVIDENCE.json`; the narrative record is `PHASE3_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md`.

## 8. Release and claim boundary

This patch does not alter tag `v1.2.0`, DOI `10.5281/zenodo.21306969`, or archived release evidence. It does not claim a v1.3.0 release, complete T121-T150 mechanization, backend proof identity, checker completeness, or empirical/physical validation.
