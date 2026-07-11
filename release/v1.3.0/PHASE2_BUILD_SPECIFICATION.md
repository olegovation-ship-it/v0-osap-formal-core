# V0 OSAP v1.3.0 Phase 2 Build Specification and Implementation Patch v0.1

**Artifact ID:** `V0_OSAP_v1_3_0_PHASE2_T127_T132`
**Date:** 2026-07-11
**Target branch:** `v1.3.0-development`
**Baseline:** Phase 1 accepted and merged; immutable release `v1.2.0` remains unchanged
**Implementation state:** `ACCEPTED / CI_PASS / MERGED / HISTORICALLY_PRESERVED`
**Closure PR:** `#2`
**Merge commit:** `f494cd9401e2b9ff91d87de77e11f4eb2468726c`
**Author:** Dmytro Panasenko, Independent Researcher

## 1. Decision summary

Phase 2 expands the executable and dual-backend theorem cluster from T121-T126 to T127-T132. It does not create the v1.3.0 release.

| ID | Canonical theorem target | Executable obligation |
|---|---|---|
| T127 | Closure minimality | Declared computed closure equals the least closure generated from the seed and enabled prerequisite families. |
| T128 | Alternative-support transparency | Every accepted `one_of` obligation records a selected member, and that member belongs to the declared family and is live in context. |
| T129 | Compatibility preservation | An accepted activation profile does not jointly activate a declared incompatible register pair. |
| T130 | Dimensional readiness soundness | `READY_VALUE` requires every protocol prerequisite register to be live. |
| T131 | Undefined is not zero | `UNDEFINED_DOMAIN` cannot carry a numeric value, including zero. |
| T132 | DLE history adequacy | Accepted DLE requires prior historical/retired evidence and current absence of a live token. |

## 2. Authority and source discipline

The normative theorem names and target statements are inherited from V0 OSAP v1.1. Phase 2 does not rename theorem IDs, weaken Phase 1 semantics, or reinterpret the archived v1.2.0 proof status.

The implementation distinguishes schema validity, deterministic checker replay, fixture evidence, Lean 4 compilation, Coq compilation, and cross-backend statement mapping. Compilation is not proof-term identity, theorem completeness, empirical confirmation, or physical validation.

## 3. Machine-readable representations

### T127 prerequisite closure claim

A `prerequisite_closure` claim carries `seed_register_ids` and `computed_closure_register_ids`. For `all_of`, all prerequisites are added. For `one_of`, only the explicit T128 selected support is added. Iteration continues to a fixed point.

### T128 one-of support selection

A `one_of_support_selection` claim records `family_id`, `selected_register_id`, `carrier_id`, and `context_id`. The family must be enabled and `one_of`; the selected register must belong to the family and be live.

### T129 compatibility profile

An `activation_profile` exposes `active_register_ids`. Enabled constraints use an explicit incompatible register pair. A profile is rejected when both endpoints are active.

### T130 protocol readiness

A protocol declares `prerequisite_register_ids`. A `protocol_readiness` claim with `READY_VALUE` passes only when every prerequisite has a matching live token.

### T131 dimension result

A `dimension_result` claim uses `READY_VALUE` or `UNDEFINED_DOMAIN`. `UNDEFINED_DOMAIN` and `numeric_value` are mutually exclusive. `READY_VALUE` requires a numeric result.

### T132 DLE claim

The existing `dle` representation is retained. Phase 2 adds exact T132 fixtures and backend theorem wrappers instead of inventing a second DLE syntax.

## 4. Diagnostics

- `PREREQUISITE_CLOSURE_NOT_LEAST`
- `ALTERNATIVE_SUPPORT_SELECTION_REQUIRED`
- `INVALID_ALTERNATIVE_SUPPORT_SELECTION`
- `COMPATIBILITY_CONSTRAINT_VIOLATION`
- `ACTIVE_PROFILE_REGISTER_NOT_LIVE`
- `PROTOCOL_READY_WITHOUT_LIVE_PREREQUISITES`
- `UNDEFINED_DOMAIN_COERCED_TO_NUMERIC`
- `READY_VALUE_MISSING_NUMERIC`
- existing DLE diagnostics `DLE_WITHOUT_HISTORICAL_SOURCE` and `DLE_CONFLICTS_WITH_LIVE_TOKEN`

## 5. Backend implementation contract

A new Lean 4 module `V0OSAP.Expansion` and a matching Coq module `Expansion.v` define T127-T132 using finite lists and explicit hypotheses inside FC-1. Root aggregation imports are updated. The Python checker adds deterministic rules and twelve paired fixtures.

## 6. Crosswalk and parity record

Each theorem record contains stable ID, canonical name, normalized signature, assumptions, conclusion, backend symbols, validator rule, diagnostics, fixtures, source section, limitations, canonical statement hash, and parity state. The implementation-time state was `PATCH_READY_CI_PENDING`; after PR #2 and its all-green matrix, the closure state is `ACCEPTED_CI_PASS`.

## 7. Acceptance gates

1. Full Python test suite passed: 111 tests.
2. Schema bundle and deterministic fixture replay passed.
3. Phase 1 verifier remained green after being scoped to Phase 1 records.
4. Phase 2 crosswalk/hash verifier passed.
5. Proof-hole scan passed.
6. Lean 4 build passed.
7. Coq build passed.
8. Release readiness preserved immutable v1.2.0 manifest and closure verification.
9. `git diff --check` passed.
10. GitHub Actions returned an all-green matrix: 8/8 PR checks.
11. The Phase 2 CI-closure audit removed stale pending metadata and recorded PR #2, head SHA, merge SHA, and historical-preservation evidence.

## 8. Release and claim boundary

This patch does not alter the `v1.2.0` tag or DOI, claim complete T121-T150 mechanization, claim semantic equivalence or proof-term identity between Lean 4 and Coq, claim checker completeness, provide empirical or physical validation, or open a Zenodo release.

## 9. Closure sequence

The implementation patch was uploaded to `v1.3.0-development`, locally validated, committed, pushed, and opened as draft PR #2. After 8/8 checks passed, PR #2 was marked ready, merged by merge commit `f494cd9401e2b9ff91d87de77e11f4eb2468726c`, and the development branch was fast-forward synchronized with `main`. This closure patch records that result and adds a dedicated historical-preservation verifier.
