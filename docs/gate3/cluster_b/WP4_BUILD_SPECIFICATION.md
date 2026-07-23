# V0 OSAP v1.4.0 Gate 3 Cluster B WP4 Build Specification v0.1

**Work package:** WP4 — Lean/Coq Proof Completion and Statement Parity
**Repository:** `olegovation-ship-it/v0-osap-formal-core`
**Target branch:** `v1.4.0-development`
**Exact baseline:** `c90041d3da5b680b574b910de50d8769d32fbfa9`
**Date:** 2026-07-23
**Decision:** `APPROVED_FOR_TEMPORARY_WORKTREE_CHECK`
**Release authorization:** `NONE`

## 1. Baseline correction

The supplied handoff contains a one-character SHA transcription error: `c90041dc3a5b680b1574b910de50d8769d32fbfa9` is not the repository commit. The merged WP3 closeout commit is `c90041d3da5b680b574b910de50d8769d32fbfa9`. The applicator is locked to the repository value and refuses the mistyped value.

## 2. Roadmap position

The operative Gate 3 Cluster B roadmap is WP0 baseline freeze, WP1 registry/contracts, WP2 executable semantics, WP3 Validator/IPEC typed binding, WP4 dual-backend proofs and statement parity, WP5 deterministic CI/evidence integration, and WP6 Gate 3 audit/RC decision. WP5 and WP6 remain unauthorized.

## 3. Exact WP4 scope

WP4 implements only the six locked targets T157-T162 in Lean 4 and Coq, imports inherited dependencies, verifies the exact normalized statement hashes, records symbol correspondence, enforces zero proof holes, and supplies a separate proof-evidence activation layer for the candidate outcomes already produced by WP3.

WP4 does not change theorem identities, WP1 contracts, WP2 runtime semantics, the frozen V0-IPEC v0.1 vocabulary, or any archived WP0-WP3 output.

## 4. Theorem targets and dependencies

| ID | Locked target | Dependencies | Conditionality |
|---|---|---|---|
| T157 | StrongDLE characterization | T123, T132 | unconditional on the supported finite fragment |
| T158 | live residual persistence under non-interfering DLE | T124, T132, T139, T162 | conditional |
| T159 | residual type separation | T131, T139 | unconditional under the declared typed vocabulary |
| T160 | admissible model-pair non-eliminability witness | T134, T135, T140, T142, T159 | conditional |
| T161 | minimal single-residual obstruction | T134 | sufficiency-only corollary |
| T162 | historical live-token nonconversion | T133, T139 | unconditional under the typed activation vocabulary |

The exact signatures and hashes are machine-recorded in `WP4_SCOPE_AND_ACCEPTANCE_GATES.json` and the implementation proof manifest.

## 5. Proof and parity products

The implementation adds `lean/V0OSAP/ClusterB.lean` and `coq/theories/ClusterB.v`, updates only four aggregate import surfaces, records a six-row proof manifest, and validates every canonical signature against the locked WP1 SHA-256. Statement parity means exact identity of theorem ID, canonical signature, dependency list, conditionality, and normalized signature hash; it does not claim proof-term identity, kernel equivalence, or unrestricted semantic equivalence between Lean and Coq.

## 6. WP3 activation boundary

WP3 deliberately leaves candidate `CERTIFIED` and extension-theorem rejection outcomes inconclusive until WP4 proof evidence exists. WP4 adds a separate activation function. It may activate a candidate outcome only when all extension theorems in the exact lineage have both backend records, matching statement hashes, and parity `PASS`. Missing evidence remains `INCONCLUSIVE_UNSUPPORTED_FRAGMENT`; parity failure becomes `BACKEND_PARITY_FAILURE`.

## 7. Repository and preservation boundary

All WP0-WP3 canonical records and historical ledgers are byte-frozen. Four aggregate import files are exact-hash-guarded; all other changed paths are new WP4-owned paths. The verifier compares every baseline file byte-for-byte, excluding only those four import surfaces.

## 8. Validation sequence

The applicator `--check` creates a disposable detached worktree at `c90041d3da5b680b574b910de50d8769d32fbfa9`, installs the payload, builds deterministic manifests, verifies the exact allowlist and frozen baseline, runs the WP4 tests plus the full Python regression, scans for proof holes, builds Lean 4 and Coq, and executes `git diff --check`. Any failure removes the worktree. Actual apply snapshots every touched path and rolls back on any failure.

## 9. Prohibitions

No automatic commit or push, release tag, GitHub Release, Zenodo publication, DOI authorization or mutation, WP5 start, force-push, history rewrite, theorem renumbering, canonical record mutation, or historical ledger mutation is authorized.

**Build specification: PROVIDED. Implementation patch: PROVIDED SEPARATELY.**
