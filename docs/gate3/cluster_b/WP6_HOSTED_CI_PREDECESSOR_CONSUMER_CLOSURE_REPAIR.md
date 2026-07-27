# WP6 Hosted-CI Predecessor Consumer Closure Repair Corrective Patch v0.9

## Scope

This bounded corrective package supersedes v0.8 after read-only
post-application verification stopped before the exact seven-workflow matrix.
Package-only attestation passed, and every required package path was present
with the expected status. The failure occurred because the repository-surface
checker compared the complete porcelain status, including unrelated untracked
package, sidecar, audit, helper, and diagnostic artifacts, with the exact
13-path prepared repair surface.

The v0.8 WP3 control-flow correction remains unchanged. The successful
delegated frozen WP3 replay still terminates the current WP3 gate without
re-entering the frozen canonical builder.

## Read-only v0.8 residual

The isolated result was:

```text
PACKAGE_ONLY_INTERNAL_ATTESTATION=PASS
WORKING_TREE_REPOSITORY_SURFACE_ATTESTATION=FAIL
missing=[]
wrong=[]
extra=[unrelated untracked artifacts outside the 13-path package surface]
```

Repository identity, index, refs, worktree registry, branch, HEAD, and parent
remained unchanged. No staging, commit, push, or workflow rerun was performed.

## Root cause

The complete output of:

```text
git status --porcelain=v1 --untracked-files=all
```

contains both the prepared package surface and unrelated untracked operational
artifacts. v0.8 required equality between that complete map and the exact
13-path package map. This made harmless `??` entries outside the package
surface fail as `extra`, even though they did not alter any tracked repository
path and were intentionally preserved by the read-only process.

## Minimal v0.9 corrective delta

The v0.9 package retains the same exact 13-path package inventory. Its exact
v0.8-to-v0.9 delta is limited to the six additive repair-control paths:

1. this document;
2. the current manifest;
3. the current record;
4. the self-excluding SHA-256 ledger;
5. the current closure verifier;
6. the dedicated regression test.

The seven controlled modified paths are byte-identical to v0.8.

The working-tree verifier now:

1. requires the exact expected statuses for all 13 package paths;
2. permits unrelated entries outside that surface only when their status is
   exactly `??`;
3. rejects every unrelated tracked, staged, deleted, unmerged, renamed, mode,
   or structural change;
4. rejects missing or wrongly classified package paths;
5. preserves the full unrelated untracked inventory without moving or deleting
   it.

Dedicated regression coverage confirms:

- unrelated untracked artifacts outside the package surface are accepted;
- an unrelated tracked modification is rejected;
- a missing or wrongly classified package path is rejected.

## Preserved semantics

The exact seven-workflow predecessor-consumer matrix is unchanged. Frozen WP3
allowlists, frozen ledgers, historical records, schemas, fixtures, proof
sources, release evidence, and publication evidence remain unchanged. No
blanket successor allowlist expansion is introduced.

## Authorization boundary

The package contains seven controlled modified paths and six additive
repair-control paths. All ZIP entries use mode `0644`.

The package performs no extraction into a repository, staging, commit, amend,
reset, push, force-push, workflow rerun, PR creation, merge, synchronization,
tag, GitHub Release, Zenodo, DOI, Gate 3 closure, or v1.4.0 release action by
itself.
