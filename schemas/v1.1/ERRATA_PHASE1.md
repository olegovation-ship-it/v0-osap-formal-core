# Phase 1 schema erratum

This development-only erratum aligns `registry_state.schema.json` with T122.

- `all_of` prerequisite families may contain an empty `prerequisite_register_ids` array; the family is then vacuously satisfied.
- `one_of` prerequisite families continue to require at least one prerequisite register.
- The immutable `v1.2.0` tag and its Zenodo archive are not modified.
- This correction becomes release-bearing only after the v1.3.0 acceptance gates pass.
