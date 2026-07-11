# V0 OSAP Formal Core

[![Schema validation](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/schema-check.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/schema-check.yml)
[![Python checker](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/python-checker.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/python-checker.yml)
[![Lean 4](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/lean4.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/lean4.yml)
[![Coq](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/coq.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/coq.yml)
[![Release readiness](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/release-readiness.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/release-readiness.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21306969.svg)](https://doi.org/10.5281/zenodo.21306969)

Executable and proof-assistant-facing formal core for the **V0 Ontological and Structural-Activation Program (V0 OSAP)**.

## v1.3.0 development status

> **PHASE 1 SEMANTIC ALIGNMENT PATCH - PATCH READY / CI PENDING**

The development branch aligns executable coverage for T122, T124, and T125:

- T122: exact empty-`all_of` vacuity fixture and schema erratum;
- T124: explicit robust-relative-V0 residual-obstruction rule and paired fixtures;
- T125: exact terminal-support-exhaustion rule, separated from observer admissibility;
- checker development version: `0.2.0.dev1`.

This is not a v1.3.0 release and is not yet a compiler-passed claim. See `release/v1.3.0/PHASE1_ACCEPTANCE_GATES.md`.

## v1.2.0 release status

> **V0 OSAP v1.2.0 - DUAL-BACKEND COMPILER-PASSED FC-1 BASELINE**

- Imported specification: **V0 OSAP v1.1 / FC-1-v1.1**.
- Canonical JSON Schemas: JSON Schema Draft 2020-12.
- Python checker release version: `0.1.0` in the immutable tag.
- Lean 4 and Coq passed on the archived baseline.
- GitHub Release: [v1.2.0](https://github.com/olegovation-ship-it/v0-osap-formal-core/releases/tag/v1.2.0).
- Zenodo version DOI: [10.5281/zenodo.21306969](https://doi.org/10.5281/zenodo.21306969).

The compiler-passed claim remains bounded to the archived FC-1 implementation and T121-T126. The tag `v1.2.0` must not be moved or retagged.

## Scope

FC-1 checks a finite, typed registry fragment covering live-state guards, prerequisite support, domain-license exhaustion, residual obstruction, observer-certificate limits, branch locality, canonical serialization, and deterministic fixture replay.

This repository is a formal-semantics and verification artifact. It is **not** empirical confirmation of a physical vacuum, cosmology, disappearance mechanism, quantum-gravity model, or multiverse.

## Local development checks

```bash
python -m pip install -e '.[dev]'
pytest -q
v0-osap-fc1 schema-bundle
v0-osap-fc1 fixtures
python scripts/check_no_proof_holes.py
python scripts/verify_phase1_alignment.py
cd lean && lake build
cd ../coq && make
```

## License

MIT. See [LICENSE](LICENSE).
