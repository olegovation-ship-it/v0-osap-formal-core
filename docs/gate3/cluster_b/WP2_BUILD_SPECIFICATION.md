# V0 OSAP v1.4.0 Gate 3 Cluster B WP2 Build Specification v0.1.3

**Work package:** WP2 — Executable Transition, Residual, and Model-Pair Semantics
**Repository:** `olegovation-ship-it/v0-osap-formal-core`
**Target branch:** `v1.4.0-development`
**Exact WP2 start commit:** `ffeaa3fd4fb2f85679f4695d5b28e333004ca24a`
**Canonical WP1 merge baseline:** `eaf142089230ea5a5096ae834bf4e733d5f369aa`
**Frozen v1.3.0 tag target:** `13bf095688bcabd5b090f188e9bd28a16237edeb`
**Date:** 2026-07-21
**Decision:** `APPROVED_FOR_BOUNDED_IMPLEMENTATION`
**Release authorization:** `NONE`

## 1. Purpose

WP2 implements deterministic finite-record runtime semantics and fixtures for the contracts locked by WP1. It converts the WP1 statement/ownership layer into an executable, testable semantics surface without changing theorem ownership, theorem statements, the dependency DAG, formal proof status, Validator/IPEC bindings, or any release object.

WP2 is not a proof package. It is not an IPEC/Validator integration package. It is not a release-candidate package.

## 2. Inherited immutable contracts

The following WP1 contracts are consumed exactly as locked:

| Contract | Owner | WP2 executable obligation |
|---|---:|---|
| `CB-CONTRACT-STRONG-DLE` | T157 | Require historical live witness, current no-live/no-license status, and typed deterministic DLE transition provenance. |
| `CB-CONTRACT-RESIDUAL-PERSISTENCE` | T158 | Preserve a live residual only under deterministic certified non-interference with identity and type preserved. |
| `CB-CONTRACT-RESIDUAL-TYPE-SEPARATION` | T159 | Reject interchangeability between distinct residual classes absent an explicit admissible translation. |
| `CB-CONTRACT-MODEL-PAIR` | T160 | Accept a bounded non-eliminability witness only for admissible, non-circular, non-label-distinct model pairs agreeing on a declared shared fragment and differing on a typed live residual. |
| `CB-CONTRACT-MINIMAL-OBSTRUCTION` | T161 | Treat one declared live residual as a sufficient raw-relative obstruction witness without converse or completeness. |
| `CB-CONTRACT-HISTORICAL-NONCONVERSION` | T162 | Prevent archive/history tokens from becoming current live guard tokens without a separate typed fresh activation creating a new token identity. |

The exact seven residual types remain:

`TARGET_PRESENCE`, `HISTORICAL`, `MEMORY`, `SIGNAL`, `CAUSAL`, `INFORMATION`, `GENERIC_TRACE`.

## 3. Seven-role runtime coverage

WP2 must supply executable fixture coverage for all seven WP1 semantic roles:

1. `CB-R1 DLE_TRANSITION` — inherited T123/T132 transition discipline.
2. `CB-R2 STRONG_DLE` — T157.
3. `CB-R3 LIVE_RESIDUAL_PERSISTENCE` — T158/T162 with inherited T124/T139.
4. `CB-R4 RAW_RESIDUAL_OBSTRUCTION` — T161 with inherited T134.
5. `CB-R5 MODEL_PAIR_NONELIMINABILITY` — T159/T160 with inherited T140/T142.
6. `CB-R6 ROBUST_OBSTRUCTION` — inherited T124/T135.
7. `CB-R7 BRANCH_LOCAL_FIREWALL` — inherited T126/T136/T142.

Runtime fixture coverage does not create new theorem ownership for inherited-only roles.

## 4. Executable semantics surface

WP2 adds the pure Python module:

`checker/v0_osap_fc1/cluster_b_wp2.py`

The module exposes nine bounded evaluators:

- `evaluate_dle_transition`;
- `evaluate_strong_dle`;
- `evaluate_residual_persistence`;
- `evaluate_residual_type_separation`;
- `evaluate_model_pair_noneliminability`;
- `evaluate_minimal_residual_obstruction`;
- `evaluate_historical_token_nonconversion`;
- `evaluate_robust_obstruction`;
- `evaluate_branch_local_firewall`.

Each evaluator returns a deterministic record containing status, typed diagnostics, theorem and semantic-role references, derived values, and explicit nonclaims. The implementation identifier is `v0-osap-cluster-b-wp2/0.1.0.dev1`; the archived FC-1 checker version remains unchanged.

## 5. Outcome discipline

Runtime outcomes use the existing three-state envelope:

- `PASS` — the bounded input is valid and no reject/deferred condition is present;
- `DEFERRED` — a conditional theorem premise or evidence obligation is absent, so no positive conclusion is certified;
- `REJECT` — a locked firewall or contract condition is violated.

Diagnostics are deterministic and ordered by fixture evaluation. WP2 does not claim diagnostic completeness beyond the bounded fixture/evaluator surface.

## 6. Fixture matrix

WP2 supplies 28 deterministic JSON fixtures covering:

- positive and negative DLE transition cases;
- all three StrongDLE components;
- residual persistence, identity change, interference, and missing-certificate cases;
- residual type separation and admissible translation discharge;
- admissible model-pair witness, label-only failure, shared-fragment mismatch, and missing residual difference;
- minimal raw-residual obstruction and no-witness cases;
- historical nonconversion, forbidden archive export, valid fresh activation, and unwitnessed activation;
- robust obstruction positive/negative cases;
- branch-local firewall positive, absolute-promotion rejection, and label-only rejection cases.

The fixture matrix must cover all nine evaluators, all seven roles, and T157–T162.

## 7. Repository boundary

The WP2 executable core adds new files under:

- `.github/workflows/gate3-cluster-b-wp2.yml`;
- `checker/v0_osap_fc1/cluster_b_wp2.py`;
- `docs/gate3/cluster_b/WP2_*`;
- `fixtures/gate3/cluster_b/wp2/`;
- `release/v1.4.0/GATE3_CLUSTER_B_WP2_*`;
- `schemas/v1.4.0/gate3_cluster_b_wp2_*`;
- `scripts/build_gate3_cluster_b_wp2.py`;
- `scripts/verify_gate3_cluster_b_wp2.py`;
- `tests/test_gate3_cluster_b_wp2.py`.

All WP0/WP1 canonical records, post-merge closeout records, historical SHA ledgers, inherited verifiers/tests, proof modules, package metadata, release notes, and citation files remain immutable. Hosted-CI successor compatibility may modify only the four inherited workflow control files explicitly listed in the WP2 baseline lock; no other pre-existing path may be modified or deleted.

## 8. Deterministic build products

The builder generates and checks:

- `GATE3_CLUSTER_B_WP2_BASELINE_LOCK.json`;
- `GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json`;
- `GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json`;
- `GATE3_CLUSTER_B_WP2_ACCEPTANCE_GATES.json`;
- `GATE3_CLUSTER_B_WP2_SCHEMA_BUNDLE_MANIFEST.json`;
- `GATE3_CLUSTER_B_WP2_SHA256SUMS.txt`.

The SHA ledger covers every WP2 code, fixture, schema, document, workflow, test, and generated JSON record except the ledger itself.

## 9. Verification sequence

From the exact clean-room baseline:

```bash
python scripts/build_gate3_cluster_b_wp2.py --check
python scripts/verify_gate3_cluster_b_wp0.py --package-only
python scripts/verify_gate3_cluster_b_wp0_post_merge_closeout.py --package-only
python scripts/verify_gate3_cluster_b_wp1.py --package-only
python scripts/verify_gate3_cluster_b_wp1_post_merge_closeout.py --package-only
python scripts/verify_gate3_cluster_b_wp2.py
python -m pytest -q -p no:cacheprovider
python scripts/check_no_proof_holes.py
cd lean && lake build
cd ../coq && make
cd ..
git diff --check ffeaa3fd4fb2f85679f4695d5b28e333004ca24a --
```

The inherited verifiers run in package-only mode because WP2 introduces a separate allowlist owned by the WP2 verifier; no inherited verifier is modified.

## 10. Acceptance gates

WP2 has 20 acceptance gates. The local package may be marked `PASS` only when:

- the exact baseline and frozen tag target are recorded;
- no canonical WP0/WP1 record, ledger, verifier, test, theorem contract, proof module, package metadata, or release/citation artifact is modified; only four inherited workflow controls receive bounded successor replay;
- all nine evaluators are present;
- all seven roles and T157–T162 have deterministic fixtures;
- schemas and SHA ledger reproduce;
- fixture expectations replay exactly;
- proof, IPEC, and release boundaries remain explicit.

Hosted CI remains `NOT_RUN` until the overlay is applied, committed, pushed, and tested in the repository workflow.

## 11. Deferred work

- **WP3:** versioned Validator Core / IPEC extension bindings, typed rule outcomes, and diagnostic transport.
- **WP4:** Lean and Coq statement-parity modules and proof completion for T157–T162.
- **WP5:** complete deterministic evidence replay across WP0–WP4.
- **WP6:** Gate 3 audit and release-candidate decision.

## 12. Release firewall

WP2 does not authorize or perform:

- a Git tag;
- a GitHub Release;
- Zenodo publication or metadata mutation;
- DOI creation or mutation;
- stable release rebuild;
- movement of `v1.3.0`;
- proof completion;
- Validator/IPEC binding publication.

**Build specification: APPROVED. Implementation patch: PROVIDED SEPARATELY. Release: NOT AUTHORIZED.**

## Full-regression compatibility correction v0.1.1

The initial new-file-only overlay exposed an inherited test-harness mismatch:
`test_wp0_full_git_firewall_accepts_current_patch` evaluated the exact WP0
path firewall against the successor WP2 working tree. WP2 runtime semantics,
fixtures, schemas, and ledgers were unaffected.

The correction is bounded to the legacy test/control plane:

- the legacy WP0 full-git-firewall test delegates to the WP2 successor
  repository-boundary verifier when the WP2 baseline lock is present;
- the dedicated WP2 workflow replays closed WP0/WP1 package verifiers in a
  detached worktree at exact baseline `ffeaa3fd4fb2f85679f4695d5b28e333004ca24a`;
- the only permitted pre-existing-path modification is
  `tests/test_gate3_cluster_b_wp0.py`;
- no WP0/WP1 release record, historical SHA ledger, theorem contract,
  production checker module, tag, GitHub Release, Zenodo record, or DOI is
  changed or authorized.

## Historical-ledger and full-suite correction v0.1.2

The v0.1.1 compatibility approach modified
`tests/test_gate3_cluster_b_wp0.py`, whose exact bytes are intentionally
attested by the closed WP0/WP1 successor-ledger chain. That approach is
withdrawn.

v0.1.2 restores the historical test file byte-for-byte from exact WP2 start
`ffeaa3fd4fb2f85679f4695d5b28e333004ca24a` and moves successor dispatch to the new WP2-owned
`tests/conftest.py` surface:

- the exact WP0 delta-firewall test is skipped only in a WP2 successor tree;
- the dedicated workflow replays the unmodified historical WP0/WP1 suite in a
  detached worktree at the exact frozen baseline;
- the current repository delta is checked by the WP2 verifier and a dedicated
  WP2 successor-firewall regression test;
- no pre-existing baseline file, WP0/WP1 release record, historical SHA ledger,
  theorem contract, tag, GitHub Release, Zenodo record, or DOI is modified.

## Hosted-CI successor compatibility correction v0.1.3

Draft PR #23 established that the dedicated WP2 workflow, Lean 4, Coq, schema
validation, release readiness, and inherited v1.3.0 lifecycle checks pass.
The remaining failures arose because exact-stage WP0/WP1 workflows evaluated
their historical path firewalls against the later WP2 successor merge tree,
while the generic Python workflow used a shallow checkout that omitted exact
baseline `ffeaa3fd4fb2f85679f4695d5b28e333004ca24a`.

The v0.1.3 correction is limited to the CI/test control plane:

- four inherited GitHub Actions workflows replay their exact closed stage in
  detached worktrees when a pull request contains the WP2 baseline lock;
- the generic shallow Python checkout skips only the history-dependent
  historical-byte assertion when the exact baseline object is unavailable;
- the dedicated WP2 workflow retains `fetch-depth: 0` and therefore still
  executes the historical-byte assertion and inherited baseline replay;
- the WP2 verifier authorizes exactly the four workflow modifications and
  continues to reject every other modified pre-existing path;
- the WP2 SHA-256 ledger attests the four compatibility workflows;
- no WP0/WP1 canonical record, historical ledger, verifier, test, theorem
  contract, proof module, tag, GitHub Release, Zenodo record, or DOI is changed
  or authorized.
