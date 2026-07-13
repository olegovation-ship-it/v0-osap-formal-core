
# V0 OSAP v1.3.0 RC1 Acceptance Gates

**Baseline:** `29201b4937cef220ef0933d852250b021f3f44d4`  
**Target branch:** `v1.3.0-development`  
**Theorem scope:** `T121-T156`  
**Current state:** `RC1_AUDIT_READY / CI_PENDING / NO_RELEASE_TAG`

| Gate | Requirement | Patch-stage state |
|---|---|---|
| RC1-G00 | Baseline Phase 6 closure commit is an ancestor | required at application |
| RC1-G01 | Candidate theorem inventory is exactly T121-T156 | generated and locally verified |
| RC1-G02 | One canonical owner per theorem ID | locally verified |
| RC1-G03 | Normative T121-T150 and extension T151-T156 are separated | locally verified |
| RC1-G04 | T140, T150, and T156 remain conditional | locally verified |
| RC1-G05 | Structural-record parity resolves Lean and Coq symbols | repository replay required |
| RC1-G06 | Fixture references resolve and canonical hashes replay | repository replay required |
| RC1-G07 | Twelve negative release-gate mutants are killed | locally verified |
| RC1-G08 | Full Python, schema, fixture, proof-hole, and Phase 1-6 matrix passes | CI pending |
| RC1-G09 | Lean 4 and Coq builds pass on the candidate commit | CI pending |
| RC1-G10 | Immutable `v1.2.0` and DOI remain unchanged | mandatory |
| RC1-G11 | No RC1/final tag or DOI is created by this patch | enforced |
| RC1-G12 | Clean-room replay completes | pending separate replay |
| RC1-G13 | Exact merged candidate commit is frozen by a separate closure decision | pending |

## Go/no-go rule

This patch may be merged only if RC1-G00 through RC1-G11 pass. It does not
authorize tagging. RC1-G12 and RC1-G13 are post-merge prerequisites for a
separate `v1.3.0-rc1` release decision.
