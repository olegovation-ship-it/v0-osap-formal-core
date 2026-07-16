# V0 OSAP v1.3.0 Post-Merge Legacy Lifecycle Compatibility Acceptance Gates

- [x] The common CI blocker is identified as the legacy `accepted_lifecycle_markers` assertion in `verify_rc1_gate_audit.py`.
- [x] `POST_MERGE_ARCHIVAL_CLOSEOUT_RECORDED` is accepted as a valid later lifecycle marker.
- [x] Acceptance of the post-merge marker requires `MAIN_DEVELOPMENT_SYNCHRONIZED`.
- [x] Acceptance of the post-merge marker requires `ZENODO_LIFECYCLE_REPLAY_COMPATIBLE`.
- [x] Acceptance of the post-merge marker requires `RELEASE_IMMUTABLE`.
- [x] Acceptance requires DOI `10.5281/zenodo.21346728`.
- [x] Acceptance requires stable tag target `13bf095688bcabd5b090f188e9bd28a16237edeb`.
- [x] Checker component remains `0.7.0.dev1`.
- [x] T140, T150, and T156 remain conditional.
- [x] Eight frozen predecessor/RC1 artifacts are replayed against their recorded SHA-256 values.
- [x] No historical manifest, record, tag, release, archive, DOI, theorem record, or checker version is rewritten.
- [x] The repair changes compatibility recognition only; it does not weaken release authorization.

Acceptance state:

`POST_MERGE_LEGACY_LIFECYCLE_COMPATIBILITY_RECORDED / FROZEN_MANIFEST_REPLAY_PRESERVED`
