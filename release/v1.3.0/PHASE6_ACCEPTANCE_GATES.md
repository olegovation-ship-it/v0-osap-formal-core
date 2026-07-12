# Phase 6 Acceptance Gates

**Scope:** T151-T156  
**Baseline merge commit:** `8053709c73045f59358244ec58afc84cfd0deeb6`  
**Current state:** `BUILD_READY / CI_PENDING`

## Gate A — extension provenance

- [ ] T151 records the explicit post-v1.1 extension namespace and record.
- [ ] The normative v1.1 ceiling remains T150.
- [ ] T151-T156 are not described as inherited v1.1 targets.

## Gate B — executable parity

- [ ] Six Python rules are implemented.
- [ ] Twelve paired fixtures replay deterministically.
- [ ] JSON Schema validates all new claim forms.
- [ ] Canonical statement hashes match the crosswalk.

## Gate C — proof-assistant parity

- [ ] Lean 4 Phase 6 module builds.
- [ ] Coq Phase 6 module builds.
- [ ] Proof-hole scan passes.
- [ ] Backend symbols exist for T151-T156.

## Gate D — preservation

- [ ] Phase 1-5 verifiers remain green.
- [ ] `v1.2.0` tag remains immutable.
- [ ] DOI `10.5281/zenodo.21306969` remains unchanged.
- [ ] No v1.3.0 release is created by this patch.

## Gate E — closure prerequisite

Phase 6 may move to `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED` only after a dedicated implementation PR passes the complete GitHub Actions matrix and is merged into `main`.
