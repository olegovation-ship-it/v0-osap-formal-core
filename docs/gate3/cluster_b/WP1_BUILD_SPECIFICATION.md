# V0 OSAP v1.4.0 Gate 3 Cluster B WP1 Build Specification v0.1

**Work package:** WP1 — Cluster Registry, Strong DLE, and ID Closure
**Repository:** `olegovation-ship-it/v0-osap-formal-core`
**Branch:** `v1.4.0-development`
**Exact WP1 baseline:** `f79bc16da3a4aa53c1e0cbbbbb65f003fea42e15`
**Date:** 2026-07-20
**Decision:** `APPROVED_FOR_BOUNDED_IMPLEMENTATION`
**Release authorization:** `NONE`

## 1. Purpose

WP1 converts the provisional Cluster B plan into a canonical statement-and-ownership surface. It closes theorem-ID ownership, the seven-role map, the typed StrongDLE/residual contracts, and the dependency DAG. It does **not** implement executable semantics, fixtures, IPEC extension bindings, Lean proofs, Coq proofs, release tags, GitHub Releases, Zenodo records, or DOI changes.

## 2. Frozen baseline

- WP0 post-merge closeout merge commit: `f79bc16da3a4aa53c1e0cbbbbb65f003fea42e15`.
- Frozen OSAP v1.3.0 tag target: `13bf095688bcabd5b090f188e9bd28a16237edeb`.
- Frozen V0-IPEC v0.1 commit: `5474a2c6a3e1c274d17f674889d427c1c91572f7`.
- Frozen Validator Core v0.12 tag target: `3540f47198140ca0a3612f247cfe356fa7fba2cb`.
- Paper B remains frozen as submitted manuscript `SCICO-D-26-00508`.
- Submission register v121 remains the operative governance baseline.

Closed WP0 records are immutable. WP1 may modify only the bounded WP1 surface and the WP0 verifier/test allowlist needed to recognize that surface.

## 3. WP1 outputs

1. Exact WP1 baseline lock.
2. Collision audit for T157–T162.
3. Seven-role ownership map.
4. Canonical glossary and six typed contracts.
5. Six complete theorem target records.
6. Acyclic dependency DAG with T131 and T133 declared as external inherited dependencies.
7. Sixteen local acceptance gates.
8. Eight-schema bundle and deterministic SHA-256 ledger.
9. Dedicated builder, verifier, regression tests, and hosted workflow.

## 4. Theorem-ID closure rule

T157–T162 are accepted for canonicalization in WP1. Their IDs and statements become canonical only after the WP1 PR merges into `main`. Before merge they remain `ACCEPTED_FOR_CANONICALIZATION_PENDING_WP1_MERGE`.

A collision is:

- a second ownership record containing `theorem_id`, `canonical_name`, and `formal_signature`; or
- a Lean/Coq formal declaration using a reserved ID outside the future authorized WP4 modules.

Textual references and downstream rule bindings are not ownership collisions.

## 5. Locked theorem targets

| ID | Canonical name | Dependencies | Conditional | Deferred implementation |
|---|---|---|---|---|
| T157 | `strong_dle_characterization` | T123, T132 | no | WP4 proof |
| T158 | `live_residual_persistence_under_noninterfering_dle` | T124, T132, T139, T162 | yes | WP2 semantics; WP4 proof |
| T159 | `residual_type_separation` | T131, T139 | no | WP2 semantics; WP4 proof |
| T160 | `model_pair_noneliminability_witness` | T134, T135, T140, T142, T159 | yes | WP2 model pairs; WP4 proof |
| T161 | `minimal_single_residual_obstruction` | T134 | no | WP4 corollary proof |
| T162 | `historical_live_token_nonconversion` | T133, T139 | no | WP2 semantics; WP4 proof |

T158 now explicitly depends on T162, matching the required nonconversion discipline.

## 6. Seven semantic roles

All seven roles receive canonical owners at the registry level: DLE transition, Strong DLE, live-residual persistence, raw residual obstruction, model-pair non-eliminability, robust obstruction, and branch-local firewall. Registry closure is not proof closure; new proofs remain deferred to WP4.

## 7. Contract perimeter

The contracts are finite-record, typed, and provenance-bearing. They do not assert proof-term identity, kernel equivalence, unrestricted cross-backend semantic equivalence, checker completeness, global soundness, empirical confirmation, physical disappearance, cosmological vacuum ontology, or absolute-V0 existence.

T158 and T160 remain conditional. T140, T150, and T156 retain their inherited conditional status.

## 8. Repository paths

WP1 adds only:

- `.github/workflows/gate3-cluster-b-wp1.yml`;
- `docs/gate3/cluster_b/WP1_*`;
- `release/v1.4.0/GATE3_CLUSTER_B_WP1_*`;
- `schemas/v1.4.0/gate3_cluster_b_wp1_*`;
- `scripts/build_gate3_cluster_b_wp1.py`;
- `scripts/verify_gate3_cluster_b_wp1.py`;
- `tests/test_gate3_cluster_b_wp1.py`;
- the bounded allowlist patch under `release/v1.4.0/tools/`.

WP1 does not create `checker/`, `fixtures/`, `lean/`, or `coq/` Cluster B implementation modules.

## 9. Verification sequence

1. Apply the repository overlay.
2. Run the idempotent WP0 allowlist patch.
3. Run the WP1 builder.
4. Run the inherited WP0 verifier.
5. Run the WP1 verifier.
6. Run WP0 and WP1 tests.
7. Run `git diff --check f79bc16da3a4aa53c1e0cbbbbb65f003fea42e15 --`.
8. Open a PR and require all hosted checks before merge.

## 10. Exit condition

WP1 closes when:

- T157–T162 are collision-free and merged;
- six ownership records and seven role owners are complete;
- the typed contracts and DAG validate;
- all local and hosted checks pass;
- no release action or frozen-upstream mutation occurs.

**Build specification: APPROVED. Implementation patch: PROVIDED SEPARATELY. Release: NOT AUTHORIZED.**
