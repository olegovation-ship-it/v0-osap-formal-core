# Changelog

## [Unreleased]

### Pending
- Zenodo DOI, repository backlink, and final citation update after the tagged GitHub Release is archived.

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
- DOI remains pending until tagged-release archival.
