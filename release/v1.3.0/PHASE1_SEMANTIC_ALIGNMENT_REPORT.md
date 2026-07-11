# V0 OSAP v1.3.0 Phase 1 Semantic Alignment and Blocker Closure Patch v0.1

Status: `ACCEPTED / CI_PASS`
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

## CI closure

- Schema validation: PASS.
- Python checker and regression suite: PASS.
- Lean 4 build and proof-hole scan: PASS.
- Coq build and proof-hole scan: PASS.
- Release readiness: PASS.
- Phase 1 semantic-alignment verifier: PASS.

## Historical preservation

- The immutable `v1.2.0` tag and DOI are unchanged.
- The immutable-baseline workflow retains both `verify_manifest.py` and `verify_closure.py`.
- The detailed v1.2.0 changelog record is preserved rather than collapsed into a summary line.

## Release discipline

This package is not a v1.3.0 release. It applies on `v1.3.0-development` or an equivalent development branch. Phase 1 acceptance does not move the v1.2.0 tag, create a new DOI, or extend the archived compiler-passed claim.
