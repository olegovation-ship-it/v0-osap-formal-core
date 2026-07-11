# Phase 1 acceptance gates

Phase 1 is marked `ACCEPTED / CI PASS` because all gates passed on the installed repository state:

1. `python -m pip install -e '.[dev]'`
2. `pytest -q`
3. `v0-osap-fc1 schema-bundle`
4. `v0-osap-fc1 fixtures`
5. `python scripts/check_no_proof_holes.py`
6. `python scripts/verify_phase1_alignment.py`
7. `cd lean && lake build`
8. `cd coq && make`
9. GitHub Actions: Schema validation, Python checker, Lean 4, Coq, and Release readiness all green.
10. No T122 attribution remains on the missing-prerequisite countermodel.
11. No T125 attribution remains on observer admissibility fixtures.
12. The immutable `v1.2.0` tag remains unchanged.
13. The immutable-v1.2.0 readiness job runs both `verify_manifest.py` and `verify_closure.py`.
14. The detailed v1.2.0 changelog history is preserved.

This acceptance closes Phase 1 only. It does not create a v1.3.0 release, move the v1.2.0 tag, or enlarge the archived compiler-passed claim.
