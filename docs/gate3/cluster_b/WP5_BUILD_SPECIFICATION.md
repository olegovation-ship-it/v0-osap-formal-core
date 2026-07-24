# V0 OSAP v1.4.0 Gate 3 Cluster B WP5 Build Specification v0.1

**Repository:** `olegovation-ship-it/v0-osap-formal-core`
**Branch:** `v1.4.0-development`
**Required synchronized baseline:** `7b497f197652874164e00fe9c0ef7f67e760c979`
**Date:** 2026-07-23
**Decision:** `WP5_BUILD_SPEC_APPROVED / IMPLEMENTATION_NOT_YET_APPLIED`
**Release authorization:** `NONE`

## 1. Scope

WP5 is the **CI Integration and Deterministic Evidence Manifests** work package defined by the Gate 3 Cluster B baseline audit. It integrates the already accepted WP0-WP4 evidence stack. It does not add runtime semantics, change theorem statements, add theorem IDs, modify Lean or Coq proofs, or make the WP6 Gate 3 closure decision.

## 2. Theorem scope

WP5 has **no new theorem targets**. It freezes and integrates:

- inherited Cluster B owners: `T123, T124, T126, T132, T134, T135, T136, T139, T140, T142`;
- extension targets completed in WP4: `T157-T162`;
- seven semantic roles: `CB-R1` through `CB-R7`;
- the accepted 16-node acyclic dependency graph.

T140 remains conditional. WP5 makes no change to the conditional status of T150 or T156 outside this cluster.

## 3. Exact WP5 deliverables

1. A 14-job, read-only GitHub Actions matrix: baseline, schemas, ID audit, role coverage, dependency DAG, Python semantics, positive models, negative/boundary models, Lean, Coq, statement parity, IPEC lineage, deterministic replay, and WP6 audit-input readiness.
2. A canonical evidence-input manifest that binds predecessor evidence paths to SHA-256 values derived from the exact synchronized baseline commit.
3. Six evidence-control fixtures. These test ordering, uniqueness, SHA-256 integrity, predecessor-chain integrity, and the release-action firewall. They do not add semantic models.
4. A two-run canonical serialization replay with byte-identical output.
5. A WP5 preservation firewall, schema bundle, SHA-256 ledger, deterministic builder, replay tool, verifier, tests, and exact-path allowlist.

## 4. Frozen predecessor boundary

All canonical WP0-WP4 records, post-merge records, frozen-upstream records, schemas, fixtures, ledgers, theorem identities, and Lean/Coq sources are immutable. The implementation is additive under WP5-specific prefixes only. Predecessor verifiers are replayed in a disposable worktree at `7b497f197652874164e00fe9c0ef7f67e760c979` rather than rewritten for successor tolerance.

## 5. Fixtures

WP5 adds six evidence-control fixtures:

- valid canonical evidence;
- unordered paths rejected;
- duplicate path rejected;
- SHA-256 mismatch rejected;
- predecessor baseline mutation rejected;
- release authorization rejected.

The WP2 semantic campaign remains the operative model library. WP5 requires at least 12 PASS models and at least 12 REJECT/DEFERRED boundary models without regenerating them.

## 6. Acceptance gates

All 24 WP5 gates are mandatory. The local application gate includes:

- exact branch/ref equality and clean baseline;
- predecessor byte preservation and SHA-256-chain replay;
- Draft 2020-12 schema validation;
- deterministic fixture replay;
- full Python regression;
- proof-hole scan;
- Lean 4 build;
- Coq build;
- two-run byte-identical evidence replay;
- exact changed-path allowlist;
- `git diff --check`.

Successful WP5 validation yields `READY_FOR_WP6_AUDIT`. It does not yield `CLOSE_GATE3`.

## 7. Prohibitions

The package performs no commit, push, merge, force-push, history rewrite, branch deletion, tag, GitHub Release, Zenodo deposit, DOI action, or WP6 decision. It does not edit `v1.4.0-development` remotely.
