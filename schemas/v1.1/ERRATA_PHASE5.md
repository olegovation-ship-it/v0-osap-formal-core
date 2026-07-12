# FC-1 v1.1 Phase 5 schema extension

Phase 5 adds six audit claim kinds for theorem targets T145-T150:

- canonical serialization and canonical hash;
- canonical round-trip identity;
- pinned replay determinism;
- visible schema/semantic migration;
- Lean/Coq statement-hash correspondence;
- conditional accepted-fragment checker soundness.

These records are audit interfaces. They do not convert schema validity into semantic proof and do not make T150 unconditional.
