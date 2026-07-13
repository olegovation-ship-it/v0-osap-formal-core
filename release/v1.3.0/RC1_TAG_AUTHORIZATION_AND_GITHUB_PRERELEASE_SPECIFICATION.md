# V0 OSAP v1.3.0 RC1 Tag Authorization, Annotated Tag Creation, and GitHub Pre-Release Specification

**Artifact ID:** `V0_OSAP_V1_3_0_RC1_TAG_AUTHORIZATION_ANNOTATED_TAG_GITHUB_PRERELEASE`
**Patch version:** `0.1`
**Date:** `2026-07-13`
**Repository:** `olegovation-ship-it/v0-osap-formal-core`
**Target branch:** `v1.3.0-development`
**Closure PR:** `#13`
**Authorized tag target:** `cf9a05b46b9b6f29cd85942f99155f89a49817a7`
**Candidate tag:** `v1.3.0-rc1`
**Patch state:** `RC1_TAG_AUTHORIZED / TAG_NOT_CREATED / PRERELEASE_NOT_CREATED`
**Immutable historical release:** `v1.2.0` at `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3`
**Immutable historical DOI:** `10.5281/zenodo.21306969`
**Author:** Dmytro Panasenko, Independent Researcher

## 1. Authorization decision

PR #13 completed the RC1 release-closure and tag-preparation stage and merged
as `cf9a05b46b9b6f29cd85942f99155f89a49817a7`. Post-merge GitHub Actions runs shown for `main` and the
synchronized `v1.3.0-development` branch passed for the Python checker, schema
validation, RC1 gate audit, release readiness, RC1 clean-room release replay,
Lean 4, and Coq.

This patch separately authorizes `cf9a05b46b9b6f29cd85942f99155f89a49817a7` as the only permitted target for the
annotated tag `v1.3.0-rc1`. It does not authorize the final tag `v1.3.0`, any Zenodo
version, any DOI mutation, or any empirical, physical, or cosmological claim.

## 2. Two-step release discipline

Applying and merging this patch records authorization but performs no external
release action. After this authorization patch itself passes CI and is merged:

1. run `scripts/create_rc1_annotated_tag.py` with its explicit execution and
   target-confirmation flags;
2. verify that the pushed tag resolves exactly to `cf9a05b46b9b6f29cd85942f99155f89a49817a7`;
3. run `scripts/create_rc1_github_prerelease.py` with its explicit execution and
   tag-confirmation flags;
4. retain the generated evidence outside the tagged tree for the subsequent RC1
   evidence-closure and historical-preservation patch.

The creation scripts are dry-run by default. No tag or GitHub Release is created
by the apply script or CI workflow.

## 3. Candidate boundary

The release candidate preserves:

- theorem inventory T121-T156, exactly 36 records;
- six canonical source crosswalks;
- twelve killed negative release-gate mutants;
- checker development version `0.7.0.dev1`;
- Lean 4 and Coq mappings;
- deterministic fixtures, manifests, and clean-room replay;
- conditional status of T140, T150, and T156;
- historical tag `v1.2.0`, its target commit, and DOI `10.5281/zenodo.21306969`.

## 4. Non-claims

The candidate does not claim checker completeness, unconditional global checker
soundness, proof-term identity between backends, unrestricted semantic
equivalence, global conservativity, empirical confirmation of a physical vacuum,
a cosmological mechanism, disappearance dynamics, or a multiverse.

## 5. Exact release metadata

- Annotated tag: `v1.3.0-rc1`
- Tag target: `cf9a05b46b9b6f29cd85942f99155f89a49817a7`
- GitHub pre-release title: `V0 OSAP v1.3.0-rc1 — Release Candidate 1`
- Pre-release flag: `true`
- Draft flag: `false`
- Final release tag: not authorized
- Zenodo action: not authorized
