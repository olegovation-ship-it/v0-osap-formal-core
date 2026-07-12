# Phase 4 acceptance gates

Status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.

Phase 4 covers T139-T144 and is accepted because all required gates passed on the installed repository state:

1. `python -m pip install -e '.[dev]'`
2. `pytest -q` - 113 tests passed.
3. `v0-osap-fc1 schema-bundle`
4. `v0-osap-fc1 fixtures`
5. `python scripts/check_no_proof_holes.py`
6. `python scripts/verify_phase1_alignment.py`
7. `python scripts/verify_phase2_expansion.py`
8. `python scripts/verify_phase2_ci_closure.py`
9. `python scripts/verify_phase3_expansion.py`
10. `python scripts/verify_phase3_ci_closure.py`
11. `python scripts/verify_phase4_expansion.py`
12. `cd lean && lake build`
13. `cd coq && make`
14. `git diff --check`
15. GitHub PR #6: 8/8 checks passed.
16. Schema validation, Python checker, Lean 4, Coq, and Release readiness were green.
17. PR head `9cec516c8ab026ce8d63fd2303f72ec5c1d36351` was merged as `417866ec94fb24891c00bdfc2e522095777532bf`.
18. The immutable `v1.2.0` readiness job retained `verify_manifest.py` and `verify_closure.py`.
19. The `v1.2.0` tag and DOI `10.5281/zenodo.21306969` remained unchanged.
20. `python scripts/verify_phase4_ci_closure.py` validates the post-merge closure record.

Implementation baseline merge commit: `24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30`.

This acceptance closes Phase 4 only. It does not release v1.3.0, move or retag v1.2.0, create a new DOI, or enlarge the archived v1.2.0 compiler-passed claim beyond T121-T126.
