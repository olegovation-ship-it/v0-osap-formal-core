from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load(path: str) -> dict: return json.loads((ROOT / path).read_text(encoding="utf-8"))

crosswalk = load("release/v1.3.0/theorem_crosswalk_phase3.json")
assert crosswalk["theorem_range"] == "T133-T138"
assert crosswalk["phase2_status"] == "ACCEPTED_CI_PASS_MERGED_HISTORICALLY_PRESERVED"
assert crosswalk["phase3_status"] == "BUILD_READY_CI_PENDING"
lean = (ROOT / "lean/V0OSAP/Phase3.lean").read_text(encoding="utf-8")
coq = (ROOT / "coq/theories/Phase3.v").read_text(encoding="utf-8")
semantic = (ROOT / "checker/v0_osap_fc1/semantic.py").read_text(encoding="utf-8")
assert [row["theorem_id"] for row in crosswalk["records"]] == [f"T{i}" for i in range(133,139)]
for row in crosswalk["records"]:
    normalized = {key: row[key] for key in ["theorem_id","canonical_name","formal_signature","assumptions","conclusion"]}
    expected = hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert row["canonical_statement_sha256"] == expected
    assert row["lean_symbol"].split(".")[-1] in lean
    assert row["coq_symbol"] in coq
    assert row["parity_status"] == "PATCH_READY_CI_PENDING"
for code in [
 "REACTIVATION_TOKEN_ID_REUSED", "LIVE_RESIDUAL_OBSTRUCTS_RAW_RELATIVE_V0",
 "LIVE_NONELIMINABLE_RESIDUAL_OBSTRUCTS_ROBUST_RELATIVE_V0", "ABSOLUTE_RELATIVE_FIREWALL",
 "APPROXIMATION_DOES_NOT_ENTAIL_V0_IDENTITY", "SAME_STATE_SELF_CERTIFICATION_FORBIDDEN"]:
    assert code in semantic
manifest=load("fixtures/manifest.json")
assert manifest["semantic_version"] == "FC-1-v1.1+phase3"
assert manifest["status"] == "PHASE3_T133_T138_PATCH_ORACLE_SET"
workflow=(ROOT/".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
for command in ["python scripts/verify_phase1_alignment.py","python scripts/verify_phase2_expansion.py","python scripts/verify_phase2_ci_closure.py","python scripts/verify_phase3_expansion.py","python scripts/verify_manifest.py","python scripts/verify_closure.py"]:
    assert command in workflow
assert 'version = "0.4.0.dev1"' in (ROOT/"pyproject.toml").read_text(encoding="utf-8")
assert '"implementation_version": "v0-osap-fc1/0.4.0.dev1"' in semantic
print("PASS: V0 OSAP v1.3.0 Phase 3 T133-T138 build patch verified statically.")
