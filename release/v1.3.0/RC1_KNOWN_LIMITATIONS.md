
# RC1 Known Limitations and Non-Claims

1. Structural-record parity is not proof-term identity.
2. Matching canonical hashes establish deterministic record identity, not semantic
   truth.
3. Lean and Coq compilation establishes only the encoded propositions under the
   imported assumptions and host logic.
4. The Python checker is not claimed complete.
5. T150 is conditional on proved rule lemmas and implementation invariants.
6. T156 is conditional on extension-handler isolation and no baseline-rule
   override.
7. T151-T156 are explicit post-v1.1 development extensions; they do not
   retroactively amend the v1.1 theorem reservation.
8. Clean-room reproducibility is pending until independently replayed.
9. The patch does not create an RC1 or final release tag.
10. The immutable `v1.2.0` tag and DOI `10.5281/zenodo.21306969` remain unchanged.
11. No empirical or physical claim concerning V0 is made.
12. No private journal correspondence is included in the public release evidence.
