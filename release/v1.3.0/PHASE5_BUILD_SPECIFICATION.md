# V0 OSAP v1.3.0 Phase 5 Build Specification and Implementation Patch v0.1

**Artifact ID:** `V0_OSAP_v1_3_0_PHASE5_T145_T150`
**Date:** 2026-07-12
**Target branch:** `v1.3.0-development`
**Baseline:** Phase 4 accepted, CI-closed, merged, and historically preserved
**Implementation baseline merge commit:** `2a769d7723470cce59df81262b586abf19b9c750`
**Implementation head commit:** `977c5404ebc5cdef9495edd1c46b08d3b0452acb`
**Implementation merge commit:** `5c689de1a30104aa6c4e3860d5e7c26746e2d797`
**Merged at:** `2026-07-12T19:11:41Z`
**Implementation state:** `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`
**Immutable release baseline:** tag `v1.2.0`, DOI `10.5281/zenodo.21306969`
**Checker development version:** `0.6.0.dev1`
**Author:** Dmytro Panasenko, Independent Researcher

## 1. Decision summary

Phase 5 completes the reserved v1.1 theorem-target interval T121-T150 by implementing the deterministic interchange, replay, migration, backend-correspondence, and conditional accepted-fragment soundness cluster T145-T150. PR #8 passed 8/8 checks and merged the implementation head `977c5404ebc5cdef9495edd1c46b08d3b0452acb` into `main` as `5c689de1a30104aa6c4e3860d5e7c26746e2d797`. This closes the Phase 5 development state; it does not release v1.3.0 and does not enlarge or rewrite the archived v1.2.0 claim.

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

Each theorem target has one positive fixture and one decisive countermodel. The Phase 5 crosswalk records canonical statements, assumptions, conclusions, backend symbols, validator rules, diagnostics, fixture IDs, limitations, and SHA-256 statement hashes. After CI closure every Phase 5 record has parity status `ACCEPTED_CI_PASS`.

## 7. Acceptance evidence

1. Implementation baseline merge commit `2a769d7723470cce59df81262b586abf19b9c750` is preserved.
2. Python regression suite passed with 14 tests.
3. Schema bundle validation passed.
4. Deterministic replay of all fixtures passed.
5. Proof-hole scan passed.
6. Phase 1 preservation and Phase 2-4 expansion/closure verifiers passed.
7. Phase 5 expansion verifier passed.
8. Lean 4 build passed.
9. Coq build passed.
10. `git diff --check` passed.
11. PR #8 passed 8/8 GitHub Actions checks.
12. Implementation head `977c5404ebc5cdef9495edd1c46b08d3b0452acb` merged into `main` as `5c689de1a30104aa6c4e3860d5e7c26746e2d797`.
13. Historical-preservation audit passed.

See `release/v1.3.0/PHASE5_CI_CLOSURE_EVIDENCE.json` and `release/v1.3.0/PHASE5_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md`.

## 8. Claim boundary

This closure does not move or retag `v1.2.0`, does not alter DOI `10.5281/zenodo.21306969`, does not create a v1.3.0 release, and does not claim checker completeness, proof-term identity, semantic equivalence of backend implementations, physical validity, or empirical validation. T150 remains conditional on proved rule lemmas and implementation invariants.
