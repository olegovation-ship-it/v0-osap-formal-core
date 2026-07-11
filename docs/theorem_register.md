# Theorem-target register

The normative v1.1 document reserves T121-T150. The immutable v1.2.0 release compiled the initial subset T121-T126. The v1.3.0 Phase 1 development patch corrects executable crosswalk coverage for T122, T124, and T125 without moving or retagging v1.2.0. Phase 2 adds the accepted development cluster T127-T132 without enlarging the archived v1.2.0 release claim. Phase 3 stages T133-T138 as build-ready and Actions-pending.

Baseline evidence commit: `48db564c085aec411552e78eef6c1740bd27a5ac`.
Phase 1 patch status: `ACCEPTED / CI PASS`.
Phase 2 head commit: `90865cca5fafde161254b7e313621d369ae5efc5`.
Phase 2 merge commit: `f494cd9401e2b9ff91d87de77e11f4eb2468726c`.
Phase 2 patch status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.

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
| T127 | Closure minimality | least closure | T127_closure_minimality | T127_closure_minimality | accepted; CI passed; merged |
| T128 | Alternative-support transparency | selected live member | T128_alternative_support_transparency | T128_alternative_support_transparency | accepted; CI passed; merged |
| T129 | Compatibility preservation | pair exclusion | T129_compatibility_preservation | T129_compatibility_preservation | accepted; CI passed; merged |
| T130 | Dimensional readiness soundness | readiness audit | T130_dimensional_readiness_soundness | T130_dimensional_readiness_soundness | accepted; CI passed; merged |
| T131 | Undefined is not zero | typed disjointness | T131_undefined_is_not_zero | T131_undefined_is_not_zero | accepted; CI passed; merged |
| T132 | DLE history adequacy | exact DLE fixtures | T132_dle_history_adequacy | T132_dle_history_adequacy | accepted; CI passed; merged |

Phase 2 acceptance is a v1.3.0 development result. It does not mutate the immutable v1.2.0 tag or DOI and does not claim completion of T133-T150.


## Phase 3 theorem expansion

| ID | Canonical name | Python | Lean 4 | Coq | Status |
|---|---|---|---|---|---|
| T133 | Fresh-token reactivation | token-history/fresh-ID audit | T133_fresh_token_reactivation | T133_fresh_token_reactivation | build-ready; Actions pending |
| T134 | Raw residual obstruction | raw residual live-set audit | T134_raw_residual_obstruction | T134_raw_residual_obstruction | build-ready; Actions pending |
| T135 | Robust residual obstruction | non-eliminable residual audit | T135_robust_residual_obstruction | T135_robust_residual_obstruction | build-ready; Actions pending |
| T136 | Relative-to-absolute non-promotion | source-claim firewall | T136_relative_to_absolute_non_promotion | T136_relative_to_absolute_non_promotion | build-ready; Actions pending |
| T137 | Approximation non-identity | approximation-identity firewall | T137_approximation_non_identity | T137_approximation_non_identity | build-ready; Actions pending |
| T138 | Terminal self-certification limit | cross-state certification audit | T138_terminal_self_certification_limit | T138_terminal_self_certification_limit | build-ready; Actions pending |

Phase 3 is not accepted or released until the full local and GitHub Actions matrix passes. The immutable v1.2.0 tag and DOI remain unchanged.
