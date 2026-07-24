# WP5 Development Synchronization Helper Generalization and Replay Repair

## Identity

- Repository: `olegovation-ship-it/v0-osap-formal-core`
- Required branch: `v1.4.0-development`
- Frozen repair baseline: `e5724fc394b2fbb26d8926b5670b8fd41a62a71c`
- Stable tag preserved: `v1.3.0` → `13bf095688bcabd5b090f188e9bd28a16237edeb`

## Defect and repair

The original helper admitted only `1 0` and `0 0`. After the implementation
and closeout merge commits, the valid fast-forward relation was `2 0`, so the
helper failed safely with return code `1`.

The repaired classifier accepts `0 0` as a no-op and every `N 0` with `N > 0`
as a candidate fast-forward. It rejects `0 N` and all `M N` relations where
development is ahead. Every candidate fast-forward must additionally pass
`git merge-base --is-ancestor`, and the only merge mode is `git merge --ff-only`.

## Replay surface

Five fixtures cover `0 0`, `1 0`, `2 0`, `0 1`, and `1 1`. Unit tests also
exercise larger safe `N 0` values.

## Preservation boundary

The patch changes exactly 27 paths: five controlled successor replacements
and twenty-two additive repair artifacts. The canonical WP5 and post-merge
ledgers remain frozen; a new repair successor ledger overlays the five
controlled replacements.

The package applicator performs no commit, push, merge, release, publication,
DOI action, WP6 start, or Gate 3 decision. It does not invoke the operational
synchronization helper.
