# V₀ Research Program — Historical Branch H1 / H1.9C
## H1.9C-R1d2g-R2A1 IMPLEMENTATION ONLY

**Date:** 2026-08-31  
**Controlling contract:** R2A0  
**Scientific execution:** NOT PERFORMED / NOT AUTHORIZED  
**Geometry promotion:** 0/12

## 1. Result

The R2A0 architecture has been implemented as a copy-on-write successor package. Local implementation preflight is **PASS (10/10 tests)**. The frozen R1d2g scientific runner was not modified or rerun.

Repository deployment is **not complete** because the available GitHub integration returned `403 Resource not accessible by integration` for both branch creation and Contents API write. No repository mutation occurred. This is an external permission/transport blocker, not a scientific or implementation-test failure.

Frozen status:

`IMPLEMENTATION_PACKAGE_PASS / REPOSITORY_DEPLOYMENT_BLOCKED`

R2A1a is not yet authorized as a repository-state compliance verdict; first deploy this exact hashed implementation package, then audit the deployed bytes against this package.

## 2. Implemented architecture

- exact simple-fragment chain streaming;
- lossless `backbone_id` start/end anchor indexing;
- frozen mapping constructor semantics;
- immediate frozen canonicalization;
- legacy `M_` prefix compatibility plus full SHA-256/canonical-byte identity;
- collision fail-closed;
- bounded-memory sorted disk chunks;
- deterministic k-way merge and exact global dedup;
- natural-exhaustion requirement for C14b PASS;
- state/time/disk interruption → `NOT_REACHED_RESOURCE_EXHAUSTION`;
- no empty-set promotion from incomplete output;
- FX/I independent completion gate and streaming merge-join only after both rails PASS;
- self-excluding SHA-manifest construction.

## 3. Preflight

- Unit tests: **10/10 PASS**
- `compileall`: **PASS**
- forbidden scientific surface scan: **PASS**
- eager-reference vs streaming exact canonical set: **PASS**
- independent small-graph chain cross-check: **PASS**
- cross-chunk duplicate collapse: **PASS**
- forced hash-prefix collision: **FAIL-CLOSED PASS**
- forced resource interruption: **FAIL-CLOSED PASS**
- incomplete FX/I empty-equality firewall: **PASS**
- completed FX/I deterministic merge-join: **PASS**
- deterministic output under input/chunk variation: **PASS**
- SHA manifest self-exclusion: **PASS**
- frozen R1d2g-a1 mapping/signature compatibility reference: `M_f98de138a8f5e90ee8fa490f505f2ef9` **PASS**

## 4. File identities

- `historical/h1_9c/r1d2g_r2a1/r2a1_streaming_exact.py` — `9015b9f4ba799ea0c805cd8132c463d280bbc0874a724e5db5dfca2571e1c9c0`
- `historical/h1_9c/r1d2g_r2a1/tests/test_r2a1_streaming_exact.py` — `b6bce77397a92988a12a480579d4ed0ff873b6eea93ad19bdaa2172c281292da`
- `historical/h1_9c/r1d2g_r2a1/README.md` — `c3c661aabe33c0f096309fb53adc9c51c08eb7107dbe76bb73fdf9d59093a548`
- `.github/workflows/h1_9c_r1d2g_r2a1_implementation_preflight.yml` — `d21fa00fa67ecce9591a04534e96f165dfae3d7a0cc6127ac8c51c010fe9a958`

## 5. GitHub deployment blocker

Authoritative base inspected: `main` = `5e19a9e15b17c3b572b49040cfac75ddbca1edbd`.

Write attempts:

- create copy-on-write branch → `403 Resource not accessible by integration`;
- create isolated R2A1 repository file → same `403`;
- repository mutation → **FALSE**.

The package therefore contains the exact repository-relative paths and CI workflow required for deployment once a GitHub connection with Contents/Refs write capability is available.

## 6. Firewall

No R2A2 scientific execution, target/CMB access, shaft-vector extraction, azimuth/inclination derivation, AUC/PI, synthetic rotations, significance claims, mapping promotion, or geometry promotion occurred.

## 7. Terminal decision

`R1d2g-R2A1_IMPLEMENTATION_ONLY_PACKAGE_COMPLETE / LOCAL_PREFLIGHT_PASS_10_OF_10 / GITHUB_REPOSITORY_DEPLOYMENT_NOT_REACHED_PERMISSION_403 / SCIENTIFIC_EXECUTION_NOT_AUTHORIZED / GEOMETRY_PROMOTION=0/12 / META_STOP`
