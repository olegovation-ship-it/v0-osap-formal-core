# WP3 Validator/IPEC Extension and Typed Outcome Binding

WP3 preserves the frozen V0-IPEC v0.1 contract at `5474a2c6a3e1c274d17f674889d427c1c91572f7` and its eight-code outcome vocabulary. It adds a separate `IPEC.EXT.GATE3.CLUSTER_B.*` rule layer for T157–T162 and binds exact WP2 result envelopes.

## Conservative resolution

- WP2 `DEFERRED` -> `INCONCLUSIVE_UNSUPPORTED_FRAGMENT`.
- WP2 `PASS` -> candidate `CERTIFIED`, actual `INCONCLUSIVE_UNSUPPORTED_FRAGMENT` until WP4 supplies the required Lean/Coq evidence.
- WP2 `REJECT` backed only by T121–T156 -> the exact frozen IPEC rejection selected by precedence.
- WP2 `REJECT` involving T157–T162 -> candidate rejection recorded, actual `INCONCLUSIVE_UNSUPPORTED_FRAGMENT` until WP4 proof activation.

This layer transports diagnostics and lineage; it does not add proof or release authority.
