# Changelog

<!-- V0_OSAP_RC1_CHANGELOG_BEGIN -->
## [Unreleased] - v1.3.0 final release authorization and stable-tag preparation

- Separately authorized exact stable target `13bf095688bcabd5b090f188e9bd28a16237edeb`.
- Prepared annotated tag `v1.3.0` without creating or pushing it.
- Prepared non-draft, non-prerelease GitHub final-release notes and metadata.
- Added deterministic authorization manifest, verifier, dry-run-first creation scripts, tests, and validation-only CI.
- Preserved RC1 tag `v1.3.0-rc1` at `cf9a05b46b9b6f29cd85942f99155f89a49817a7`.
- Preserved `v1.2.0`, target `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3`, DOI `10.5281/zenodo.21306969`, conditional records, and non-claims.
- Retained embedded checker component version `0.7.0.dev1`.
- Created no stable tag, final GitHub Release, Zenodo version, or DOI change.
- State: `FINAL_RELEASE_AUTHORIZED / STABLE_TAG_NOT_CREATED / FINAL_GITHUB_RELEASE_NOT_CREATED / ZENODO_NOT_PUBLISHED`.
<!-- V0_OSAP_RC1_CHANGELOG_END -->


## [Unreleased] — Phase 6 accepted development state

- Accepted explicit post-v1.1 extension cluster T151-T156 after PR #10 passed 8/8 checks.
- Recorded implementation baseline `8053709c73045f59358244ec58afc84cfd0deeb6`, head `dd1b234647a96b31719da0f3c5ad5e91b40144da`, and merge commit `306f80dd36a70211b04f9a64215cc8807cbce709`.
- Recorded 15 passing Python tests, schema and deterministic fixture replay PASS, proof-hole PASS, Phase 1-5 preservation/closure PASS, Phase 6 verifier PASS, Lean 4 PASS, and Coq PASS.
- Advanced T151-T156 theorem-crosswalk parity from `PATCH_READY_CI_PENDING` to `ACCEPTED_CI_PASS`.
- Added a dedicated Phase 6 CI-closure and historical-preservation verifier.
- Preserved the immutable v1.2.0 manifest and closure jobs, tag, DOI `10.5281/zenodo.21306969`, and Phase 1-5 closure history.
- State: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.

## [Unreleased]

### Phase 5 theorem expansion T145-T150
- Added strict V0-OSAP-CJ-1 canonical serialization, parsing, round-trip, SHA-256, and hash-envelope utilities.
- Added executable replay-determinism, migration-visibility, backend-correspondence, and conditional checker-soundness audits.
- Added twelve paired fixtures and Lean 4 / Coq Phase 5 modules.
- Added a canonical statement-hash theorem crosswalk and Phase 5 verifier.
- Advanced the development checker to `0.6.0.dev1`.
- Baseline merge commit is `2a769d7723470cce59df81262b586abf19b9c750`.
- Status is `BUILD_READY / CI_PENDING`; no Phase 5 acceptance or v1.3.0 release is claimed.

### Phase 5 CI closure
- Recorded PR #8 with 8/8 successful checks.
- Recorded head commit `977c5404ebc5cdef9495edd1c46b08d3b0452acb` and merge commit `5c689de1a30104aa6c4e3860d5e7c26746e2d797`.
- Recorded 14 passing Python tests, schema and fixture PASS, proof-hole PASS, Phase 1 preservation PASS, Phase 2-4 expansion/closure PASS, Phase 5 verifier PASS, Lean 4 PASS, and Coq PASS.
- Advanced T145-T150 theorem-crosswalk parity from `PATCH_READY_CI_PENDING` to `ACCEPTED_CI_PASS`.
- Added a dedicated Phase 5 CI-closure and historical-preservation verifier.
- Preserved the immutable v1.2.0 manifest and closure jobs, tag, DOI `10.5281/zenodo.21306969`, and Phase 1-4 closure history.
- Recorded the Phase 5 implementation merge baseline `5c689de1a30104aa6c4e3860d5e7c26746e2d797` for development-branch synchronization.

### Phase 4 theorem expansion T139-T144
- Added executable archive/witness, no-container, branch-distinctness, cardinality, and diagnostic-precedence rules.
- Added twelve paired fixtures and Lean 4 / Coq Phase 4 modules.
- Added a canonical statement-hash theorem crosswalk and Phase 4 verifier.
- Advanced the development checker to `0.5.0.dev1`.
- Baseline merge commit is `24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30`.
- Status is `BUILD_READY / CI_PENDING`; no Phase 4 acceptance or v1.3.0 release is claimed.

### Phase 3 theorem expansion T133-T138
- Added executable fresh-token reactivation and residual-obstruction rules.
- Extended the relative-to-absolute firewall and added approximation-identity and same-state certification firewalls.
- Added twelve paired fixtures and Lean 4 / Coq Phase 3 modules.
- Added a statement-hash theorem crosswalk and Phase 3 verifier.
- Advanced the development checker to `0.4.0.dev1`.
- Status advanced to `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`; no v1.3.0 release is claimed.

### Phase 4 CI closure
- Recorded PR #6 with 8/8 successful checks.
- Recorded head commit `9cec516c8ab026ce8d63fd2303f72ec5c1d36351` and merge commit `417866ec94fb24891c00bdfc2e522095777532bf`.
- Recorded 113 passing Python tests, schema and fixture PASS, proof-hole PASS, Phase 1 preservation PASS, Phase 2 and Phase 3 expansion/closure PASS, Phase 4 verifier PASS, Lean 4 PASS, and Coq PASS.
- Advanced T139-T144 theorem-crosswalk parity from `PATCH_READY_CI_PENDING` to `ACCEPTED_CI_PASS`.
- Added a dedicated Phase 4 CI-closure and historical-preservation verifier.
- Preserved the immutable v1.2.0 manifest and closure jobs, tag, DOI, and Phase 1-3 closure history.
- Recorded the Phase 4 implementation merge baseline `417866ec94fb24891c00bdfc2e522095777532bf` for development-branch synchronization.

### Phase 3 CI closure
- Recorded PR #4 with 8/8 successful checks.
- Recorded head commit `2172591ed8a5ab3c1fa31f2a3a6575536f161fe4` and merge commit `c02b05f667b82aa31ac8865c31219b94b1fc74d2`.
- Recorded 112 passing Python tests, schema and fixture PASS, proof-hole PASS, Phase 1 preservation PASS, Phase 2 expansion and closure PASS, Phase 3 verifier PASS, Lean 4 PASS, and Coq PASS.
- Advanced T133-T138 theorem-crosswalk parity from `PATCH_READY_CI_PENDING` to `ACCEPTED_CI_PASS`.
- Added a dedicated Phase 3 CI-closure and historical-preservation verifier.
- Preserved the immutable v1.2.0 manifest and closure jobs, tag, DOI, and Phase 1 / Phase 2 closure history.
- Recorded `main` and `v1.3.0-development` as synchronized at the Phase 3 merge commit.

### Phase 2 theorem expansion T127-T132
- Added executable rules for closure, one_of support selection, compatibility, protocol readiness, typed dimensional results, and exact DLE history mapping.
- Added twelve paired fixtures and Lean 4 / Coq expansion modules.
- Added a statement-hash theorem crosswalk and Phase 2 verifier.
- Advanced the development checker to `0.3.0.dev1`.
- Status advanced to `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`; no v1.3.0 release is claimed.

### Phase 2 CI closure
- Recorded PR #2 with 8/8 successful checks.
- Recorded head commit `90865cca5fafde161254b7e313621d369ae5efc5` and merge commit `f494cd9401e2b9ff91d87de77e11f4eb2468726c`.
- Recorded 111 passing Python tests, schema and fixture PASS, proof-hole PASS, Phase 1 preservation PASS, Phase 2 verifier PASS, Lean 4 PASS, and Coq PASS.
- Advanced T127-T132 theorem-crosswalk parity from `PATCH_READY_CI_PENDING` to `ACCEPTED_CI_PASS`.
- Added a dedicated Phase 2 CI-closure and historical-preservation verifier.
- Preserved the immutable v1.2.0 manifest and closure jobs, tag, DOI, and detailed release history.
- Corrected the stale non-claim that the development tree contained no theorem IDs beyond T126.

### Phase 1 semantic alignment
- Added exact executable coverage for T122 empty-`all_of` vacuity.
- Added explicit T124 robust-relative-V0 residual-obstruction diagnostics and fixtures.
- Aligned Python T125 semantics with the Lean 4 and Coq terminal-support-exhaustion predicate.
- Split observer admissibility into a separate unnumbered predicate and diagnostic.
- Added the Phase 1 theorem crosswalk, schema erratum, acceptance gates, static verifier, and development CI job.
- Bumped the development checker version to `0.2.0.dev1`.

### Phase 1 CI closure
- Advanced Phase 1 from `PATCH_READY / CI_PENDING` to `ACCEPTED / CI PASS`.
- Recorded the all-green PR #1 matrix for Schema validation, Python checker, Lean 4, Coq, and Release readiness.
- Restored `python scripts/verify_closure.py` to the immutable-v1.2.0 baseline job.
- Added explicit CI-closure and historical-preservation verification.

### Post-release metadata preservation
- Added the Zenodo version DOI `10.5281/zenodo.21306969`.
- Added repository and tagged-release backlinks to the citation metadata.
- Finalized `CITATION.cff` for the archived v1.2.0 software release.
- Updated the closure verifier to require finalized DOI metadata.
- Preserved the immutable `v1.2.0` tag; this is a post-release metadata patch, not a retag.

### Release discipline
- Preserved the immutable `v1.2.0` tag and DOI `10.5281/zenodo.21306969`.
- Phase 1, Phase 2, Phase 3, and Phase 4 acceptance are not a v1.3.0 release or an enlargement of the archived v1.2.0 compiler-passed claim.

## [1.2.0] - 2026-07-11

### Added
- Compiler-version evidence in `release/compiler_versions.json`.
- Closure verification script and final release-readiness gate.
- GitHub Release notes for the bounded FC-1 baseline.

### Changed
- README status advanced from bootstrap/pending to dual-backend compiler-passed.
- Lean 4 and Coq workflows now print compiler versions.
- The theorem register now records compiled status for T121-T126.
- Release manifest status advanced to `DUAL_BACKEND_ACCEPTED`.

### Fixed
- Replaced Lean 4 reserved identifiers in the branch-firewall definitions and T126 wrapper.
- Refreshed manifest integrity after the Lean repair.

### Verified
- Schema validation: PASS.
- Python checker and fixtures: PASS.
- Lean 4 build and proof-hole scan: PASS.
- Coq build and proof-hole scan: PASS.
- Release readiness: PASS.
- Evidence commit: `48db564c085aec411552e78eef6c1740bd27a5ac`.

### Limits
- No theorem-completeness claim beyond the initial T121-T126 subset.
- No proof-equivalence claim between Lean 4 and Coq.
- No empirical or physical validation claim.
- Version 1.2.0 is archived under DOI `10.5281/zenodo.21306969`; the tagged source baseline remains immutable.
