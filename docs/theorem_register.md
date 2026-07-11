# Theorem-target register

The normative v1.1 document reserves T121-T150. The immutable v1.2.0 release compiled the initial subset T121-T126. The v1.3.0 Phase 1 development patch corrects executable crosswalk coverage for T122, T124, and T125 without moving or retagging v1.2.0.

Baseline evidence commit: `48db564c085aec411552e78eef6c1740bd27a5ac`.
Phase 1 patch status: `ACCEPTED / CI PASS`.

| ID | Canonical name | Python after Phase 1 | Lean 4 | Coq | Phase 1 status |
|---|---|---:|---:|---:|---|
| T121 | live guard has a live token | existing fixture | baseline compiled | baseline compiled | unchanged |
| T122 | empty all-of prerequisite set is vacuously satisfied | exact positive fixture | baseline compiled | baseline compiled | blocker closed by schema erratum and exact fixture; CI passed |
| T123 | DLE implies current no-live status | existing fixture | baseline compiled | baseline compiled | unchanged |
| T124 | live residual obstructs robust relative V0 | explicit `robust_relative_v0` rule plus positive/countermodel fixtures | baseline compiled | baseline compiled | blocker closed; CI passed |
| T125 | terminal self-certification exposes support exhaustion | exact exhaustion rule plus positive/countermodel fixtures | definition retained | definition retained | semantic collision removed; CI passed |
| T126 | branch-local support does not license absolute promotion | existing fixture | baseline compiled | baseline compiled | unchanged |

## Observer-certificate split

`TerminalSelfCertificate` remains the T125 predicate: internal support and external evidence are both empty. `AdmissibleObserverCertificate` is a separate unnumbered operational predicate requiring external evidence and an independence group. The two predicates must not share a diagnostic code or theorem-target mapping.

`compiled` remains bounded evidence that the corresponding module passed its backend build and proof-hole scan. It does not establish cross-assistant proof-term identity or semantic equivalence.

## Phase 2 theorem expansion

| ID | Canonical name | Python | Lean 4 | Coq | Status |
|---|---|---|---|---|---|
| T127 | Closure minimality | least closure | T127_closure_minimality | T127_closure_minimality | CI pending |
| T128 | Alternative-support transparency | selected live member | T128_alternative_support_transparency | T128_alternative_support_transparency | CI pending |
| T129 | Compatibility preservation | pair exclusion | T129_compatibility_preservation | T129_compatibility_preservation | CI pending |
| T130 | Dimensional readiness soundness | readiness audit | T130_dimensional_readiness_soundness | T130_dimensional_readiness_soundness | CI pending |
| T131 | Undefined is not zero | typed disjointness | T131_undefined_is_not_zero | T131_undefined_is_not_zero | CI pending |
| T132 | DLE history adequacy | exact DLE fixtures | T132_dle_history_adequacy | T132_dle_history_adequacy | CI pending |
