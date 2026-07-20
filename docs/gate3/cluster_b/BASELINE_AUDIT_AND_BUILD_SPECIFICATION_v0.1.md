# Gate 3 Cluster B Baseline Audit and Build Specification v0.1

**Program:** V0 OSAP Formal Core  
**Target development version:** v1.4.0  
**Target branch:** `v1.4.0-development`  
**Date:** 2026-07-20  
**Decision:** `PASS_WITH_IDENTIFIED_BUILD_GAPS / GO_TO_IMPLEMENTATION_SPEC`  
**Release authorization:** `NONE`

## 1. Purpose

This artifact defines the exact baseline and implementation plan for **Gate 3 - Cluster B: DLE and Residual Core**. It does not modify V0 OSAP v1.3.0, V0 Validator Core v0.12, V0-IPEC v0.1, the submitted Paper B baseline, or submission register v121. It authorizes only a new development branch and a bounded implementation cycle.

Gate 3 closes only when one coherent logical cluster has a complete evidence stack: prose and machine statements, dependencies, positive and negative models, Lean and Coq proofs, statement parity, validator/IPEC lineage, deterministic replay, and explicit non-claims.

## 2. Exact baseline lock

| Layer | Frozen identity | Role |
|---|---|---|
| OSAP stable source | `v1.3.0` -> `13bf095688bcabd5b090f188e9bd28a16237edeb`; DOI `10.5281/zenodo.21346728` | Canonical T121-T156 theorem and dual-backend owner |
| OSAP branch start | `main` at `a13a96fda4964dde1719c7d014f11878e1103b20` | Post-release archival baseline for `v1.4.0-development` |
| V0-IPEC v0.1 | `5474a2c6a3e1c274d17f674889d427c1c91572f7` | Frozen Gate 2 integration contract |
| Validator Core | `v0.12-compiler-passed-freeze` -> `3540f47198140ca0a3612f247cfe356fa7fba2cb`; DOI `10.5281/zenodo.21285577` | Frozen validator/schema baseline |
| Paper B | `SCICO-D-26-00508`, submitted 19 July 2026 | Frozen replay/correspondence evidence baseline |
| Register | v121 package SHA-256 `9e75d4c27a6151195486641d3d1074aaab494e2b1a50f293d5a710be58903eaf` | Operative governance baseline |

## 3. Baseline audit result

The inherited theorem base is strong but not yet a closed Cluster B release.

- Existing cluster candidates: **10** theorem records.
- Required semantic roles: **7**.
- Complete from existing theorems: **4**.
- Partial: **1**.
- Open theorem gaps: **2**.
- Proposed bounded extension: **T157-T162** (six provisional IDs).
- Target cluster size after implementation: **16** theorem records.
- Existing IPEC negative-fixture baseline: **24**.
- New cluster negative/boundary target: **12**.
- Combined target after integration: **36**.

The central gaps are a named StrongDLE contract, live-residual persistence across non-interfering DLE, typed residual separation, and an admissible model-pair non-eliminability theorem.

## 4. Existing theorem ownership

The inherited canonical core is:

| ID | Role | Status |
|---|---|---|
| T123 | DLE current no-live consequence | inherited, parity PASS, IPEC-bound |
| T124 | live residual obstructs robust relative V0 | inherited, parity PASS, IPEC-bound |
| T126 | direct branch-local to absolute firewall | inherited, parity PASS, IPEC-bound |
| T132 | DLE historical adequacy | inherited, parity PASS, IPEC-bound |
| T134 | raw residual obstruction | inherited, parity PASS, IPEC-bound |
| T135 | robust non-eliminable residual obstruction | inherited, parity PASS, IPEC-bound |
| T136 | relative-to-absolute non-promotion | inherited, parity PASS, IPEC-bound |
| T139 | archive cannot export a current guard | inherited, parity PASS, IPEC-bound |
| T140 | independent witness conditional sufficiency | inherited, conditional, parity PASS, IPEC-bound |
| T142 | branch-label insufficiency | inherited, parity PASS, IPEC-bound |

T140 remains conditional. Nothing in Gate 3 removes the conditional status of T140, T150, or T156.

## 5. Required semantic roles

1. **DLE transition** - closed by T123 and T132, subject to cluster-level replay aggregation.
2. **Strong DLE** - partial; requires T157.
3. **Live residual persistence** - open; requires T158 and T162.
4. **Raw residual obstruction** - closed by T134; T161 adds a minimal-witness corollary.
5. **Model-pair non-eliminability** - open; requires T159 and T160.
6. **Robust obstruction** - closed by T124 and T135.
7. **Branch-local firewall** - closed by T126, T136, and T142.

## 6. Provisional theorem extension T157-T162

The six IDs are reserved only within this build specification. They become canonical after WP1 collision audit and repository merge.

- **T157 strong_dle_characterization** - explicit equivalence between StrongDLE, historical liveness, current no-live status, and transition provenance.
- **T158 live_residual_persistence_under_noninterfering_dle** - conditional persistence under explicit non-interference.
- **T159 residual_type_separation** - no type collapse without an admissible translation map.
- **T160 model_pair_noneliminability_witness** - conditional non-eliminability from an admissible shared-fragment model pair.
- **T161 minimal_single_residual_obstruction** - one live declared residual is a minimal sufficient obstruction witness; no converse completeness claim.
- **T162 historical_live_token_nonconversion** - historical evidence cannot become current liveness without fresh activation.

## 7. Dependency order

Recommended implementation order:

1. T157 from T123 and T132.
2. T159 from typed-domain and archive/current-state separation.
3. T162 from fresh-token reactivation and archive non-export.
4. T158 from T124, T132, T139, and the new nonconversion discipline.
5. T161 as a bounded corollary of T134.
6. T160 from T134, T135, T140, T142, and T159.

The verifier must reject cycles and undeclared imports.

## 8. Repository layout

All work occurs on `v1.4.0-development`. The planned files are machine-recorded in `registries/CLUSTER_B_REPOSITORY_BUILD_PATHS.json`. The implementation should add a versioned `release/v1.4.0` surface, dedicated Python/Lean/Coq modules, cluster fixtures, a parity verifier, and a dedicated Gate 3 workflow.

## 9. Work packages

### WP0 - Baseline Freeze and Branch Bootstrap
Create `v1.4.0-development` exactly from OSAP `main` commit `a13a96f...`; verify all frozen identities and emit a branch-bootstrap record.

### WP1 - Cluster Registry, Strong DLE, and ID Closure
Finalize the seven-role map, collision-audit T157-T162, define the canonical StrongDLE and residual contracts, and emit complete theorem records plus an acyclic DAG.

### WP2 - Transition, Residual, and Model-Pair Library
Implement the executable bounded semantics and produce 12 positive fixtures, 12 negative/boundary fixtures, and two model-pair fixtures.

### WP3 - Validator/IPEC Extension and Typed Outcome Binding
Add a new versioned extension layer. Do not edit frozen V0-IPEC v0.1. Preserve the Gate 2 rule that every nonprocedural outcome has theorem and evidence lineage.

### WP4 - Lean/Coq Proof Completion and Statement Parity
Implement T157-T162 in both backends, import and preserve the inherited theorems, normalize statements, verify hashes, and enforce zero proof holes.

### WP5 - CI Integration and Deterministic Evidence Manifests
Implement the 14 mandatory CI jobs, canonical evidence manifests, and two-run byte-identical replay.

### WP6 - Gate 3 Audit and Release-Candidate Decision
Evaluate all 24 mandatory gates. The decision is `CLOSE_GATE3` or `HOLD_WITH_EXPLICIT_BLOCKERS`. Tag, GitHub Release, Zenodo, and DOI steps remain separate and unauthorized.

## 10. Fixture campaign

The campaign adds 12 cluster-specific negative/boundary fixtures and 12 positive models. It exercises DLE conflicts, missing history/provenance, residual-transition interference, residual-type collapse, invalid model pairs, minimal obstruction, silent historical-token promotion, branch promotion, and robust obstruction.

Unsupported premises must return `INCONCLUSIVE_UNSUPPORTED_FRAGMENT`; they must not be transformed into fabricated certification or failure.

## 11. CI matrix

Fourteen mandatory jobs are specified in `ci/GATE3_CLUSTER_B_CI_JOB_MATRIX.json`: baseline, schemas, ID audit, role coverage, DAG, Python semantics, positive models, negative/boundary campaign, Lean, Coq, parity, IPEC lineage, deterministic replay, and final Gate 3 audit.

## 12. Acceptance rule

All 24 gates in `audit/GATE3_CLUSTER_B_ACCEPTANCE_GATES.json` are mandatory. In particular:

- seven roles complete;
- T157-T162 collision-free;
- zero Lean/Coq proof holes;
- 100 percent statement parity;
- theorem/evidence lineage for all nonprocedural outcomes;
- 12 new negative/boundary fixtures and a combined target of at least 36;
- two byte-identical replays;
- explicit claim perimeter;
- no release action embedded in the implementation PR.

## 13. Claim perimeter

This Gate 3 plan does not establish proof-term identity, kernel equivalence, unrestricted cross-backend semantic equivalence, checker completeness, global soundness, empirical confirmation, physical disappearance, cosmological vacuum ontology, or absolute-V0 existence. T158 and T160 are expected to remain conditional on recorded premises.

## 14. Final build decision

**Baseline audit: PASS. Build specification: APPROVED. Implementation: NOT STARTED. Release: NOT AUTHORIZED.**

The first implementation deliverable should be:

`V0_OSAP_v1.4.0_Gate3_Cluster_B_WP0_Baseline_Freeze_and_Branch_Bootstrap_Patch_v0.1`
