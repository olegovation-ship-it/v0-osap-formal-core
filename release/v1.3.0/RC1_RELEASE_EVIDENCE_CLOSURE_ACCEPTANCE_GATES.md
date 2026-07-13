# RC1 Release Evidence Closure Acceptance Gates

## G1 — Exact annotated-tag identity

`v1.3.0-rc1` must exist as an annotated tag and peel exactly to
`cf9a05b46b9b6f29cd85942f99155f89a49817a7`.

## G2 — GitHub pre-release evidence

The GitHub object must have tag `v1.3.0-rc1`, URL `https://github.com/olegovation-ship-it/v0-osap-formal-core/releases/tag/v1.3.0-rc1`,
publication time `2026-07-13T18:15:33Z`, `isPrerelease=true`, and
`isDraft=false`.

## G3 — Frozen historical snapshots

`RC1_RELEASE_CLOSURE_MANIFEST.json` and
`RC1_TAG_AUTHORIZATION_MANIFEST.json` must remain byte-identical to their recorded
SHA-256 values. Historical pre-creation ledgers are not rewritten.

## G4 — Historical v1.2.0 preservation

Tag `v1.2.0` must remain pinned to `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3` and DOI
`10.5281/zenodo.21306969` must remain unchanged.

## G5 — Formal-scope and conditionality preservation

The inventory remains T121-T156 with 36 records and 6 source crosswalks. T140,
T150, and T156 remain conditional.

## G6 — Final-release prohibition

Tag `v1.3.0`, a final GitHub Release, Zenodo publication, and DOI mutation
remain unauthorized and absent.

## G7 — Executable gate-audit integrity

`verify_rc1_gate_audit.py` must contain and execute the inventory, parity, and
negative-mutant audits. An empty or no-op verifier fails regression tests.

## G8 — Validation-only CI

The RC1 closure workflows may verify tags and evidence but must not run tag creation,
GitHub release creation, Zenodo deposition, or DOI mutation commands.
