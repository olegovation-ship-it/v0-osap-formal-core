# Lean 4 Mapping (v1.1)

Design-level mapping only. No compiler-passed claim is made in v1.1.

- IDs: `String` plus `WellFormedId`.
- Finite collections: `Finset` where extensional equality is intended.
- Registry: `structure RegistryState`.
- Semantic rules: `Prop` definitions indexed by registry state.
- Executable checks: Boolean functions with soundness theorems.
- Theorem identifiers: T121-T150, names reserved in Appendix C of the specification.

First proof subset recommended: T121-T135.
