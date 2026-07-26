# WP6 Post-Commit Regression Closure Repair

## Scope

This bounded repair closes the six regressions reproduced after ordinary commit
`33e292b6ae2e5f35135c9a8e35c9697901cae829`. It does not rewrite that commit, any historical ledger, any
archival record, or any release/publication artifact.

## Authorized surface

The repair has exactly twelve repository paths:

- six controlled modifications to the WP2, WP3, and WP6 successor consumers;
- six additive repair-control artifacts.

No workflow, proof source, frozen ledger, tag, release, Zenodo, DOI, pull-request,
or remote-reference mutation is included.

## Evidence-domain separation

The implementation separates three domains:

1. **Frozen historical evidence.** Existing ledgers retain their byte-exact
   contents and are interpreted at their frozen commit boundaries.
2. **Committed predecessor repair.** The prior 34-path repair is verified as the
   exact ordinary commit `33e292b6ae2e5f35135c9a8e35c9697901cae829`, whose exact parent is `ba32d8e855a79461fdcda14740acab86aafcb17a`.
3. **Current regression-closure repair.** Current bytes are accepted only when
   they match this repair's eleven-entry SHA-256 ledger and its exact 12-path
   working-tree or ordinary-child topology.

## HEAD topology

Prepared-uncommitted mode requires `HEAD == 33e292b6ae2e5f35135c9a8e35c9697901cae829`, six unstaged
controlled modifications, and six additive untracked files.

Committed mode requires one ordinary child whose exact parent is
`33e292b6ae2e5f35135c9a8e35c9697901cae829`, a clean working tree, and an exact `M`/`A` 12-path diff.

Amend, reset, history rewrite, synchronization, push, force-push, PR mutation,
GitHub Actions rerun, tag, GitHub Release, Zenodo, DOI, and Gate 3 closure remain
unauthorized.
