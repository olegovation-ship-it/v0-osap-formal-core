# V0 OSAP v1.4.0 Gate 3 Cluster B WP3 Build Specification v0.1.1

**Work package:** WP3 — Validator/IPEC Extension and Typed Outcome Binding
**Repository:** `olegovation-ship-it/v0-osap-formal-core`
**Target branch:** `v1.4.0-development`
**Exact candidate WP3 baseline:** `7b49aa76fef65bced7141a639e8ef6fe3b5ba313`
**Date:** 2026-07-22
**Build decision:** `APPROVED_FOR_CHECK`
**Apply decision:** `CHECK_REQUIRED_BEFORE_APPLICATION`
**Release authorization:** `NONE`

## 1. Repository and source audit

The operative Gate 3 Cluster B roadmap assigns WP3 a new versioned Validator/IPEC extension layer. Frozen V0-IPEC v0.1 must not be edited, and every nonprocedural typed outcome must retain theorem lineage and evidence lineage.

The inherited ownership boundary is:

- WP0: baseline freeze, branch bootstrap, and frozen-upstream preservation;
- WP1: canonical contracts, theorem IDs `T157`–`T162`, seven-role map, and dependency DAG;
- WP2: executable finite-record semantics, nine case types, 28 fixtures, schemas, acceptance records, and canonical SHA-256 ledger;
- WP3: adapter/rule extension, exact IPEC outcome compatibility, diagnostic transport, and theorem/evidence lineage binding;
- WP4: Lean/Coq proof completion and statement parity for `T157`–`T162`.

WP3 consumes WP2 results exactly; it does not reinterpret or rewrite WP2 semantics.

## 2. Uploaded-input audit

The uploaded files are sufficient:

- `...WP2_Post_Merge...Patch_v0.1.1.zip` is the operative closeout package;
- its supplied SHA-256 value matches the ZIP: `1a7ef53a2f84151558035bb577ccf1cd1ad4a4ee997863c9edb44ef85555bf9b`;
- `...Patch_v0.1.zip` is superseded and is not needed for WP3 construction;
- no separate WP2 implementation ZIP is required because the merged WP1/WP2 records are available in the repository.

## 3. Exact baseline and synchronization gate

The recorded identities are:

- WP2 accepted head: `b0f5fc5b0d5103e1bb22b06ca51716d40e22a5d7`;
- WP2 merge commit: `b6370af53add3fdff1ddb48824dd76ebba3aaa32`;
- WP2 post-merge closeout commit: `ea029430b96fd3b90acbf4cb4419564eff583210`;
- WP2 closeout CI-dispatch repair head: `9160b8199f42e75c1a554b45793852e8d9aafdb5`;
- PR #24 closeout merge commit and exact WP3 baseline: `7b49aa76fef65bced7141a639e8ef6fe3b5ba313`.

`origin/main`, `origin/v1.4.0-development`, and the clean working-tree `HEAD` are synchronized at the final PR #24 merge commit. The applicator therefore refuses both `--check` and apply unless:

1. the current branch is exactly `v1.4.0-development`;
2. the working tree is clean;
3. `HEAD == 7b49aa76fef65bced7141a639e8ef6fe3b5ba313`;
4. `origin/main == 7b49aa76fef65bced7141a639e8ef6fe3b5ba313`;
5. `origin/v1.4.0-development == 7b49aa76fef65bced7141a639e8ef6fe3b5ba313`.

This locks WP3 to the exact, fully merged and synchronized WP2 closeout baseline and prevents execution on the pre-merge closeout head or repair head.

## 4. Frozen external contracts

WP3 pins, but does not edit:

- V0-IPEC v0.1 closeout commit `5474a2c6a3e1c274d17f674889d427c1c91572f7`;
- V0-IPEC typed-outcome records SHA-256 `4e05803bd53ecc7ed0c7926fddfb9ad517c8b14b3c795217df511a11cae60bfb`;
- Validator Core v0.12 frozen target `3540f47198140ca0a3612f247cfe356fa7fba2cb`;
- OSAP v1.3.0 frozen target `13bf095688bcabd5b090f188e9bd28a16237edeb`.

The exact V0-IPEC v0.1 typed-outcome vocabulary remains:

1. `BACKEND_PARITY_FAILURE`;
2. `REJECTED_BRANCH_PROMOTION`;
3. `REJECTED_NONELIM_OBSTRUCTION`;
4. `REJECTED_LIVE_RESIDUAL`;
5. `REJECTED_DLE_FAILURE`;
6. `REJECTED_GUARD_FAILURE`;
7. `INCONCLUSIVE_UNSUPPORTED_FRAGMENT`;
8. `CERTIFIED`.

WP3 does not invent replacement outcome codes.

## 5. Certification and proof boundary

V0-IPEC `CERTIFIED` requires coherent evidence lineage and required Lean/Coq backend evidence. WP4 has not yet completed the new proofs for `T157`–`T162`. Therefore WP3:

- records `CERTIFIED` as the candidate outcome for a WP2 `PASS`;
- emits `INCONCLUSIVE_UNSUPPORTED_FRAGMENT` until WP4 binds the required backend proof evidence;
- never claims certification in this package;
- defers a rejection whose lineage contains any of `T157`–`T162`, while preserving the exact candidate rejection code;
- may bind a rejection immediately only when its full lineage is inherited from the frozen proved range `T121`–`T156`.

This avoids fabricated certification and fabricated theorem-backed rejection.

## 6. Versioned extension-rule layer

The six new theorem targets receive collision-free extension identifiers outside the frozen `IPEC.RULE.*` namespace:

| Theorem | Extension rule | Candidate violation outcome | Proof activation |
|---|---|---|---|
| T157 | `IPEC.EXT.GATE3.CLUSTER_B.RULE.T157` | `REJECTED_DLE_FAILURE` | WP4 pending |
| T158 | `IPEC.EXT.GATE3.CLUSTER_B.RULE.T158` | `REJECTED_LIVE_RESIDUAL` | WP4 pending |
| T159 | `IPEC.EXT.GATE3.CLUSTER_B.RULE.T159` | `REJECTED_GUARD_FAILURE` | WP4 pending |
| T160 | `IPEC.EXT.GATE3.CLUSTER_B.RULE.T160` | `REJECTED_NONELIM_OBSTRUCTION` | WP4 pending |
| T161 | `IPEC.EXT.GATE3.CLUSTER_B.RULE.T161` | `REJECTED_LIVE_RESIDUAL` | WP4 pending |
| T162 | `IPEC.EXT.GATE3.CLUSTER_B.RULE.T162` | `REJECTED_GUARD_FAILURE` | WP4 pending |

The extension registry is additive and versioned. It does not mutate V0-IPEC v0.1.

## 7. Exact WP2 case bindings

| WP2 case type | Exact theorem lineage | Exact role lineage |
|---|---|---|
| `DLE_TRANSITION` | T123, T132 | CB-R1 |
| `STRONG_DLE` | T157 | CB-R1, CB-R2 |
| `RESIDUAL_PERSISTENCE` | T158, T162 | CB-R3 |
| `RESIDUAL_TYPE_SEPARATION` | T159 | CB-R5 |
| `MODEL_PAIR_NONELIMINABILITY` | T159, T160 | CB-R5 |
| `MINIMAL_RESIDUAL_OBSTRUCTION` | T161 | CB-R4 |
| `HISTORICAL_TOKEN_NONCONVERSION` | T162 | CB-R3 |
| `ROBUST_OBSTRUCTION` | T124, T135 | CB-R6 |
| `BRANCH_LOCAL_FIREWALL` | T126, T136, T142 | CB-R7 |

The binder rejects any case-type, theorem-lineage, role-lineage, status, diagnostic, source-version, or evidence-hash mismatch.

## 8. Implementation products

The patch provides:

- versioned Python WP3 binder;
- IPEC compatibility profile;
- T157–T162 extension-rule registry;
- nine-case adapter-binding manifest;
- typed outcome, evidence-lineage, and diagnostic-transport schemas;
- 15 deterministic binding fixtures;
- deterministic builder and SHA-256 ledger;
- strict repository/preservation verifier;
- regression tests;
- dedicated hosted-CI workflow;
- safe applicator with `--check` and rollback.

## 9. Additive boundary with bounded successor-firewall handoff

WP3 adds only:

- `.github/workflows/gate3-cluster-b-wp3.yml`;
- `checker/v0_osap_fc1/cluster_b_wp3.py`;
- `docs/gate3/cluster_b/WP3_*`;
- `fixtures/gate3/cluster_b/wp3/`;
- `release/v1.4.0/GATE3_CLUSTER_B_WP3_*`;
- `schemas/v1.4.0/gate3_cluster_b_wp3_*`;
- `scripts/build_gate3_cluster_b_wp3.py`;
- `scripts/verify_gate3_cluster_b_wp3.py`;
- `tests/test_gate3_cluster_b_wp3.py`.

Three pre-existing successor-control paths receive exact-hash-guarded compatibility updates:

- `scripts/verify_gate3_cluster_b_wp2.py` receives a bounded WP3 path allowlist extension;
- `scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py` receives the exact 44-path WP3 successor delta;
- `release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt` records both resulting verifier hashes.

No other pre-existing path may be edited or deleted. Every WP0/WP1/WP2 canonical record and canonical ledger remains byte-preserved. All other baseline paths are replayed byte-exactly, and the applicator rolls back all three authorized replacements and all newly created paths on any failure.

## 10. Validation and rollback

`--check` uses a disposable detached worktree and runs:

```bash
python release/v1.4.0/tools/patch_wp2_post_merge_allowlist.py --check
python scripts/build_gate3_cluster_b_wp2.py --check
python scripts/build_gate3_cluster_b_wp2_post_merge_closeout.py --check
python scripts/verify_gate3_cluster_b_wp2.py
python scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py --package-only
python scripts/build_gate3_cluster_b_wp3.py --check
python scripts/verify_gate3_cluster_b_wp3.py
python -m pytest -q -p no:cacheprovider
python scripts/check_no_proof_holes.py
python scripts/verify_gate3_cluster_b_wp3.py
git diff --check
```

An explicit payload whitespace scan covers all added and authorized replacement files. Exact delta inventory and all-baseline-byte preservation checks run before and after regression. Hosted CI uses full history and additionally runs `git diff --check 7b49aa76fef65bced7141a639e8ef6fe3b5ba313...HEAD`.

For actual apply, every created path and all three authorized replacement backups are recorded. Any failure restores the exact original bytes and modes, removes only paths created by this patch, and requires a final clean-tree assertion.

## 11. Hosted CI and acceptance

The dedicated workflow runs the deterministic build check, WP3 verifier, full Python regression, proof-hole scan, second preservation verification, baseline-range whitespace check, and artifact upload. The implementation contains no commit, push, tag, Release, Zenodo, or DOI action.

## 12. Explicit prohibitions and nonclaims

WP3 authorizes no automatic commit or push, release tag, GitHub Release, Zenodo publication, DOI creation/authorization, frozen-record mutation, Lean/Coq proof completion, proof-term identity, kernel equivalence, checker completeness, unrestricted global soundness, empirical/physical/cosmological claim, or absolute-V0 claim.

## 13. Exit condition

WP3 is ready to apply only after the remote synchronization gate passes. It becomes implementation-complete only after local `--check`, actual application, author review, a dedicated PR, full hosted CI, and merge. Post-merge archival closeout is a separate successor artifact.

**Build specification: PROVIDED. Implementation patch: PROVIDED SEPARATELY. Release: NOT AUTHORIZED.**
