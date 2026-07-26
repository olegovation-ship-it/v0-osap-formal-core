# V0 OSAP v1.4.0 Gate 3 Cluster B WP6

## Post-Merge Push-Context Compatibility and Predecessor Workflow Isolation Repair

Version: 0.1
Status: PREPARED_UNCOMMITTED
Date: 2026-07-25

## Frozen identities

- Development baseline: `ba32d8e855a79461fdcda14740acab86aafcb17a`
- Canonical PR #33 merge commit: `47614ce7891f4895e003cb85e7651b7d043a963d`
- Branch: `v1.4.0-development`

## Root cause

The existing PR-#33-only job guard isolated the closeout pull request,
but did not isolate the successor push event on `refs/heads/main`.

The canonical merge topology, merge tree, Lean build and Coq build were
not damaged. The failures were caused by predecessor exact-baseline and
frozen-ledger controls executing in a successor post-merge context.

## Repair policy

Predecessor jobs are skipped only for:

1. an internal pull request from `v1.4.0-development` to `main`;
2. a push to `refs/heads/main`.

They remain active for:

- all other pull requests;
- pushes to all other refs;
- `workflow_dispatch`.

## Repair surface

- 14 predecessor workflows with exact job-level guard replacement;
- 1 successor WP6 post-merge workflow with main-push coverage;
- 2 legacy compatibility consumers updated to verify frozen evidence
  against hosted-CI repair commit `ba32d8e855a79461fdcda14740acab86aafcb17a` and recognize the
  successor guard;
- 6 historical WP2, WP5, WP6 and v1.3 compatibility consumers updated
  to accept only the exact SHA-256-attested successor repair surface;
- historical ledgers and frozen manifests remain byte-unchanged;
- 6 additive evidence and validation paths;
- 34 total changed paths.

## Historical replay and validation anchors

- WP5 historical replay anchor:
  `e5724fc394b2fbb26d8926b5670b8fd41a62a71c`
- WP6 canonical implementation-ledger anchor:
  `8a692859b2e02a8c9fccc008f76bb24218716f40`
- WP6 historical 54-path allowlist is replayed in a detached
  frozen worktree at `8a692859b2e02a8c9fccc008f76bb24218716f40`; it is never evaluated against
  the successor repair working tree.
- Repair-ledger anchor:
  `ba32d8e855a79461fdcda14740acab86aafcb17a`
- Local post-merge validation boundary:
  `origin/main=47614ce7891f4895e003cb85e7651b7d043a963d`,
  `origin/v1.4.0-development=ba32d8e855a79461fdcda14740acab86aafcb17a`,
  main ahead `2`, development ahead `0`,
  relation `FAST_FORWARD_ALLOWED`.
- Synchronization remains unperformed and unauthorized.

## Authorization firewall

No commit, push, synchronization, rerun, branch deletion, force-push,
history rewrite, tag, GitHub Release, Zenodo action, DOI action or
Gate 3 closure is authorized.
