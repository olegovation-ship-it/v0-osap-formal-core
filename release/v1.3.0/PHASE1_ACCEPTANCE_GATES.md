# Phase 1 acceptance gates

Phase 1 may be marked `ACCEPTED` only when all gates pass on the installed repository state:

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

Until these gates pass, use `PATCH_READY / CI_PENDING`, not `compiler-passed`, `accepted`, or `v1.3.0 released`.
