# V0 OSAP v1.4.0 — Final GitHub Release Evidence Closure and Historical Preservation Report

Date: 2026-08-07

## Terminal state

`FINAL_RELEASE_EVIDENCE_CLOSED / STABLE_TAG_CREATED / FINAL_GITHUB_RELEASE_CREATED / ZENODO_NOT_PUBLISHED`

This record closes the repository-facing GitHub final-release evidence layer for v1.4.0. It does not perform or claim Zenodo publication or DOI finalization.

## Canonical repository and merge identity

- Repository: `olegovation-ship-it/v0-osap-formal-core`
- Canonical merge / baseline: `75b84e5800686372fb6a19add12c8896f59274ee`
- Tree: `8ec377cadaeddfd6bef67dd01d981b83d09c327b`
- Parent 1: `47614ce7891f4895e003cb85e7651b7d043a963d`
- Parent 2: `aeeaeefa5d40bbb26ffe7c9ae02abc75b3636a5d`
- PR #34: `WP6 successor-attestation layer`; closed and merged.
- `main` and `v1.4.0-development` are synchronized at the canonical merge baseline before this evidence-closure successor is applied.

## Gate 3 Cluster B WP6 authority

Formal Gate 3 Cluster B WP6 closure is `PASS / GO / FORMALLY_CLOSED`. The terminal authority is the separately frozen 2026-08-07 formal closure tied to PR #34 and the canonical merge. Historical repository records created before that authority remain historical evidence and are not rewritten.

Post-merge hosted CI for the canonical merge is terminal: 29 workflow runs completed, with 15 success and 14 skipped; failures, cancellations and pending runs are zero. Checks API inventory is 65 completed check runs with zero pending.

## Stable tag and GitHub Release

The annotated tag `v1.4.0` is immutable:
- tag object: `21d9a42ceb9985dbcd6330582a8cb80e81d883c5`
- peeled target: `75b84e5800686372fb6a19add12c8896f59274ee`
- tag-message SHA-256: `9dbffe6f0bf3182f9e19fe278d8b3834ed3bb607d75282bae814db39b8fee5a5`

GitHub Release:
- ID: `366706025`
- tag: `v1.4.0`
- name: `V0 OSAP v1.4.0 — Stable Release`
- draft: `false`
- prerelease: `false`
- latest: `true`
- published: `2026-08-07T11:32:01Z`
- body SHA-256: `530711e7baa7408f51f53844c969020520a0c0bd5c100bfe29275867735623ba`
- asset count: `4`

This closure does not move the tag, edit the Release, or replace any Release asset.

## Historical preservation

The exact baseline subtree `release/v1.4.0/` is `45aaeec48443924fa153ac343ab904bac814792f`. Every path already present in that subtree at `75b84e5800686372fb6a19add12c8896f59274ee` is preservation-locked byte-for-byte.

In particular, `GATE3_CLUSTER_B_WP6_ACCEPTANCE_GATES.json` historically records `gate3_closed=false` and `release_authorized=false`, and `GATE3_CLUSTER_B_WP6_GATE_RESULT_MATRIX.json` historically records `gate3_closed=false` with hosted-CI evidence pending. These records are `HISTORICAL_PRE_PR34_NON_TERMINAL_EVIDENCE`. Their values are not stale data to be edited; they are evidence of the earlier lifecycle boundary.

The new terminal release evidence is additive and successor-scoped. No historical v1.3.0 status block is replaced.

## Version boundary

Repository release version is `v1.4.0`. The embedded checker/project remains `v0-osap-fc1` version `0.7.0.dev1`. These are separate version namespaces. No component promotion is performed.

## Zenodo / DOI boundary

- `ZENODO_V1_4_0_CREATED=NO`
- `V1_4_0_DOI_FINALIZED=NO`
- `DOI_MUTATION_PERFORMED=NO`
- `CITATION_CFF_CHANGE_NOW=NO`
- `README_DOI_TARGET_CHANGE_NOW=NO`

`CITATION.cff` remains byte-identical to the baseline and retains the archived v1.3.0 DOI `10.5281/zenodo.21346728`. The README DOI badge/target remains unchanged. A v1.4.0 DOI must not be invented; publication-dependent metadata remains deferred to a separately authorized Zenodo stage.

## Exact repository surface

Modified: 3. Additive: 10. Total: 13. Removals: 0.

## Non-claims

This evidence closure does not claim proof-term identity, unrestricted semantic equivalence, checker completeness, unconditional global checker soundness, global conservativity, or empirical, physical, cosmological, disappearance-mechanism, quantum-gravity, or multiverse validation.
