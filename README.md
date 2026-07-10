# V0 OSAP Formal Core

[![Schema validation](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/schema-check.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/schema-check.yml)
[![Python checker](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/python-checker.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/python-checker.yml)
[![Lean 4](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/lean4.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/lean4.yml)
[![Coq](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/coq.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/coq.yml)

Executable and proof-assistant-facing formal core for the **V0 Ontological and Structural-Activation Program (V0 OSAP)**.

## Bootstrap status

- Specification imported: **V0 OSAP v1.1 / FC-1-v1.1**.
- Canonical JSON Schemas: Draft 2020-12.
- Python checker: bootstrap implementation with deterministic diagnostics and fixture replay.
- Lean 4 mapping: source skeleton included; compiler status is established only by the GitHub Actions result.
- Coq mapping: source skeleton included; compiler status is established only by the GitHub Actions result.
- Release / Zenodo DOI: **not yet created**.

The repository must not be described as dual-backend compiler-passed until both the Lean 4 and Coq workflows pass on the target commit and the release-readiness checks are satisfied.

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
lean/               Lean 4 source skeleton
coq/                Coq source skeleton
docs/               normative specification and architecture notes
scripts/            manifest and static-integrity utilities
.github/workflows/  CI workflows
```

## Local Python check

```bash
python -m pip install -e '.[dev]'
v0-osap-fc1 schema-bundle
v0-osap-fc1 fixtures
pytest -q
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

## Evidence levels

`E0_SPECIFIED` → `E1_SCHEMA_VALID` → `E2_CHECKER_REPLAYED` → `E3_MODEL_WITNESSED` → `E4_PROOF_ASSISTANT_COMPILED` → `E5_CROSS_ASSISTANT_REPLAYED`.

Bootstrap files do not by themselves establish E4 or E5.

## License

MIT. See [LICENSE](LICENSE).
