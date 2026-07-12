# V0 OSAP v1.3.0 Phase 4 Build Specification and Implementation Patch v0.1

**Artifact ID:** `V0_OSAP_v1_3_0_PHASE4_T139_T144`
**Date:** 2026-07-12
**Target branch:** `v1.3.0-development`
**Baseline:** Phase 3 accepted, CI-closed, merged, and historically preserved
**Baseline merge commit:** `24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30`
**Immutable release baseline:** tag `v1.2.0`, DOI `10.5281/zenodo.21306969`
**Implementation state:** `BUILD_READY / CI_PENDING`
**Checker development version:** `0.5.0.dev1`
**Author:** Dmytro Panasenko, Independent Researcher

## 1. Decision summary

Phase 4 extends the accepted development surface from T121-T138 to a build-ready T139-T144 cluster. It implements archive/witness discipline, branch and cardinality firewalls, and deterministic diagnostic precedence. It does not release v1.3.0 and does not enlarge the archived v1.2.0 claim.

| ID | Canonical theorem target | Executable obligation |
|---|---|---|
| T139 | Archive non-guard-export | An archive record cannot export a current observer guard. |
| T140 | Independent-witness conditional sufficiency | A witness certificate requires policy compliance, non-circularity, identity/evidence verification, external evidence, and an independence group. |
| T141 | No-container | A NullMark cannot stand in an ordinary Contains relation to a Branch. |
| T142 | Branch-label insufficiency | `label_only` cannot license branch distinctness; non-label bases require evidence. |
| T143 | Cardinality licensing | A non-finite cardinality claim requires a typed `meta_index_certificate` evidence object and proof evidence. |
| T144 | Diagnostic precedence totality | A finite closed-status list has one deterministic primary status under `STATUS_RANK`. |

## 2. Normative source discipline

The theorem names and target statements are inherited from V0 OSAP v1.1. Phase 4 preserves the rules that archives do not export current guards, witness independence is explicit, V0 is not an ordinary container, labels are not identity proofs, non-finite cardinality requires a licensed meta-index, and diagnostic results are deterministic.

## 3. Machine-readable extension

New claim kinds:

- `archive_guard_export`
- `external_witness_certificate`
- `v0_branch_containment`
- `branch_distinctness`
- `branch_cardinality`
- `diagnostic_precedence_audit`

New claim fields include archive/witness identifiers, policy booleans, containment mode, branch-distinctness basis, cardinality kind, meta-index evidence, and finite diagnostic-status lists.

## 4. Diagnostics

- `ARCHIVE_CANNOT_EXPORT_CURRENT_GUARD`
- `INDEPENDENT_WITNESS_CERTIFICATE_UNSUPPORTED`
- `CONTAINMENT_REFERENCE_SORT_MISMATCH`
- `V0_ORDINARY_CONTAINS_FORBIDDEN`
- `BRANCH_LABELS_DO_NOT_PROVE_DISTINCTNESS`
- `BRANCH_DISTINCTNESS_EVIDENCE_REQUIRED`
- `DEFERRED_CARDINALITY_CERT`
- `DIAGNOSTIC_PRIMARY_STATUS_MISMATCH`

## 5. Proof-assistant implementation

`V0OSAP.Phase4` and `Phase4.v` provide bounded finite-record formalizations for T139-T144. The root aggregation modules and Coq project list are extended. Compilation is evidence for these encoded propositions only; it is not a proof of semantic identity between Python, Lean 4, and Coq.

## 6. Fixture and crosswalk contract

Each theorem target has one positive fixture and one decisive countermodel. The Phase 4 crosswalk records canonical statements, formal signatures, assumptions, conclusions, backend symbols, validator rules, diagnostics, fixture IDs, limitations, and SHA-256 statement hashes.

## 7. Acceptance gates

1. Editable Python install succeeds.
2. Full Python regression suite passes; expected total after this patch: 113 tests.
3. Schema bundle validation passes.
4. Deterministic replay of all fixtures passes.
5. Proof-hole scan passes.
6. Phase 1 preservation verifier passes.
7. Phase 2 expansion and CI-closure verifiers pass.
8. Phase 3 expansion and CI-closure verifiers pass.
9. Phase 4 expansion verifier passes.
10. Lean 4 build passes.
11. Coq build passes.
12. `git diff --check` passes.
13. GitHub Actions returns an all-green matrix before acceptance or merge.

## 8. Claim boundary

This patch does not move or retag `v1.2.0`, does not alter DOI `10.5281/zenodo.21306969`, does not create a new release, and does not claim completion of T145-T150, checker completeness, cross-assistant proof identity, physical multiplicity, multiverse evidence, or empirical validation.
