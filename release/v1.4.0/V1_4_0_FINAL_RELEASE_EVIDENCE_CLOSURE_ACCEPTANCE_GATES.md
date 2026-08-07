# V0 OSAP v1.4.0 — Final Release Evidence Closure Acceptance Gates

Date: 2026-08-07

| Gate | Requirement | Expected |
|---|---|---|
| FREC-G01 | Canonical predecessor `75b84e5800686372fb6a19add12c8896f59274ee`, tree `8ec377cadaeddfd6bef67dd01d981b83d09c327b`, exact parents. | PASS |
| FREC-G02 | PR #34 merged; Gate 3 Cluster B WP6 `PASS / GO / FORMALLY_CLOSED`. | PASS |
| FREC-G03 | 29 terminal workflow runs (15 success, 14 skipped, 0 failed/cancelled/pending); 65 completed checks. | PASS |
| FREC-G04 | Annotated tag `v1.4.0` identity and peeled target remain immutable. | PASS |
| FREC-G05 | GitHub Release `366706025`, body hash and four-asset boundary remain frozen. | PASS |
| FREC-G06 | Exact surface is 3 modified + 10 additive = 13; no removal or 14th path. | PASS |
| FREC-G07 | Baseline `release/v1.4.0/` subtree `45aaeec48443924fa153ac343ab904bac814792f` and all pre-existing paths remain byte-identical. | PASS |
| FREC-G08 | Historical pre-PR #34 WP6 non-terminal records remain unchanged. | PASS |
| FREC-G09 | Historical v1.3.0 sections remain byte-preserved outside new v1.4.0 blocks. | PASS |
| FREC-G10 | `CITATION.cff` remains blob `0adb7aaa73a052b8621c3f0d393f6f128cf4bada`; README DOI target unchanged. | PASS |
| FREC-G11 | No v1.4.0 Zenodo record or DOI; DOI mutation zero. | PASS |
| FREC-G12 | Repository release `v1.4.0` and checker/project `0.7.0.dev1` remain separate namespaces. | PASS |
| FREC-G13 | Manifest builder reproduces checked-in manifest deterministically. | PASS |
| FREC-G14 | Static verifier and unit tests pass fail-closed. | PASS |
| FREC-G15 | Workflow permissions are read-only with no workflow_dispatch, release publication, Zenodo/DOI, or artifact-upload mutation. | PASS |

Terminal expected state: `FINAL_RELEASE_EVIDENCE_CLOSED / STABLE_TAG_CREATED / FINAL_GITHUB_RELEASE_CREATED / ZENODO_NOT_PUBLISHED`
