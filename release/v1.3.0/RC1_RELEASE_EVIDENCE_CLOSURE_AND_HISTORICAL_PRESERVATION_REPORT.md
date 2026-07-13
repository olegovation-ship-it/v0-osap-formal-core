# V0 OSAP v1.3.0 RC1 Release Evidence Closure and Historical Preservation Report

## Closure state

`RC1_RELEASE_EVIDENCE_CLOSED / TAG_CREATED / PRERELEASE_CREATED / FINAL_RELEASE_NOT_CREATED`

The exact-target annotated tag `v1.3.0-rc1` has been created and resolves to
`cf9a05b46b9b6f29cd85942f99155f89a49817a7`. GitHub reports a published, non-draft pre-release:

- name: `V0 OSAP v1.3.0-rc1 — Release Candidate 1`;
- URL: `https://github.com/olegovation-ship-it/v0-osap-formal-core/releases/tag/v1.3.0-rc1`;
- published at: `2026-07-13T18:15:33Z`;
- `isPrerelease`: `true`;
- `isDraft`: `false`.

## Provenance

- RC1 gate-audit merge: `29f9ec108efbb419fd030573b33ef5d30486d2ab`;
- RC1 release-closure and tag-preparation merge: `cf9a05b46b9b6f29cd85942f99155f89a49817a7`;
- RC1 tag-authorization merge: `cc1148f4c01cec2e2fca05651d02edc18fdc7312`;
- exact authorized tag target: `cf9a05b46b9b6f29cd85942f99155f89a49817a7`.

## Historical preservation

The prior release-closure and tag-authorization manifests are retained as frozen
historical snapshots and are referenced by SHA-256 from the new evidence-closure
record. Their former pre-creation action ledgers remain unchanged rather than being
retrospectively rewritten.

Historical tag `v1.2.0`, target `befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3`, and DOI
`10.5281/zenodo.21306969` remain immutable.

## Gate-audit integrity repair

The executable `scripts/verify_rc1_gate_audit.py` is restored. The repository copy
had become empty during the tag-authorization change set, allowing a no-op process
to return success. This patch reinstates the 36-record inventory audit, the 12/12
negative-mutant kill audit, workflow contract checks, deterministic evidence output,
and an explicit regression test preventing another empty-verifier pass.

## Boundary

T140, T150, and T156 remain conditional. The RC1 tag and GitHub pre-release do not
authorize the final tag `v1.3.0`, a final GitHub Release, a Zenodo version, or
any DOI mutation.

No checker-completeness, unconditional global checker-soundness, proof-term
identity, global conservativity, empirical, physical, or cosmological claim is made.
