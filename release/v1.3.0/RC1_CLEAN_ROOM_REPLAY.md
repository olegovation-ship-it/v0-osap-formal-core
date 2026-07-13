
# V0 OSAP v1.3.0 RC1 Clean-Room Replay Protocol

**Status:** `DEFINED / REPLAY_PENDING`  
**Candidate source baseline:** `29201b4937cef220ef0933d852250b021f3f44d4`  
**Historical release:** `v1.2.0` / `10.5281/zenodo.21306969`

## Environment

Use a new clone without local caches or generated proof artifacts. Record:

- operating system and architecture;
- Python version and dependency lock resolution;
- Lean version and lake toolchain;
- Coq version;
- exact candidate commit;
- timezone and locale only if they affect serialization.

## Replay sequence

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python scripts/build_rc1_release_inventory.py
python scripts/verify_rc1_statement_parity.py
python scripts/verify_rc1_gate_audit.py
pytest -q
v0-osap-fc1 schema-bundle
v0-osap-fc1 fixtures
python scripts/check_no_proof_holes.py
python scripts/verify_phase1_alignment.py
python scripts/verify_phase2_expansion.py
python scripts/verify_phase2_ci_closure.py
python scripts/verify_phase3_expansion.py
python scripts/verify_phase3_ci_closure.py
python scripts/verify_phase4_expansion.py
python scripts/verify_phase4_ci_closure.py
python scripts/verify_phase5_expansion.py
python scripts/verify_phase5_ci_closure.py
python scripts/verify_phase6_expansion.py
python scripts/verify_phase6_ci_closure.py
(cd lean && lake build)
(cd coq && make)
git diff --check
```

## Required comparison

Compare the replayed:

- theorem inventory hash;
- structural parity evidence hash;
- release manifest file hashes;
- fixture outcomes and decisive diagnostics;
- Python test count;
- Lean and Coq build results.

## Allowed differences

Only documented environment metadata may differ. The normalized theorem inventory,
diagnostic outcomes, canonical RC1 record hashes, and release-file hashes must not
differ.

## Completion record

A separate closure patch must record the clean-room operator, environment,
candidate commit, results, hashes, and any permitted differences before an RC1
tag is created.
