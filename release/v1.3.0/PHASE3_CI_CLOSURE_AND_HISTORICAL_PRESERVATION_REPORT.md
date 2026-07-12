# Phase 3 CI Closure and Historical-Preservation Report

Status: `ACCEPTED / CI_PASS / MERGED / HISTORICALLY_PRESERVED`
Date: 2026-07-12
Theorem range: `T133-T138`
Pull request: `#4`
Development branch: `v1.3.0-development`
Head commit: `2172591ed8a5ab3c1fa31f2a3a6575536f161fe4`
Merge commit: `c02b05f667b82aa31ac8865c31219b94b1fc74d2`
Merged at: `2026-07-11T21:56:58Z`
Immutable baseline: `v1.2.0`
Baseline DOI: `10.5281/zenodo.21306969`

## Closure result

The Phase 3 firewall-expansion patch passed the complete pull-request validation matrix and was merged into `main` through PR #4.

- Pull-request checks: 8/8 PASS.
- Python regression suite: 112 tests PASS.
- Schema validation: PASS.
- Deterministic fixture replay: PASS.
- Proof-hole scan: PASS.
- Phase 1 preservation verifier: PASS.
- Phase 2 expansion verifier: PASS.
- Phase 2 CI-closure verifier: PASS.
- Phase 3 statement-hash and backend-symbol verifier: PASS.
- Lean 4 build: PASS.
- Coq build: PASS.
- Release readiness: PASS.

The accepted scope is the finite FC-1 theorem cluster T133-T138: fresh-token reactivation, raw residual obstruction, robust non-eliminable residual obstruction, relative-to-absolute non-promotion, approximation non-identity, and the terminal same-state self-certification limit.

## GitHub evidence

PR #4 merged two commits into `main`, changing 50 files with 1848 additions and 20 deletions. The merge commit is `c02b05f667b82aa31ac8865c31219b94b1fc74d2`.

The successful workflow families were Schema validation, Python checker, Lean 4, Coq, and Release readiness. Release readiness preserved both jobs: the immutable `v1.2.0` baseline audit and the v1.3.0 development audit.

The branch comparison after merge reported `main` and `v1.3.0-development` as identical at the Phase 3 merge commit.

## Historical-preservation audit

The closure audit confirms:

1. The tag `v1.2.0` remains immutable and is not moved or retagged.
2. DOI `10.5281/zenodo.21306969` remains bound to the archived v1.2.0 software record.
3. The immutable-baseline readiness job retains `verify_manifest.py` and `verify_closure.py`.
4. Phase 1 and Phase 2 accepted closure records remain preserved.
5. The development branch and `main` were synchronized to the PR #4 merge commit after merge.
6. No new release tag, GitHub Release, or Zenodo version is created by this patch.

## Metadata and integrity repairs

The post-merge closure patch removes stale Phase 3 `BUILD_READY / CI_PENDING` labels, advances the theorem crosswalk to accepted parity status, updates the theorem register, and advances the explicit development non-claim boundary to T138. The immutable v1.2.0 release claim remains bounded to T121-T126.

A dedicated static verifier checks the closure evidence, PR and merge identifiers, accepted statuses, release-readiness preservation, DOI boundary, branch synchronization, and absence of stale Phase 3 pending labels.

## Boundary

This report closes Phase 3 only. It is not a v1.3.0 release record, does not move or retag `v1.2.0`, does not create a new DOI, and does not claim complete T121-T150 mechanization, checker completeness, proof-term identity or semantic equivalence among Python, Lean 4, and Coq, or empirical and physical truth of V0.
