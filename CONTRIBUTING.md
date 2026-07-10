# Contributing

1. Preserve the distinction between specification, schema validity, checker replay, model witnessing, and proof-assistant compilation.
2. Do not add `sorry`, `admit`, `Admitted`, or equivalent proof holes to frozen modules.
3. Add a positive fixture and a countermodel for every new semantic rule.
4. Keep diagnostic output deterministic: code, priority, path, and related IDs must be stable.
5. Update the theorem register and release manifest when adding or renaming formal targets.
6. Do not promote branch-local or relative-V0 results to absolute-V0 claims without an explicit bridge object.
