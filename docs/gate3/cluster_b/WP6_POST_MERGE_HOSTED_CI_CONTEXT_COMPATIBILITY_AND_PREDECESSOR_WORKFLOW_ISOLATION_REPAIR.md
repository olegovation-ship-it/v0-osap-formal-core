# V0 OSAP v1.4.0 Gate 3 Cluster B WP6 Post-Merge Hosted-CI Context Compatibility and Predecessor Workflow Isolation Repair Patch v0.1

## Frozen identity

- repository: `olegovation-ship-it/v0-osap-formal-core`
- development branch: `v1.4.0-development`
- closeout PR: `#33`
- closeout commit: `79c531885f90fb9c0dbd9dd4a223d8fc9a5f74c9`
- closeout parent / accepted WP6 implementation head: `8a692859b2e02a8c9fccc008f76bb24218716f40`
- canonical WP6 merge commit on `main`: `f984b59cec832307bac7270c7d437a789bec99ce`

## Defect addressed

The original closeout allowlist accepted only the pre-commit worktree form in which all 30 closeout files were untracked. Hosted CI checks out a committed branch or GitHub synthetic merge ref, so that worktree is clean. The pre-commit-only assertion therefore failed in the dedicated closeout workflow and cascaded into the closeout verifier and dedicated tests.

Several frozen predecessor workflows also executed on PR #33 because their historical path filters overlap the new `WP6_POST_MERGE_*` surface. Those workflows enforce predecessor-specific exact baselines and are not authoritative for the WP6 post-merge closeout patch.

## Repair

1. Preserve the original 30-path additive closeout boundary by validating the frozen closeout commit `79c531885f90fb9c0dbd9dd4a223d8fc9a5f74c9` against `8a692859b2e02a8c9fccc008f76bb24218716f40` in committed CI contexts.
2. Retain the original untracked-file mode for clean-room pre-commit application replay.
3. Update the closeout workflow to invoke committed mode explicitly and add a repair verifier job.
4. Isolate predecessor workflows only for pull request `#33` by adding a job-level guard. Push, workflow-dispatch, and all other pull requests retain their original semantics.
5. Preserve the canonical WP6 implementation records, schemas, fixtures, proof sources, tags, and release firewall.

## Authorization firewall

This repair does not merge PR #33, synchronize branches, force-push, rewrite history, delete `v1.4.0-development`, close Gate 3, create a tag or GitHub Release, contact Zenodo, or perform a DOI/publication action.

## v0.1.1 recovery correction

The v0.1 applier correctly isolated predecessor jobs but its local post-application
verification remained strictly bound to the current digest of the frozen WP6
workflow file. v0.1.1 preserves the accepted predecessor blob and ledger at
`8a692859b2e02a8c9fccc008f76bb24218716f40`, while allowing only the explicitly
recorded PR-#33 job-guard overlays in the current repair worktree.

The recovery mode accepts the exact uncommitted v0.1 partial application and
does not require resetting or discarding it.
