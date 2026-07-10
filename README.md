# V0 OSAP Formal Core

[![Schema validation](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/schema-check.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/schema-check.yml)
[![Python checker](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/python-checker.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/python-checker.yml)
[![Lean 4](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/lean4.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/lean4.yml)
[![Coq](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/coq.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/coq.yml)
[![Release readiness](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/release-readiness.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/release-readiness.yml)

Executable and proof-assistant-facing formal core for the **V0 Ontological and Structural-Activation Program (V0 OSAP)**.

## v1.2.0 release status

> **V0 OSAP v1.2.0 — DUAL-BACKEND COMPILER-PASSED FC-1 BASELINE**

- Imported specification: **V0 OSAP v1.1 / FC-1-v1.1**.
- Canonical JSON Schemas: JSON Schema Draft 2020-12.
- Python checker: deterministic diagnostics and fixture replay, package version `0.1.0`.
- Lean 4: `Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release)`; `lake build` passed with the proof-hole scan.
- Coq: `The Coq Proof Assistant, version 8.18.0`; `make` passed with the proof-hole scan.
- CI evidence commit: `48db564c085aec411552e78eef6c1740bd27a5ac`.
- Closure metadata generated: `2026-07-10T22:33:40Z`.
- GitHub Release / Zenodo DOI: **DOI: pending** until the tagged release is archived.

The compiler-passed claim is bounded to the current FC-1 implementation and the initial theorem subset T121-T126. It is not a claim that all T1-T150 are mechanized.

## Scope

FC-1 checks a finite, typed registry fragment covering:

- live, historical, retired, and deferred token separation;
- guard-before-value discipline;
- prerequisite-family support;
- domain-license exhaustion (DLE);
- residual obstruction;
- observer-reflexive certification limits;
- universe-branch locality and absolute/relative V0 separation;
- canonical serialization and reproducible fixture replay.

This repository is a formal-semantics and verification artifact. It is **not** empirical confirmation of a physical vacuum, cosmology, disappearance mechanism, quantum-gravity model, or multiverse.

## Repository layout

```text
schemas/v1.1/       canonical v1.1 schema bundle
fixtures/           positive and countermodel registry fixtures
checker/            Python FC-1 checker
lean/               Lean 4 formalization
coq/                Coq formalization
docs/               normative specification and architecture notes
release/            compiler versions, manifest, preflight, and release notes
scripts/            manifest, closure, and static-integrity utilities
.github/workflows/  CI workflows
```

## Local checks

```bash
python -m pip install -e '.[dev]'
pytest -q
v0-osap-fc1 schema-bundle
v0-osap-fc1 fixtures
python scripts/check_no_proof_holes.py
python scripts/verify_manifest.py
python scripts/verify_closure.py
```

## Lean 4

```bash
cd lean
lake build
```

## Coq

```bash
cd coq
make
```

## Canonicalization

The canonical JSON profile is `V0-OSAP-CJ-1`: UTF-8, object keys sorted lexicographically, no insignificant whitespace, arrays retained in declared order, and one terminal LF.

## Evidence level

For T121-T126, the repository establishes a bounded dual-backend compiled state: Lean 4 and Coq sources compile, proof-hole markers are rejected, and the Python fixtures replay. This does not prove proof-term identity, semantic equivalence between assistants, theorem completeness, or empirical truth of V0.

## Release policy

The annotated tag `v1.2.0` may be created only after the closure commit passes all five workflows. A DOI must be added only after the immutable GitHub Release is archived by Zenodo.

## License

MIT. See [LICENSE](LICENSE).
