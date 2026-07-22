# V0 OSAP v1.4.0 Gate 3 Cluster B WP2 — Post-Merge Archival Closeout and Development-Branch Synchronization

## Identity

- Repository: `olegovation-ship-it/v0-osap-formal-core`
- Merged pull request: `#23`
- Accepted WP2 head: `b0f5fc5b0d5103e1bb22b06ca51716d40e22a5d7`
- Merge commit: `b6370af53add3fdff1ddb48824dd76ebba3aaa32`
- Merge time: `2026-07-22T15:42:03Z`
- Development branch: `v1.4.0-development`
- Main branch: `main`

## Closeout result

WP2 executable semantics are merged and accepted. The merged surface preserves:

- 9 deterministic semantic case types;
- 28 positive, negative, and deferred fixtures;
- semantic-role coverage `CB-R1` through `CB-R7`;
- theorem-target coverage `T157` through `T162`;
- 20/20 WP2 acceptance gates;
- 25/25 hosted checks;
- detached Python replay: 106 passed, 6 intentionally skipped, 0 failed.

## Archival boundary

This closeout does not add proof implementation, Validator/IPEC bindings, new runtime semantics,
a release tag, a GitHub Release, a Zenodo publication, or DOI authorization.

The canonical WP2 SHA-256 ledger remains historical and is not rewritten. A separate successor ledger
attests only the bounded post-merge control changes and new closeout records.

## Branch synchronization

At capture, `main` and `v1.4.0-development` both pointed to `b6370af53add3fdff1ddb48824dd76ebba3aaa32`. The closeout patch is applied on
`v1.4.0-development`, reviewed through a dedicated pull request, merged using a merge commit, and then
the development branch is synchronized to `main` by fast-forward only.

Force-push, history rewrite, and deletion of `v1.4.0-development` are not authorized.

## Next work package

WP3 begins only after this closeout pull request is merged and both branches are identical again.
WP3 requires a separate build specification and implementation patch.
