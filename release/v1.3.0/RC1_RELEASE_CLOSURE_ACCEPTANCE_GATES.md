# V0 OSAP v1.3.0 RC1 Release-Closure Acceptance Gates

**Audit merge baseline:** `29f9ec108efbb419fd030573b33ef5d30486d2ab`  
**Target branch:** `v1.3.0-development`  
**Theorem scope:** `T121-T156`  
**Candidate tag:** `v1.3.0-rc1`  
**Current state:** `RC1_CLOSURE_READY / CI_PENDING / TAG_NOT_CREATED`

| Gate | Requirement | Patch-stage state |
|---|---|---|
| RC1-C00 | PR #12 audit merge commit is an ancestor | required at application |
| RC1-C01 | Audit inventory remains exactly T121-T156 / 36 records | executable verification installed |
| RC1-C02 | Six crosswalks and twelve killed negative mutants remain reproducible | executable verification installed |
| RC1-C03 | T140, T150, and T156 remain conditional | executable verification installed |
| RC1-C04 | Historical `v1.2.0` still targets `befa094c...` | full-history CI verification installed |
| RC1-C05 | Historical DOI remains `10.5281/zenodo.21306969` | mandatory |
| RC1-C06 | Closure manifest hashes replay deterministically | builder and verifier installed |
| RC1-C07 | Clean-room Python, schema, fixture, proof-hole, and Phase 1-6 replay passes | CI pending |
| RC1-C08 | Lean 4 and Coq clean-runner builds pass | CI pending |
| RC1-C09 | Candidate tag and final tag do not exist | enforced |
| RC1-C10 | No GitHub Release, Zenodo version, or DOI action occurs | enforced |
| RC1-C11 | Draft tag annotation and release metadata are internally consistent | locally verifiable |
| RC1-C12 | Closure PR merge commit is recorded as exact candidate target | post-merge pending |
| RC1-C13 | Separate tag authorization is issued | not authorized by this patch |

## Merge rule

The closure patch may be merged only after RC1-C00 through RC1-C11 pass. Merging
this patch does not authorize tagging.

## Tag rule

`v1.3.0-rc1` may be created only after RC1-C12 and RC1-C13 are completed on the
same exact commit. The final tag `v1.3.0` remains outside this patch.
