# Phase 5 Acceptance Gates

Phase 5 covers T145-T150 from baseline merge commit `2a769d7723470cce59df81262b586abf19b9c750`.

| Gate | Requirement | Build-patch state |
|---|---|---|
| P5-G01 | Baseline commit is an ancestor of the development branch | required |
| P5-G02 | Python package installs and 14 tests pass | pending repository replay |
| P5-G03 | Schema bundle validates | pending repository replay |
| P5-G04 | All fixtures replay deterministically | pending repository replay |
| P5-G05 | Proof-hole scan passes | pending repository replay |
| P5-G06 | Phase 1-4 preservation/closure verifiers pass | pending repository replay |
| P5-G07 | Phase 5 static verifier passes | pending repository replay |
| P5-G08 | Lean 4 build passes | pending repository replay |
| P5-G09 | Coq build passes | pending repository replay |
| P5-G10 | `git diff --check` passes | pending repository replay |
| P5-G11 | GitHub Actions complete matrix passes | pending PR |
| P5-G12 | Immutable v1.2.0 tag and DOI `10.5281/zenodo.21306969` remain unchanged | mandatory |

Phase 5 remains `BUILD_READY / CI_PENDING` until all gates pass and the implementation PR is reviewed and merged.
