# WP6 Hosted-CI Regression Corrective Repair v0.3

## Scope

This bounded successor repair supersedes package v0.2 after its isolated full-suite
clean-room verification reduced the original hosted-CI regression set to two
residual failures. The predecessor remains
`59fa5076fdabf74b832fb985947253eaaecca4ae`; no commit history is rewritten.

The v0.3 surface contains fourteen controlled modifications and six additive
repair-control artifacts. It retains the v0.2 WP2, WP3, WP6, replay, allowlist,
and legacy-consumer corrections and adds only the remaining WP5 post-merge
consumer. The already controlled WP6 full verifier receives a bounded boundary
correction for local clean-room clones.

## Residual failures closed

1. **WP5 post-merge effective-digest successor recognition.** The WP5 verifier
   now prefers the exact v0.3 layered SHA-256 attestation before falling back to
   the earlier frozen repair layer, then replays its historical builders and
   allowlists in the exact frozen WP5 worktree.
2. **WP6 full-verifier post-merge boundary recognition.** A local-path origin
   created solely by the authorized clean-room clone is verified by immutable
   commit identity, merge-base, and divergence rather than by the clone's
   potentially stale copied `origin/main` ref. Normal GitHub remotes retain the
   exact `origin/main` and `origin/v1.4.0-development` checks. Hosted Actions
   behavior remains unchanged.

## Evidence-domain separation

Frozen canonical and post-merge SHA-256 ledgers remain byte-exact. Historical
records, proof sources, schemas, fixtures, release/publication evidence, tags,
and commit history are excluded from this repair. Current bytes are accepted
only through the exact v0.3 prepared or committed surface and its SHA-256 ledger.

## Verification target

The package is designed for a fresh isolated replay of the complete Python suite
and the three previously failed hosted-CI jobs: full Python regression, replay
and claim perimeter, and decision/allowlist/release firewall. Package-only
integrity is verified outside the repository; full repository replay remains a
separately authorized local step.

## Authorization perimeter

Extraction, staging, commit, amend, push, force-push, workflow rerun, PR creation,
merge, synchronization, rebase, branch deletion, tag, GitHub Release, Zenodo,
DOI, Gate 3 closure, and v1.4.0 release authorization are not performed by this
package.
