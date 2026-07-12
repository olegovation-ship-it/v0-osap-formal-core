# V0 OSAP v1.3.0 Phase 5 Build Specification and Implementation Patch v0.1

**Artifact ID:** `V0_OSAP_v1_3_0_PHASE5_T145_T150`
**Date:** 2026-07-12
**Target branch:** `v1.3.0-development`
**Baseline:** Phase 4 accepted, CI-closed, merged, and historically preserved
**Baseline merge commit:** `2a769d7723470cce59df81262b586abf19b9c750`
**Implementation state:** `BUILD_READY / CI_PENDING`
**Immutable release baseline:** tag `v1.2.0`, DOI `10.5281/zenodo.21306969`
**Checker development version:** `0.6.0.dev1`
**Author:** Dmytro Panasenko, Independent Researcher

## 1. Decision summary

Phase 5 completes the reserved v1.1 theorem-target interval T121-T150 by implementing the deterministic interchange, replay, migration, backend-correspondence, and conditional accepted-fragment soundness cluster T145-T150. It does not release v1.3.0 and does not enlarge or rewrite the archived v1.2.0 claim.

| ID | Canonical theorem target | Executable obligation |
|---|---|---|
| T145 | Canonical serialization determinism | A well-formed JSON-compatible FC-1 object has one `V0-OSAP-CJ-1` byte representation and SHA-256 envelope. |
| T146 | Round-trip identity | Canonical serialize/parse returns the original well-formed object. |
| T147 | Replay determinism | Pinned proof, registry, and ruleset hashes produce one canonical replay result. |
| T148 | Schema migration visibility | A schema or semantic-version change is explicit and cannot be hidden as parser coercion. |
| T149 | Backend statement correspondence | Lean and Coq entries for a mapped theorem share its canonical statement hash. |
| T150 | Accepted-fragment checker soundness | Conditional on proved rule lemmas and implementation invariants, checker PASS entails the implemented FC-1 obligations. |

## 2. Normative source discipline

The theorem names and target statements are inherited from V0 OSAP v1.1. Canonical JSON uses UTF-8 without BOM, lexicographically sorted object keys, no insignificant whitespace, LF termination, and SHA-256 under `V0-OSAP-CJ-1`. Migrations are explicit transformations rather than silent parser coercions. Replay is deterministic only under pinned inputs and no hidden state.

## 3. Machine-readable extension

New claim kinds:

- `canonical_serialization_audit`
- `round_trip_audit`
- `replay_determinism_audit`
- `schema_migration_audit`
- `backend_statement_mapping`
- `accepted_fragment_soundness_audit`

The canonical utility layer adds strict canonical parsing, round-trip replay, and typed hash envelopes.

## 4. Diagnostics

- `CANONICALIZATION_PROFILE_MISMATCH`
- `CANONICAL_SERIALIZATION_HASH_MISMATCH`
- `ROUND_TRIP_IDENTITY_MISMATCH`
- `REPLAY_INPUTS_NOT_PINNED`
- `REPLAY_NONDETERMINISTIC_RESULT`
- `HIDDEN_SCHEMA_MIGRATION_COERCION`
- `SCHEMA_MIGRATION_RECORD_REQUIRED`
- `BACKEND_STATEMENT_HASH_MISMATCH`
- `CHECKER_SOUNDNESS_PREMISES_UNPROVED`
- `CHECKER_PASS_VIOLATES_ACCEPTED_FRAGMENT_SOUNDNESS`

## 5. Proof-assistant implementation

`V0OSAP.Phase5` and `Phase5.v` provide bounded formal encodings for T145-T150. The T150 result is explicitly conditional: it consumes a soundness implication plus proved premises and a PASS hypothesis. Compilation is evidence for these encoded propositions only. It is not proof-term identity, full checker completeness, or soundness beyond the accepted fragment.

## 6. Fixture and crosswalk contract

Each theorem target has one positive fixture and one decisive countermodel. The Phase 5 crosswalk records canonical statements, assumptions, conclusions, backend symbols, validator rules, diagnostics, fixture IDs, limitations, and SHA-256 statement hashes.

## 7. Acceptance gates

1. Baseline merge commit `2a769d7723470cce59df81262b586abf19b9c750` is an ancestor of the development branch.
2. Editable Python install passes.
3. Full Python regression suite passes with expected total 14 tests.
4. Schema bundle validation passes.
5. Deterministic replay of all fixtures passes.
6. Proof-hole scan passes.
7. Phase 1 preservation passes.
8. Phase 2, Phase 3, and Phase 4 expansion/closure verifiers pass.
9. Phase 5 expansion verifier passes.
10. Lean 4 build passes.
11. Coq build passes.
12. `git diff --check` passes.
13. The complete GitHub Actions matrix passes before acceptance.

## 8. Claim boundary

This patch does not move or retag `v1.2.0`, does not alter DOI `10.5281/zenodo.21306969`, does not create a v1.3.0 release, and does not claim checker completeness, proof-term identity, semantic equivalence of backend implementations, physical validity, or empirical validation. T150 remains conditional on proved rule lemmas and implementation invariants.
