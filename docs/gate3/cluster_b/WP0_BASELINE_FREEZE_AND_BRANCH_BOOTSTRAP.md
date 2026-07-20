# Gate 3 Cluster B WP0 - Baseline Freeze and Branch Bootstrap

**Program:** V0 OSAP Formal Core
**Target:** v1.4.0 development
**Branch:** `v1.4.0-development`
**Exact branch parent:** `a13a96fda4964dde1719c7d014f11878e1103b20`
**Date:** 2026-07-20
**State:** `BUILD_READY / BRANCH_APPLICATION_PENDING / HOSTED_CI_PENDING`

## Purpose

WP0 freezes every upstream identity required by Gate 3 Cluster B and authorizes a new development branch rooted exactly at the post-v1.3.0 archival `main` baseline. It does not implement T157-T162 and does not alter any frozen release.

## Frozen identities

- OSAP v1.3.0: `v1.3.0` -> `13bf095688bcabd5b090f188e9bd28a16237edeb`, DOI `10.5281/zenodo.21346728`.
- OSAP branch source: `main` -> `a13a96fda4964dde1719c7d014f11878e1103b20`.
- V0-IPEC v0.1: `5474a2c6a3e1c274d17f674889d427c1c91572f7`, Gate 2 closed.
- Validator Core v0.12: `v0.12-compiler-passed-freeze` -> `3540f47198140ca0a3612f247cfe356fa7fba2cb`, DOI `10.5281/zenodo.21285577`.
- Paper B: `SCICO-D-26-00508`, submitted 2026-07-19.
- Submission register v121 package SHA-256: `9e75d4c27a6151195486641d3d1074aaab494e2b1a50f293d5a710be58903eaf`.

## Repository mutation boundary

WP0 adds only new Gate 3 governance, schema, verifier, test, and workflow files. It must not modify `release/v1.3.0`, checker implementation, proof backends, fixtures, or v1.1 schemas. The provisional range T157-T162 remains non-canonical until WP1.

## Exit condition

WP0 exits only after:

1. the branch is created from the exact source commit;
2. local verifier and regression test pass;
3. hosted GitHub Actions passes;
4. the PR evidence records no frozen-upstream or release mutation.

No tag, GitHub Release, Zenodo publication, DOI action, or release authorization is part of WP0.
