# Changelog

## [Unreleased]

### Phase 2 theorem expansion T127-T132
- Added executable rules for closure, one_of support selection, compatibility, protocol readiness, typed dimensional results, and exact DLE history mapping.
- Added twelve paired fixtures and Lean 4 / Coq expansion modules.
- Added a statement-hash theorem crosswalk and Phase 2 verifier.
- Advanced the development checker to `0.3.0.dev1`.
- Status remains `PATCH_READY / CI_PENDING`; no v1.3.0 release is claimed.


### Phase 1 semantic alignment
- Added exact executable coverage for T122 empty-`all_of` vacuity.
- Added explicit T124 robust-relative-V0 residual-obstruction diagnostics and fixtures.
- Aligned Python T125 semantics with the Lean 4 and Coq terminal-support-exhaustion predicate.
- Split observer admissibility into a separate unnumbered predicate and diagnostic.
- Added the Phase 1 theorem crosswalk, schema erratum, acceptance gates, static verifier, and development CI job.
- Bumped the development checker version to `0.2.0.dev1`.

### Phase 1 CI closure
- Advanced Phase 1 from `PATCH_READY / CI_PENDING` to `ACCEPTED / CI_PASS`.
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
- Phase 1 acceptance is not a v1.3.0 release or a full-v1.3.0 compiler-passed claim.

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
