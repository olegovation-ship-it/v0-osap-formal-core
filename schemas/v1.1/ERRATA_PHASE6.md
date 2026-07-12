# ERRATA / EXTENSION NOTE — Phase 6

The normative V0 OSAP v1.1 theorem-target interval is T121-T150. Phase 6 introduces T151-T156 as an explicit repository-local v1.3.0 development extension. These IDs are not represented as latent or previously reserved v1.1 targets.

The registry schema is extended with six audit claim kinds and their typed fields. The schema version remains `v1.1` for compatibility with the current fixture corpus; the extension is made visible through:

- `semantic_version = FC-1-v1.1+phase6`;
- an explicit T151 extension-provenance audit;
- the Phase 6 theorem crosswalk;
- the Phase 6 build specification and acceptance gates.

This note does not amend the immutable v1.2.0 release or DOI.
