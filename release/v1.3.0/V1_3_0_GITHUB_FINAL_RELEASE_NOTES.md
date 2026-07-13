# V0 OSAP v1.3.0 — Stable Release

This stable GitHub release publishes the accepted V0 OSAP formal-core corpus at the
separately authorized exact target `13bf095688bcabd5b090f188e9bd28a16237edeb`.

## Included scope

- theorem inventory `T121-T156`;
- 36 theorem records and 6 source crosswalks;
- executable Python checker and regression suite;
- canonical JSON Schema validation;
- deterministic positive/countermodel fixture replay;
- Lean 4 and Coq mappings;
- theorem-crosswalk and manifest evidence;
- release-gate audit, clean-room replay, RC1 publication evidence, and historical controls.

## Conditional records

`T140`, `T150`, and `T156` remain conditional under their recorded premises and implementation
invariants.

## Version boundary

The repository release identifier is `v1.3.0`. The embedded checker component remains
`0.7.0.dev1` exactly as audited. No silent component-version promotion is made.

## Non-claims

This release does not claim proof-term identity, unrestricted semantic equivalence, checker
completeness, unconditional global checker soundness, global conservativity, or empirical,
physical, or cosmological validation.

## Historical preservation

Historical tag `v1.2.0`, target `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3`, and DOI `10.5281/zenodo.21306969` remain
immutable. This GitHub release does not create a Zenodo version and does not mutate any DOI.
