# V0 OSAP Formal Core

[![Schema validation](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/schema-check.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/schema-check.yml)
[![Python checker](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/python-checker.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/python-checker.yml)
[![Lean 4](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/lean4.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/lean4.yml)
[![Coq](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/coq.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/coq.yml)
[![Release readiness](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/release-readiness.yml/badge.svg)](https://github.com/olegovation-ship-it/v0-osap-formal-core/actions/workflows/release-readiness.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21306969.svg)](https://doi.org/10.5281/zenodo.21306969)

Executable and proof-assistant-facing formal core for the **V0 Ontological and Structural-Activation Program (V0 OSAP)**.

## v1.3.0 development status

<!-- V0_OSAP_RC1_GATE_AUDIT_BEGIN -->
> **V0 OSAP v1.3.0 RC1 TAG AUTHORIZATION AND GITHUB PRERELEASE PREPARATION - RC1_TAG_AUTHORIZED / TAG_NOT_CREATED / PRERELEASE_NOT_CREATED**

PR #13 completed the RC1 release-closure stage and merged as
`cf9a05b46b9b6f29cd85942f99155f89a49817a7`. Post-merge GitHub Actions checks for Python, schema validation,
RC1 gate audit, release readiness, clean-room release replay, Lean 4, and Coq
were observed successful on `main`; the corresponding synchronized development
checks also passed.

This patch separately authorizes `cf9a05b46b9b6f29cd85942f99155f89a49817a7` as the only permitted target for the
annotated tag `v1.3.0-rc1`. It installs a final tag message, target-specific
authorization record, GitHub pre-release metadata and notes, deterministic
authorization manifest, validation-only CI workflow, and explicit dry-run-first
creation scripts.

Applying or merging this patch creates no tag and no GitHub Release. After the
authorization PR itself passes CI and is merged, the annotated tag and pre-release
must be created by separate explicit commands and then recorded by a subsequent
evidence-closure patch.

Historical tag `v1.2.0`, target `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3`, and DOI `10.5281/zenodo.21306969` remain
immutable. T140, T150, and T156 remain conditional. The final tag `v1.3.0`,
Zenodo publication, and DOI mutation remain unauthorized.

See `release/v1.3.0/RC1_TAG_AUTHORIZATION_AND_GITHUB_PRERELEASE_SPECIFICATION.md`
and `release/v1.3.0/RC1_TAG_AUTHORIZATION_GATES.md`.
<!-- V0_OSAP_RC1_GATE_AUDIT_END -->


> **PHASE 6 T151-T156 EXTENSION PROVENANCE, VOCABULARY, DIAGNOSTIC, EVIDENCE, VERSION-LOCK, AND CONSERVATIVITY EXPANSION - ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED**

Phase 6 introduces an explicit post-v1.1 development extension for T151-T156. It adds extension provenance, declared claim-vocabulary closure, diagnostic-envelope determinism, finite evidence-provenance acyclicity, version-lock coherence, and conditional conservative non-interference. Checker version: `0.7.0.dev1`.

PR #10 passed 8/8 checks and merged head commit
`dd1b234647a96b31719da0f3c5ad5e91b40144da` into `main` as
`306f80dd36a70211b04f9a64215cc8807cbce709`. The regression suite recorded
15 passing tests, and both Lean 4 and Coq builds passed.

The implementation was built from the preserved Phase 5 closure baseline
`8053709c73045f59358244ec58afc84cfd0deeb6`. The patch includes twelve paired fixtures,
Lean 4 and Coq Phase 6 modules, and a canonical statement-hash crosswalk.
This is an accepted v1.3.0 development state, not a v1.3.0 release.
T151-T156 remain explicit extension IDs beyond the normative v1.1 ceiling T150,
and T156 remains conditional. See
`release/v1.3.0/PHASE6_ACCEPTANCE_GATES.md` and
`release/v1.3.0/PHASE6_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md`.

### Phase 5 closed baseline

> **PHASE 5 T145-T150 CANONICALIZATION, REPLAY, MIGRATION, CORRESPONDENCE, AND SOUNDNESS EXPANSION - ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED**

Phase 5 adds V0-OSAP-CJ-1 canonical serialization and round-trip audits, pinned replay determinism, explicit schema-migration visibility, backend statement-hash correspondence, and conditional accepted-fragment checker soundness. Checker version: `0.6.0.dev1`.

PR #8 passed 8/8 checks and merged head commit
`977c5404ebc5cdef9495edd1c46b08d3b0452acb` into `main` as
`5c689de1a30104aa6c4e3860d5e7c26746e2d797`. The regression suite recorded
14 passing tests, and both Lean 4 and Coq builds passed.

The implementation was built from the preserved Phase 4 closure baseline
`2a769d7723470cce59df81262b586abf19b9c750`. The patch includes twelve paired fixtures,
Lean 4 and Coq Phase 5 modules, and a canonical statement-hash crosswalk.
This is an accepted v1.3.0 development state, not a v1.3.0 release. T150
remains conditional on proved rule lemmas and implementation invariants. See
`release/v1.3.0/PHASE5_ACCEPTANCE_GATES.md` and
`release/v1.3.0/PHASE5_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md`.

### Phase 4 closed baseline

> **PHASE 4 T139-T144 ARCHIVE, BRANCH, CARDINALITY, AND DIAGNOSTIC EXPANSION - ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED**

Phase 4 adds archive non-guard export, independent-witness conditional sufficiency,
the no-container and branch-label firewalls, non-finite cardinality licensing, and
finite diagnostic-precedence totality. Checker version: `0.5.0.dev1`.

PR #6 passed 8/8 checks and merged head commit
`9cec516c8ab026ce8d63fd2303f72ec5c1d36351` into `main` as
`417866ec94fb24891c00bdfc2e522095777532bf`. The regression suite recorded
113 passing tests, and both Lean 4 and Coq builds passed.

The implementation was built from the preserved Phase 3 closure baseline
`24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30`. The patch includes twelve paired fixtures,
Lean 4 and Coq Phase 4 modules, and a canonical statement-hash crosswalk.
This is an accepted v1.3.0 development state, not a v1.3.0 release. See
`release/v1.3.0/PHASE4_ACCEPTANCE_GATES.md` and
`release/v1.3.0/PHASE4_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md`.

### Phase 3 closed baseline

> **PHASE 3 T133-T138 FIREWALL EXPANSION - ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED**

Phase 3 adds fresh-token reactivation, raw and robust residual obstruction,
relative-to-absolute non-promotion, approximation non-identity, and terminal
same-state self-certification limits. Checker version: `0.4.0.dev1`.

PR #4 passed 8/8 checks and merged head commit
`2172591ed8a5ab3c1fa31f2a3a6575536f161fe4` into `main` as
`c02b05f667b82aa31ac8865c31219b94b1fc74d2`. The regression suite recorded
112 passing tests, and both Lean 4 and Coq builds passed.

The patch includes twelve paired fixtures, Lean 4 and Coq Phase 3 modules, and a
canonical statement-hash crosswalk. This is an accepted v1.3.0 development state,
not a v1.3.0 release. See `release/v1.3.0/PHASE3_ACCEPTANCE_GATES.md` and
`release/v1.3.0/PHASE3_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md`.

### Phase 2 closed baseline

> **PHASE 2 T127-T132 EXPANSION - ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED**

Phase 2 adds T127 closure minimality, T128 one_of support transparency,
T129 compatibility preservation, T130 dimensional readiness, T131 undefined-domain
separation from numeric zero, and T132 DLE history adequacy. Checker version: `0.3.0.dev1`.

PR #2 passed 8/8 checks and merged head commit
`90865cca5fafde161254b7e313621d369ae5efc5` into `main` as
`f494cd9401e2b9ff91d87de77e11f4eb2468726c`. The local regression suite recorded
111 passing tests, and both Lean 4 and Coq builds passed.

The patch includes twelve paired fixtures, Lean 4 and Coq expansion modules, and a
canonical statement-hash crosswalk. This is an accepted v1.3.0 development state,
not a v1.3.0 release. See `release/v1.3.0/PHASE2_ACCEPTANCE_GATES.md` and
`release/v1.3.0/PHASE2_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md`.

### Phase 1 closed baseline

> **PHASE 1 SEMANTIC ALIGNMENT - ACCEPTED / CI PASS**

The development branch aligns executable coverage for T122, T124, and T125:

- T122: exact empty-`all_of` vacuity fixture and schema erratum;
- T124: explicit robust-relative-V0 residual-obstruction rule and paired fixtures;
- T125: exact terminal-support-exhaustion rule, separated from observer admissibility;
- checker development version: `0.2.0.dev1`.

The Phase 1 acceptance matrix passed for Schema validation, Python checker, Lean 4, Coq, and Release readiness. The immutable-v1.2.0 readiness job retains both manifest and closure verification.

This is not a v1.3.0 release and does not extend the archived v1.2.0 compiler-passed claim. See `release/v1.3.0/PHASE1_ACCEPTANCE_GATES.md` and `release/v1.3.0/PHASE1_CI_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md`.

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
python scripts/verify_phase2_expansion.py
python scripts/verify_phase2_ci_closure.py
python scripts/verify_phase3_expansion.py
python scripts/verify_phase3_ci_closure.py
python scripts/verify_phase4_expansion.py
python scripts/verify_phase4_ci_closure.py
python scripts/verify_phase5_expansion.py
python scripts/verify_phase5_ci_closure.py
python scripts/verify_phase6_expansion.py
python scripts/verify_phase6_ci_closure.py
cd lean && lake build
cd ../coq && make
```

The archived baseline closure check is executed by the Release readiness workflow after checking out the immutable `v1.2.0` tag.

## License

MIT. See [LICENSE](LICENSE).
