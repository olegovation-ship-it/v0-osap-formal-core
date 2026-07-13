# Status and non-claims

<!-- V0_OSAP_RC1_STATUS_BEGIN -->
## v1.3.0 RC1 tag authorization and GitHub pre-release preparation

- Candidate scope: T121-T156 / 36 theorem records / 6 source crosswalks.
- Status: `RC1_TAG_AUTHORIZED / TAG_NOT_CREATED / PRERELEASE_NOT_CREATED`.
- Gate-audit PR: #12; merge commit: `29f9ec108efbb419fd030573b33ef5d30486d2ab`.
- Release-closure PR: #13; merge commit and authorized tag target: `cf9a05b46b9b6f29cd85942f99155f89a49817a7`.
- Checker development version remains `0.7.0.dev1`.
- Candidate tag name: `v1.3.0-rc1`.
- Historical tag `v1.2.0` remains pinned to `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3`.
- Historical DOI remains `10.5281/zenodo.21306969`.
- T121-T150 remain the normative v1.1 range; T151-T156 remain explicit post-v1.1 extensions.
- T140, T150, and T156 remain conditional.
- Tag-target authorization is complete; tag creation and GitHub pre-release publication are not yet complete.
- The final tag `v1.3.0`, Zenodo version creation, and DOI mutation remain unauthorized.
- No checker-completeness, unconditional global soundness, proof-term identity, global conservativity, empirical, physical, or cosmological claim is made.
<!-- V0_OSAP_RC1_STATUS_END -->


## v1.3.0 Phase 6

- Scope: T151-T156 explicit post-v1.1 development extension.
- Status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- Implementation baseline merge commit: `8053709c73045f59358244ec58afc84cfd0deeb6`.
- PR #10: 8/8 checks passed.
- Head commit: `dd1b234647a96b31719da0f3c5ad5e91b40144da`.
- Merge commit: `306f80dd36a70211b04f9a64215cc8807cbce709`.
- Merged at: `2026-07-12T21:09:06Z`.
- Checker development version: `0.7.0.dev1`.
- Python suite: 15 tests passed.
- Twelve paired fixtures and Lean 4 / Coq modules are accepted in the development tree.
- Phase 1 through Phase 5 accepted states remain preserved.
- T156 remains conditional on extension-handler isolation and no baseline-rule override.
- No v1.3.0 release, normative-v1.1 amendment, global conservativity, checker-completeness, unconditional global checker-soundness, proof-identity, or empirical claim.

## v1.3.0 Phase 5

- Scope: T145-T150.
- Status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- Implementation baseline merge commit: `2a769d7723470cce59df81262b586abf19b9c750`.
- PR #8: 8/8 checks passed.
- Head commit: `977c5404ebc5cdef9495edd1c46b08d3b0452acb`.
- Merge commit: `5c689de1a30104aa6c4e3860d5e7c26746e2d797`.
- Merged at: `2026-07-12T19:11:41Z`.
- Checker development version: `0.6.0.dev1`.
- Python suite: 14 tests passed.
- Twelve paired fixtures and Lean 4 / Coq modules are accepted in the development tree.
- Phase 1 through Phase 4 accepted states remain preserved.
- T150 remains conditional on proved rule lemmas and implementation invariants.
- No v1.3.0 release, theorem-completeness, proof-identity, checker-completeness, unconditional global soundness, or empirical claim.

## v1.3.0 Phase 4

- Scope: T139-T144.
- Status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- Implementation baseline merge commit: `24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30`.
- PR #6: 8/8 checks passed.
- Head commit: `9cec516c8ab026ce8d63fd2303f72ec5c1d36351`.
- Merge commit: `417866ec94fb24891c00bdfc2e522095777532bf`.
- Checker development version: `0.5.0.dev1`.
- Python suite: 113 tests passed.
- Twelve paired fixtures and Lean 4 / Coq modules are accepted in the development tree.
- Phase 1, Phase 2, and Phase 3 accepted states remain preserved.
- No v1.3.0 release, theorem-completeness, proof-identity, checker-completeness, or empirical claim.

## v1.3.0 Phase 3

- Scope: T133-T138.
- Status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- PR #4: 8/8 checks passed.
- Head commit: `2172591ed8a5ab3c1fa31f2a3a6575536f161fe4`.
- Merge commit: `c02b05f667b82aa31ac8865c31219b94b1fc74d2`.
- Checker development version: `0.4.0.dev1`.
- Python suite: 112 tests passed.
- Twelve paired fixtures and Lean 4 / Coq modules are accepted in the development tree.
- Phase 1 and Phase 2 accepted states remain preserved.
- No v1.3.0 release, theorem-completeness, proof-identity, checker-completeness, or empirical claim.

## v1.3.0 Phase 2

- Scope: T127-T132.
- Status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- PR #2: 8/8 checks passed.
- Head commit: `90865cca5fafde161254b7e313621d369ae5efc5`.
- Merge commit: `f494cd9401e2b9ff91d87de77e11f4eb2468726c`.
- Python suite: 111 tests passed.
- Lean 4 and Coq builds: PASS.
- Phase 1 remains accepted and historically preserved.
- No v1.3.0 release, theorem-completeness, proof-identity, or empirical claim.

## Immutable v1.2.0 baseline

- Tag `v1.2.0` and DOI `10.5281/zenodo.21306969` remain immutable.
- The archived baseline remains the bounded dual-backend compiler-passed T121-T126 release.
- The immutable baseline CI job executes proof-hole, schema, fixture, manifest, and closure verification.
- The Phase 2, Phase 3, Phase 4, and Phase 5 closure packages are development-history patches and do not rewrite the archived release.

## v1.3.0 Phase 1 assertions

- T122 receives an exact executable positive fixture for empty `all_of` vacuity.
- T124 receives an explicit Python rule and paired positive/countermodel fixtures.
- T125 is aligned with the Lean/Coq exhaustion predicate.
- Observer admissibility is separated into an unnumbered operational predicate.
- The old missing-prerequisite countermodel is no longer presented as T122 evidence.
- The old observer-support countermodel is no longer presented as T125 evidence.

## v1.3.0 Phase 2 assertions

- T127 checks least prerequisite closure.
- T128 checks explicit and live `one_of` support selection.
- T129 excludes jointly active incompatible register pairs.
- T130 requires live protocol prerequisites for `READY_VALUE`.
- T131 separates `UNDEFINED_DOMAIN` from every numeric value, including zero.
- T132 requires historical evidence and current no-live state for accepted DLE.

## v1.3.0 Phase 3 assertions

- T133 requires a distinct live token identifier for reactivation while preserving carrier, register, and context coordinates.
- T134 blocks raw relative V0 when any declared residual remains live.
- T135 blocks robust relative V0 when any declared non-eliminable residual remains live.
- T136 prevents direct relative-to-absolute V0 promotion.
- T137 prevents approximation certificates from licensing V0 identity.
- T138 forbids same-state terminal self-certification.

## v1.3.0 Phase 4 assertions

- T139 forbids archive evidence from exporting a current observer guard.
- T140 requires explicit policy-compliant independent witness support.
- T141 rejects ordinary V0-to-branch containment.
- T142 rejects label-only branch distinctness.
- T143 defers non-finite cardinality claims without typed meta-index and evidence.
- T144 computes one deterministic primary status for every finite closed-status list.

## v1.3.0 Phase 5 assertions

- T145 checks one canonical V0-OSAP-CJ-1 byte/hash representation.
- T146 checks canonical serialize/parse round-trip identity.
- T147 checks canonical replay-result identity under pinned proof, registry, and ruleset hashes.
- T148 rejects hidden parser coercion for schema or semantic-version changes.
- T149 checks canonical statement-hash correspondence between mapped Lean and Coq entries.
- T150 enforces only conditional accepted-fragment soundness under proved rule lemmas and implementation invariants.

## v1.3.0 Phase 6 assertions

- T151 requires explicit provenance for theorem IDs beyond the normative v1.1 ceiling T150.
- T152 rejects observed extension claim kinds absent from the declared vocabulary.
- T153 requires deterministic canonical diagnostic envelopes under pinned inputs.
- T154 rejects repeated identifiers in explicit finite evidence-provenance paths.
- T155 requires schema, language, checker, and semantic versions to match a declared lock tuple.
- T156 preserves baseline-only result hashes only under explicit isolation and no-override premises.

## Acceptance state

- Phase 6 status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- Phase 5 status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- Phase 1 status: `ACCEPTED / CI PASS`.
- Phase 2 status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- Phase 3 status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- Phase 4 status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.
- Package-level static verification: PASS.
- Python test suite and schema/fixture replay: PASS.
- Proof-hole scan: PASS.
- Lean 4 build: PASS.
- Coq build: PASS.
- GitHub Actions all-green matrix: PASS.
- Historical v1.2.0 manifest and closure preservation: PASS.

## Explicit non-claims

- No release claim for v1.3.0.
- No accepted theorem IDs beyond T156 in the current v1.3.0 development state.
- No complete mechanization claim for T1-T150 or T121-T150.
- No formal equivalence or proof-term identity claim among Python, Lean 4, and Coq.
- No checker-completeness claim.
- No empirical, physical, cosmological, disappearance-mechanism, quantum-gravity, or multiverse validation claim.
