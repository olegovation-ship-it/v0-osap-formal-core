# Theorem-target register

The normative v1.1 document reserves T121-T150. The immutable v1.2.0 release compiled the initial subset T121-T126. The v1.3.0 Phase 1 development patch corrects executable crosswalk coverage for T122, T124, and T125 without moving or retagging v1.2.0.

Baseline evidence commit: `48db564c085aec411552e78eef6c1740bd27a5ac`.
Phase 1 patch status: `PATCH_READY / CI_PENDING`.

| ID | Canonical name | Python after Phase 1 | Lean 4 | Coq | Phase 1 status |
|---|---|---:|---:|---:|---|
| T121 | live guard has a live token | existing fixture | baseline compiled | baseline compiled | unchanged |
| T122 | empty all-of prerequisite set is vacuously satisfied | exact positive fixture | baseline compiled | baseline compiled | blocker closed by schema erratum and exact fixture; CI pending |
| T123 | DLE implies current no-live status | existing fixture | baseline compiled | baseline compiled | unchanged |
| T124 | live residual obstructs robust relative V0 | explicit `robust_relative_v0` rule plus positive/countermodel fixtures | baseline compiled | baseline compiled | blocker closed; CI pending |
| T125 | terminal self-certification exposes support exhaustion | exact exhaustion rule plus positive/countermodel fixtures | definition retained | definition retained | semantic collision removed; CI pending |
| T126 | branch-local support does not license absolute promotion | existing fixture | baseline compiled | baseline compiled | unchanged |

## Observer-certificate split

`TerminalSelfCertificate` remains the T125 predicate: internal support and external evidence are both empty. `AdmissibleObserverCertificate` is a separate unnumbered operational predicate requiring external evidence and an independence group. The two predicates must not share a diagnostic code or theorem-target mapping.

`compiled` remains bounded evidence that the corresponding module passed its backend build and proof-hole scan. It does not establish cross-assistant proof-term identity or semantic equivalence.
