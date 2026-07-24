# V0 OSAP v1.4.0 Gate 3 Cluster B WP6 Build Specification v0.1

**Repository:** `olegovation-ship-it/v0-osap-formal-core`
**Branch:** `v1.4.0-development`
**Required synchronized baseline:** `b3798367af960ff3b588778966c5e233d89e72ab`
**Date:** 2026-07-24
**Decision:** `WP6_BUILD_SPEC_APPROVED / IMPLEMENTATION_NOT_YET_APPLIED / GATE3_NOT_CLOSED`
**Release authorization:** `NONE`
**Gate 3 close authorization:** `NONE`

## 1. Purpose and architectural position

WP6 is the **Gate 3 Audit and Release-Candidate Decision** work package defined by the Gate 3 Cluster B baseline architecture. WP0-WP5 already supply the frozen baseline, theorem registry, executable semantics, Validator/IPEC bindings, dual-backend proofs, statement parity, CI integration, deterministic evidence manifests, post-merge lifecycle records, and synchronization-helper repair.

WP6 does not extend those implementation layers. It performs a read-only meta-audit over their canonical evidence and emits either:

- `ELIGIBLE_FOR_CLOSE_GATE3_PENDING_EXPLICIT_AUTHORIZATION`; or
- `HOLD_WITH_EXPLICIT_BLOCKERS`.

The positive result is only a decision candidate. It is not `CLOSE_GATE3`, does not authorize a tag or release, and requires a separate explicit user authorization and a separate closure action.

## 2. Verified predecessor baseline

The required repository identity is:

- `HEAD`: `b3798367af960ff3b588778966c5e233d89e72ab`;
- `origin/main`: `b3798367af960ff3b588778966c5e233d89e72ab`;
- `origin/v1.4.0-development`: `b3798367af960ff3b588778966c5e233d89e72ab`;
- main/development divergence: `0 0`;
- stable tag `v1.3.0` peeled target: `13bf095688bcabd5b090f188e9bd28a16237edeb`;
- working tree before application: clean.

The WP5 lifecycle chain locked by this specification is:

- implementation head `1c16ffb529b7e9a43c16739de26ad185c2f4b74c`;
- implementation merge `adda93cae34d6579e8b715d4107ff7f62a6f9c6b`;
- post-merge closeout head `dba0425c0f98950534bf5c6d407246da58eacd2f`;
- post-merge closeout merge `e5724fc394b2fbb26d8926b5670b8fd41a62a71c`;
- synchronization-helper repair head `14e761e7a34889eebc3c4ef7df17fc56c9267af9`;
- canonical repair merge `b3798367af960ff3b588778966c5e233d89e72ab`;
- hosted checks at the final WP5 repair state: `55 PASS`.

## 3. Predecessor-boundary and duplication audit result

The audit result is `PASS / WP6_SCOPE_IS_NON_DUPLICATIVE`.

WP6 must not regenerate or mutate:

- canonical WP0-WP5 records, schemas, fixtures, ledgers, or workflows;
- theorem identities `T157-T162` or the ten inherited Cluster B owners;
- semantic roles `CB-R1` through `CB-R7`;
- the accepted 16-node dependency DAG;
- WP2 executable semantics or semantic models;
- WP3 Validator/IPEC rules and typed bindings;
- WP4 Lean/Coq statements, proof sources, or parity hashes;
- WP5 canonical evidence manifests, replay records, post-merge ledgers, or repair successor ledger;
- the synchronization helper.

All WP6 implementation paths are additive and WP6-prefixed. No controlled predecessor replacement is planned.

## 4. WP6 objectives

1. Lock the exact synchronized baseline and stable-tag history.
2. Build a canonical WP0-WP5 evidence-input manifest with SHA-256 bindings.
3. Evaluate all 24 Gate 3 Cluster B acceptance obligations independently.
4. Recheck theorem identity closure, seven-role coverage, DAG acyclicity, fixture thresholds, typed lineage, proof completion, statement parity, and deterministic replay.
5. Produce a complete gate-result matrix and explicit blocker register.
6. Lock the claim perimeter and reject release or close-authorization injection.
7. Emit one of the two bounded decision candidates without closing Gate 3.
8. Preserve a deterministic WP6 evidence bundle and successor SHA-256 chain.

## 5. Theorem and formal target scope

WP6 introduces **no new numbered theorem** and no theorem ID `T163+`.

The inherited owners remain:

`T123, T124, T126, T132, T134, T135, T136, T139, T140, T142`.

The Cluster B extension targets remain:

`T157, T158, T159, T160, T161, T162`.

WP6 uses unnumbered meta-audit predicates only:

- `BaselineIdentityLocked`
- `PredecessorChainPreserved`
- `TheoremIdentityClosure`
- `SemanticRoleCoverageComplete`
- `DependencyDAGAcyclic`
- `FixtureCampaignSufficient`
- `TypedLineageComplete`
- `DualBackendCompletionPreserved`
- `StatementParityPreserved`
- `DeterministicReplayPreserved`
- `ClaimPerimeterLocked`
- `ReleaseFirewallIntact`
- `DecisionCandidateWellFormed`

These predicates classify evidence completeness; they do not alter object-level semantics or proof statements.

## 6. Schemas and evidence records

The implementation must add 14 WP6 schemas and the corresponding records for:

- baseline lock;
- acceptance gates;
- CI matrix;
- evidence-input manifest;
- audit fixtures and fixture manifest;
- gate-result matrix;
- blocker register;
- decision candidate;
- claim perimeter;
- preservation firewall;
- replay record;
- schema-bundle manifest;
- build plan.

Every record must use deterministic sorted UTF-8 JSON serialization and be bound into `GATE3_CLUSTER_B_WP6_SHA256SUMS.txt`.

## 7. Audit fixture campaign

WP6 adds 14 audit-control fixtures, not semantic models:

1. all gates pass and a close-eligible candidate is produced;
2. branch/ref mismatch;
3. predecessor digest mismatch;
4. missing WP5 repair ledger;
5. theorem-ID closure failure;
6. semantic-role coverage failure;
7. dependency cycle;
8. positive-model threshold failure;
9. negative/boundary threshold failure;
10. typed-lineage gap;
11. backend completion or statement-parity failure;
12. replay nondeterminism;
13. claim-perimeter expansion;
14. release or Gate 3 close-authorization injection.

Fixtures 2-13 must yield `HOLD_WITH_EXPLICIT_BLOCKERS`. Fixture 14 must be rejected as malformed/unauthorized rather than converted into a valid decision.

## 8. Scripts and tests

The implementation surface is limited to:

- deterministic builder;
- audit-evidence capture tool;
- two-run replay tool;
- full verifier with bounded job selectors;
- build-spec verifier;
- one implementation regression module;
- one build-spec regression module.

No script may commit, push, merge, create or move a tag, create a GitHub Release, contact Zenodo, mutate a DOI, publish an artifact, delete a branch, rewrite history, execute the synchronization helper, or issue a canonical Gate 3 decision.

## 9. CI design

A dedicated read-only WP6 workflow contains 10 jobs:

1. **Exact baseline, branch, refs, tag, and clean-state lock** — `python scripts/verify_gate3_cluster_b_wp6.py --job baseline-lock`
2. **WP0-WP5 predecessor records and SHA-256 successor-chain preservation** — `python scripts/verify_gate3_cluster_b_wp6.py --job predecessor-chain`
3. **Theorem identity, seven-role coverage, and dependency DAG** — `python scripts/verify_gate3_cluster_b_wp6.py --job theorem-role-dag`
4. **WP2 model thresholds and admissible model-pair evidence** — `python scripts/verify_gate3_cluster_b_wp6.py --job semantic-evidence`
5. **WP3 typed outcomes and theorem/IPEC lineage** — `python scripts/verify_gate3_cluster_b_wp6.py --job typed-lineage`
6. **WP6 schemas, audit fixtures, verifier, and Python regression** — `python -m pytest -q -p no:cacheprovider`
7. **Lean build and proof-hole firewall** — `python scripts/verify_gate3_cluster_b_wp6.py --job lean-proof-holes`
8. **Coq build and statement-parity preservation** — `python scripts/verify_gate3_cluster_b_wp6.py --job coq-parity`
9. **Deterministic replay and claim-perimeter lock** — `python scripts/verify_gate3_cluster_b_wp6.py --job replay-claims`
10. **Blocker register, decision candidate, exact allowlist, and release firewall** — `python scripts/verify_gate3_cluster_b_wp6.py --job decision-firewall`

The workflow uploads audit evidence only. It does not perform repository writes or publication actions.

## 10. Acceptance gates

All 24 gates are mandatory:

1. exact branch, HEAD, and both remote refs equal `b3798367af960ff3b588778966c5e233d89e72ab`;
2. stable `v1.3.0` tag target and historical DOI evidence are unchanged;
3. WP0-WP4 canonical records and historical ledgers are byte-preserved;
4. WP5 canonical records and canonical ledger are byte-preserved;
5. WP5 post-merge and repair successor chains reproduce exactly;
6. inherited theorem owners and `T157-T162` are identity-locked;
7. `CB-R1`-`CB-R7` remain complete;
8. the 16-node dependency graph is acyclic with no undeclared imports;
9. the WP2 positive-model count remains at least 12;
10. the WP2 negative/boundary count remains at least 12 and the combined threshold is preserved;
11. admissible model-pair evidence is present and internally coherent;
12. all nine WP3 case types retain exact typed bindings;
13. every nonprocedural outcome retains theorem and IPEC lineage;
14. `T157-T162` remain complete in Lean and Coq;
15. statement parity remains 100 percent and statement hashes are locked;
16. proof-hole scan returns PASS;
17. full Python regression returns PASS;
18. schemas and deterministic fixtures return PASS;
19. Lean build returns PASS;
20. Coq build returns PASS;
21. WP5 evidence manifest, ledgers, and two-run replay reproduce;
22. all 14 WP6 audit fixtures produce the required bounded outcomes;
23. claim perimeter, exact allowlist, rollback, SHA-256 chain, and release firewall pass;
24. the result is only a bounded decision candidate; automatic `CLOSE_GATE3` is prohibited.

Any failed mandatory gate creates a blocker and forces `HOLD_WITH_EXPLICIT_BLOCKERS`.

## 11. Exact changed-path boundary

The Build Specification package adds exactly 6 paths. The subsequent Implementation Patch is limited to exactly 54 additive WP6 paths recorded in `GATE3_CLUSTER_B_WP6_BUILD_PLAN.json`.

Forbidden path families include `checker/`, `lean/`, `coq/`, all WP0-WP5 canonical prefixes, non-WP6 semantic fixtures, and every existing predecessor workflow.

## 12. Validation protocol

The Build Specification applicator must:

1. verify package SHA-256 integrity;
2. require the exact branch/ref/HEAD baseline and clean worktree;
3. validate the six-path package in a detached disposable worktree;
4. replay WP5 canonical, post-merge, and synchronization-repair verifiers;
5. run the full Python regression, proof-hole scan, Lean build, Coq build, schema validation, and `git diff --check`;
6. install the six additive build-spec paths only after disposable validation passes;
7. rollback all six paths on any failure;
8. leave the successful delta uncommitted.

## 13. Authorization boundary

This Build Specification authorizes preparation and local validation of a separate WP6 Implementation Patch only after review of this specification. It does not authorize:

- commit, push, merge, force-push, or history rewrite;
- branch deletion;
- tag creation or movement;
- GitHub Release;
- Zenodo deposit;
- DOI creation or mutation;
- publication;
- a canonical `CLOSE_GATE3` decision.

## 14. Build decision

`PREDECESSOR_BOUNDARY_PASS / DUPLICATION_AUDIT_PASS / WP6_BUILD_SPEC_APPROVED / IMPLEMENTATION_NOT_APPLIED / GATE3_NOT_CLOSED / RELEASE_NOT_AUTHORIZED`
