# Coq Mapping (v1.1)

Design-level mapping only. No compiler-passed claim is made in v1.1.

- IDs: `string` plus `valid_id`.
- Finite collections: lists with `NoDup` and decidable membership.
- Registry: `Record registry_state`.
- Semantic rules: `Prop` definitions indexed by registry state.
- Executable checks: `bool` functions connected by reflection/soundness lemmas.
- Theorem identifiers: T121-T150, names reserved in Appendix C of the specification.

First proof subset recommended: T121-T135.
