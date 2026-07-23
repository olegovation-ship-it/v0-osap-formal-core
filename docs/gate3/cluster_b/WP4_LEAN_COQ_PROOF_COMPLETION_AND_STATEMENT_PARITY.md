# Gate 3 Cluster B WP4 — Lean/Coq Proof Completion and Statement Parity

## Canonical identity

- Repository: `olegovation-ship-it/v0-osap-formal-core`
- Exact baseline: `c90041d3da5b680b574b910de50d8769d32fbfa9`
- Work package: WP4
- Theorem range: T157-T162
- Release authorization: none

## Implementation boundary

This surface adds the dual-backend theorem modules, exact locked-signature parity records, deterministic proof-evidence activation fixtures, schemas, verifier, tests, and dedicated hosted CI. It does not mutate any frozen WP0-WP3 canonical record, historical ledger, WP2 semantics, WP3 binding, V0-IPEC v0.1 vocabulary, stable tag, release, Zenodo record, or DOI.

T158 and T160 remain conditional. T161 remains sufficiency-only. Statement parity is bounded to theorem ID, canonical signature, dependency list, conditionality, symbol correspondence, and normalized signature hash.

## Lifecycle

1. Verify the external ZIP SHA-256.
2. Run the applicator with `--check`; it uses a disposable worktree and changes no current repository file.
3. Review the check transcript.
4. Apply only after an explicit author decision.
5. Review the exact changed-path inventory before any manual commit or push.
6. Open a dedicated WP4 PR and require all hosted checks.
7. Do not begin WP5 until WP4 is merged and separately archived/closed.
