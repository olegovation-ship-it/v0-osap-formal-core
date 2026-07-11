# V0 OSAP v1.3.0 Phase 1 Semantic Alignment and Blocker Closure Patch v0.1

Status: `PATCH_READY / CI_PENDING`
Date: 2026-07-11
Baseline: immutable `v1.2.0`, DOI `10.5281/zenodo.21306969`

## Objective

Close the three crosswalk blockers identified after the v1.3.0 build-plan audit while preserving the archived v1.2.0 tag:

1. T122 lacked an exact executable fixture because the schema prohibited an empty prerequisite list.
2. T124 lacked a direct Python rule and paired theorem-target fixtures.
3. T125 conflated terminal support exhaustion with operational observer admissibility.

## Repairs

### T122

- Correct the schema so empty `all_of` families are permitted and vacuously satisfied.
- Preserve the nonempty requirement for `one_of` families.
- Add `fixture:positive:t122_empty_all_prerequisites`.
- Remove T122 attribution from the legacy missing-prerequisite countermodel.

### T124

- Add claim kind `robust_relative_v0`.
- Add diagnostic `LIVE_RESIDUAL_OBSTRUCTS_ROBUST_RELATIVE_V0`.
- Add positive and countermodel fixtures with exact T124 attribution.

### T125

- Keep T125 equal to terminal support exhaustion in Python, Lean 4, and Coq.
- Add diagnostic `TERMINAL_SELF_CERTIFICATE_NOT_EXHAUSTED`.
- Add exact positive and countermodel fixtures.
- Introduce `AdmissibleObserverCertificate` as a separate unnumbered predicate.
- Replace the old conflated diagnostic with `OBSERVER_CERTIFICATION_SUPPORT_REQUIRED` and remove T125 attribution.

## Release discipline

This package is not a v1.3.0 release. It must be applied on `v1.3.0-development` or an equivalent development branch. The tag `v1.2.0` must not be moved. Phase 1 closes only after Python, schema, Lean 4, Coq, proof-hole, and crosswalk checks are all green on the installed repository state.
