# V0 OSAP v1.3.0 RC1 Release Closure and Tag-Preparation Specification

**Artifact ID:** `V0_OSAP_V1_3_0_RC1_RELEASE_CLOSURE_TAG_PREPARATION`  
**Patch version:** `0.1`  
**Date:** `2026-07-13`  
**Repository:** `olegovation-ship-it/v0-osap-formal-core`  
**Target branch:** `v1.3.0-development`  
**RC1 audit PR:** `#12`  
**RC1 audit merge commit:** `29f9ec108efbb419fd030573b33ef5d30486d2ab`  
**Candidate theorem scope:** `T121-T156`  
**Candidate tag name:** `v1.3.0-rc1`  
**Patch state:** `RC1_CLOSURE_READY / CI_PENDING / TAG_NOT_CREATED`  
**Immutable historical release:** `v1.2.0` at `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3`  
**Immutable historical DOI:** `10.5281/zenodo.21306969`  
**Author:** Dmytro Panasenko, Independent Researcher

## 1. Decision

PR #12 completed the RC1 gate-audit freeze with ten successful GitHub Actions
checks and merged the frozen T121-T156 audit corpus into `main`. This patch moves
the program from audit freeze to release-closure preparation. It introduces no
new theorem, semantic rule, proof-assistant theorem, checker version, empirical
claim, release tag, GitHub Release, Zenodo version, or DOI.

## 2. Closure boundary

The closure boundary contains:

- the accepted audit merge commit `29f9ec108efbb419fd030573b33ef5d30486d2ab`;
- exactly thirty-six theorem records, T121 through T156;
- six source crosswalks and twelve negative release-gate mutants;
- checker development version `0.7.0.dev1`;
- the existing RC1 audit manifest, theorem inventory, parity evidence, claim
  classification matrix, and known-limitations record;
- a deterministic closure manifest, clean-room replay workflow, tag-preparation
  record, and draft annotated-tag message.

The historical tag `v1.2.0`, its target commit, and DOI remain immutable.

## 3. Tag-target policy

The string `v1.3.0-rc1` is reserved only. This patch does not create it.

The tag target is not the audit merge commit by default. The target must be the
exact merge commit of the release-closure PR, resolved only after:

1. the complete closure CI matrix is green;
2. the closure PR is reviewed and merged;
3. `main` and `v1.3.0-development` are synchronized;
4. the post-merge closure verifier passes on that exact commit;
5. a separate tag-authorization record writes the exact forty-character SHA.

Until all five conditions are met, `tag_target_commit` remains `null` and tag
creation is unauthorized.

## 4. Clean-room replay

The dedicated workflow checks out full history in a new GitHub Actions runner,
installs the declared Python dependencies, rebuilds both RC1 manifests, verifies
inventory and structural parity, executes all Python and phase verifiers, and
runs independent Lean 4 and Coq build jobs. It uploads environment and hash
evidence as a workflow artifact.

A successful workflow run is release evidence, not a release action.

## 5. Claim firewall

T140, T150, and T156 remain conditional under their recorded assumptions and
implementation invariants. Structural-record parity remains distinct from
proof-term identity and unrestricted semantic equivalence.

No checker-completeness, unconditional global checker-soundness, global
conservativity, physical V0, disappearance mechanism, cosmological, quantum-
gravity, multiverse, or empirical claim is made.

## 6. Release hold

This patch must leave all of the following false:

- RC1 tag created;
- final tag created;
- GitHub Release created;
- Zenodo version created;
- DOI changed;
- exact tag target authorized.

The next permissible state after a green, merged closure PR is
`RC1_TAG_AUTHORIZATION_READY`, not an automatic release.
