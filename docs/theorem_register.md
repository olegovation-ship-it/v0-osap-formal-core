# Theorem-target register

The normative v1.1 document reserves T121-T150. Version 1.2.0 mechanizes and compiles only the initial subset T121-T126.

Evidence commit: `48db564c085aec411552e78eef6c1740bd27a5ac`.

| ID | Bootstrap name | Python | Lean 4 | Coq | v1.2.0 status |
|---|---|---:|---:|---:|---|
| T121 | live guard has a live token | yes | compiled | compiled | bounded dual-backend PASS |
| T122 | empty all-of prerequisite set is vacuously satisfied | n/a | compiled | compiled | bounded dual-backend PASS |
| T123 | DLE implies current no-live status | yes | compiled | compiled | bounded dual-backend PASS |
| T124 | live residual obstructs robust relative V0 | yes | compiled | compiled | bounded dual-backend PASS |
| T125 | terminal self-certification exposes support exhaustion | yes | compiled | compiled | bounded dual-backend PASS |
| T126 | branch-local support does not license absolute promotion | yes | compiled | compiled | bounded dual-backend PASS |

`compiled` means the corresponding source module passed its backend build and the repository proof-hole scan. It does not mean that Lean and Coq proof terms are identical, that a machine-checked cross-assistant equivalence theorem exists, or that T127-T150 are implemented.
