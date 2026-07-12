# Theorem-target register

The normative v1.1 document reserves T121-T150. The immutable v1.2.0 release compiled the initial subset T121-T126. The v1.3.0 Phase 1 development patch corrects executable crosswalk coverage for T122, T124, and T125 without moving or retagging v1.2.0. Phase 2 adds the accepted development cluster T127-T132 without enlarging the archived v1.2.0 release claim. Phase 3 adds the accepted development cluster T133-T138 under the same historical-preservation boundary. Phase 4 adds the accepted development cluster T139-T144 under the same historical-preservation boundary from implementation baseline `24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30`. Phase 5 stages the final reserved cluster T145-T150 from baseline `2a769d7723470cce59df81262b586abf19b9c750`.

Baseline evidence commit: `48db564c085aec411552e78eef6c1740bd27a5ac`.
Immutable baseline DOI: `10.5281/zenodo.21306969`.
Phase 1 patch status: `ACCEPTED / CI PASS`.
Phase 2 head commit: `90865cca5fafde161254b7e313621d369ae5efc5`.
Phase 2 merge commit: `f494cd9401e2b9ff91d87de77e11f4eb2468726c`.
Phase 2 patch status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
Phase 3 head commit: `2172591ed8a5ab3c1fa31f2a3a6575536f161fe4`.
Phase 3 merge commit: `c02b05f667b82aa31ac8865c31219b94b1fc74d2`.
Phase 3 patch status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
Phase 4 implementation baseline merge commit: `24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30`.
Phase 4 head commit: `9cec516c8ab026ce8d63fd2303f72ec5c1d36351`.
Phase 4 merge commit: `417866ec94fb24891c00bdfc2e522095777532bf`.
Phase 4 patch status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.

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
| T133 | Fresh-token reactivation | token-history/fresh-ID audit | T133_fresh_token_reactivation | T133_fresh_token_reactivation | accepted; CI passed; merged |
| T134 | Raw residual obstruction | raw residual live-set audit | T134_raw_residual_obstruction | T134_raw_residual_obstruction | accepted; CI passed; merged |
| T135 | Robust residual obstruction | non-eliminable residual audit | T135_robust_residual_obstruction | T135_robust_residual_obstruction | accepted; CI passed; merged |
| T136 | Relative-to-absolute non-promotion | source-claim firewall | T136_relative_to_absolute_non_promotion | T136_relative_to_absolute_non_promotion | accepted; CI passed; merged |
| T137 | Approximation non-identity | approximation-identity firewall | T137_approximation_non_identity | T137_approximation_non_identity | accepted; CI passed; merged |
| T138 | Terminal self-certification limit | cross-state certification audit | T138_terminal_self_certification_limit | T138_terminal_self_certification_limit | accepted; CI passed; merged |

Phase 3 acceptance is a v1.3.0 development result. It does not mutate the immutable v1.2.0 tag or DOI and does not claim completion of T139-T150.

## Phase 4 theorem expansion

| ID | Canonical name | Python | Lean 4 | Coq | Status |
|---|---|---|---|---|---|
| T139 | Archive non-guard-export | archive current-guard export audit | T139_archive_non_guard_export | T139_archive_non_guard_export | accepted; CI passed; merged |
| T140 | Independent-witness conditional sufficiency | witness policy/independence audit | T140_independent_witness_conditional_sufficiency | T140_independent_witness_conditional_sufficiency | accepted; CI passed; merged |
| T141 | No-container | NullMark ordinary-containment firewall | T141_no_container | T141_no_container | accepted; CI passed; merged |
| T142 | Branch-label insufficiency | distinctness-basis audit | T142_branch_label_insufficiency | T142_branch_label_insufficiency | accepted; CI passed; merged |
| T143 | Cardinality licensing | typed meta-index/evidence audit | T143_cardinality_licensing | T143_cardinality_licensing | accepted; CI passed; merged |
| T144 | Diagnostic precedence totality | finite primary-status replay | T144_diagnostic_precedence_totality | T144_diagnostic_precedence_totality | accepted; CI passed; merged |

Phase 4 acceptance is a v1.3.0 development result. It does not mutate the immutable v1.2.0 tag or DOI `10.5281/zenodo.21306969` and does not claim completion of T145-T150.

## Phase 5 theorem expansion

Phase 5 baseline merge commit: `2a769d7723470cce59df81262b586abf19b9c750`.
Phase 5 patch status: `BUILD_READY / CI PENDING`.

| ID | Canonical name | Python | Lean 4 | Coq | Status |
|---|---|---|---|---|---|
| T145 | Canonical serialization determinism | canonical byte/hash audit | T145_canonical_serialization_determinism | T145_canonical_serialization_determinism | build-ready; CI pending |
| T146 | Round-trip identity | canonical round-trip audit | T146_round_trip_identity | T146_round_trip_identity | build-ready; CI pending |
| T147 | Replay determinism | pinned replay-result audit | T147_replay_determinism | T147_replay_determinism | build-ready; CI pending |
| T148 | Schema migration visibility | migration/coercion audit | T148_schema_migration_visibility | T148_schema_migration_visibility | build-ready; CI pending |
| T149 | Backend statement correspondence | canonical statement-hash audit | T149_backend_statement_correspondence | T149_backend_statement_correspondence | build-ready; CI pending |
| T150 | Accepted-fragment checker soundness | conditional soundness audit | T150_accepted_fragment_checker_soundness | T150_accepted_fragment_checker_soundness | build-ready; CI pending |

Phase 5 is not accepted or released until the complete local and GitHub Actions matrix passes. T150 is conditional on proved rule lemmas and implementation invariants. The immutable v1.2.0 tag and DOI `10.5281/zenodo.21306969` remain unchanged.
