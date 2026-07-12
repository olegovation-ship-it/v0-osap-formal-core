# Phase 3 acceptance gates

Status: `ACCEPTED / CI PASS / MERGED / HISTORICALLY PRESERVED`.

Phase 3 covers T133-T138 and is accepted because all required gates passed on the installed repository state:

1. `python -m pip install -e '.[dev]'`
2. `pytest -q` - 112 tests passed.
3. `v0-osap-fc1 schema-bundle`
4. `v0-osap-fc1 fixtures`
5. `python scripts/check_no_proof_holes.py`
6. `python scripts/verify_phase1_alignment.py`
7. `python scripts/verify_phase2_expansion.py`
8. `python scripts/verify_phase2_ci_closure.py`
9. `python scripts/verify_phase3_expansion.py`
10. `cd lean && lake build`
11. `cd coq && make`
12. `git diff --check`
13. GitHub PR #4: 8/8 checks passed.
14. Schema validation, Python checker, Lean 4, Coq, and Release readiness were green.
15. PR head `2172591ed8a5ab3c1fa31f2a3a6575536f161fe4` was merged as `c02b05f667b82aa31ac8865c31219b94b1fc74d2`.
16. The immutable `v1.2.0` readiness job retained `verify_manifest.py` and `verify_closure.py`.
17. The `v1.2.0` tag and DOI `10.5281/zenodo.21306969` remained unchanged.
18. `python scripts/verify_phase3_ci_closure.py` validates the post-merge closure record.

This acceptance closes Phase 3 only. It does not release v1.3.0, move or retag v1.2.0, create a new DOI, or enlarge the archived v1.2.0 compiler-passed claim beyond T121-T126.
