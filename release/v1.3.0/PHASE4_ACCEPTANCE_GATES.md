# Phase 4 acceptance gates

Status: `BUILD_READY / CI_PENDING`.

Phase 4 covers T139-T144. Acceptance requires the following installed-repository checks:

1. `python -m pip install -e '.[dev]'`
2. `pytest -q` — expected total: 113 tests.
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
15. A Draft PR from `v1.3.0-development` to `main`.
16. The complete GitHub Actions matrix is green.
17. Review and merge are completed before status advances to accepted.

Baseline merge commit: `24fc12fa0fce3d2b67ebe684e00ef7bb8537cf30`.

The immutable `v1.2.0` readiness job must retain `verify_manifest.py` and `verify_closure.py`; tag `v1.2.0` and DOI `10.5281/zenodo.21306969` must remain unchanged.
