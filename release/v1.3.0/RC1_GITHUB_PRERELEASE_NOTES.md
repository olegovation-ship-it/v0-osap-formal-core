# V0 OSAP v1.3.0-rc1 — Release Candidate 1

This is the first release candidate for the V0 OSAP formal core.

## Candidate scope

- Frozen theorem inventory: T121-T156, 36 records.
- Six canonical source crosswalks.
- Twelve negative release-gate mutants.
- Python checker and JSON Schema validation.
- Deterministic positive and countermodel fixture replay.
- Lean 4 and Coq mappings/builds.
- RC1 gate audit, structural-record parity, release-closure manifest, and
  clean-room replay.
- Exact source target: `cf9a05b46b9b6f29cd85942f99155f89a49817a7`.

## Conditional results and limitations

T140, T150, and T156 remain conditional on their recorded premises and
implementation invariants.

This release candidate does not claim checker completeness, unconditional global
checker soundness, proof-term identity between Lean and Coq, unrestricted
semantic equivalence, global conservativity, empirical confirmation of a
physical vacuum, a cosmological mechanism, disappearance dynamics, or a
multiverse.

## Historical preservation

The immutable historical release `v1.2.0` remains pinned to
`befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3`. Its DOI remains `10.5281/zenodo.21306969`.

This GitHub pre-release does not create or alter a Zenodo version or DOI.
