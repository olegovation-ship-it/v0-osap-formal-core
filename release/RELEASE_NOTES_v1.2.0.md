# V0 OSAP Formal Core v1.2.0 — Compiler-Passed FC-1 Baseline

## Summary

This release closes the v1.2 repository bootstrap as a bounded compiler-passed formal baseline for the V0 Ontological and Structural-Activation Program.

## Verified components

- JSON Schema Draft 2020-12 bundle: PASS
- Python FC-1 checker and fixture replay: PASS
- Lean 4: `Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release)` — `lake build` PASS
- Coq: `The Coq Proof Assistant, version 8.18.0` — `make` PASS
- Proof-hole scan: PASS
- Release manifest integrity: PASS
- Evidence commit: `48db564c085aec411552e78eef6c1740bd27a5ac`

## Mechanized scope

The current dual-backend subset is T121-T126:

- live-guard witness existence;
- empty prerequisite-family vacuity;
- DLE implies current no-live status;
- live residual obstruction to robust relative V0;
- terminal self-certification support exhaustion;
- branch-local to absolute-promotion firewall.

## Repair included

Lean 4 reserved identifiers in the branch-firewall definitions and T126 wrapper were replaced without changing the intended theorem content.

## Non-claims

This release does not claim complete mechanization of T1-T150, cross-assistant proof equivalence, empirical confirmation of V0, or a physical/cosmological model.

## Archival status

Zenodo DOI: pending. The DOI and repository backlink must be added in a later citation-finalization patch after archival.
