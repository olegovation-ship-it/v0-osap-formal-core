
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rc1_audit_lib import EXPECTED_IDS, audit_inventory

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release/v1.3.0"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


inventory = load(RELEASE / "RC1_THEOREM_INVENTORY.json")
diagnostics = audit_inventory(inventory)
if diagnostics:
    raise SystemExit(f"Inventory structural audit failed: {diagnostics}")

lean_sources = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "lean").rglob("*.lean"))
)
coq_sources = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "coq").rglob("*.v"))
)
fixture_sources = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "fixtures").rglob("*.json"))
)

record_evidence = []
errors = []
for record in inventory["records"]:
    theorem_id = record["theorem_id"]
    lean_symbol = record["lean_symbol"].split(".")[-1]
    coq_symbol = record["coq_symbol"]
    positive_fixture = record["positive_fixture"]
    countermodel_fixture = record["countermodel_fixture"]

    lean_found = lean_symbol in lean_sources
    coq_found = coq_symbol in coq_sources
    positive_found = bool(positive_fixture and positive_fixture in fixture_sources)
    countermodel_found = bool(
        countermodel_fixture
        and (
            countermodel_fixture in fixture_sources
            or (
                isinstance(countermodel_fixture, str)
                and countermodel_fixture.startswith(
                    ("not_applicable:", "not_available:")
                )
            )
        )
    )

    if not lean_found:
        errors.append(f"{theorem_id}: Lean symbol not found")
    if not coq_found:
        errors.append(f"{theorem_id}: Coq symbol not found")
    if not positive_found:
        errors.append(f"{theorem_id}: positive fixture ID not found")
    if not countermodel_found:
        errors.append(f"{theorem_id}: countermodel fixture ID not found")

    record_evidence.append({
        "theorem_id": theorem_id,
        "lean_symbol_found": lean_found,
        "coq_symbol_found": coq_found,
        "positive_fixture_found": positive_found,
        "countermodel_fixture_found": countermodel_found,
        "rc1_record_sha256": record["rc1_record_sha256"],
        "verdict": "PASS" if all([lean_found, coq_found, positive_found, countermodel_found]) else "FAIL",
    })

if [item["theorem_id"] for item in record_evidence] != EXPECTED_IDS:
    errors.append("Evidence order/coverage differs from T121-T156")

evidence = {
    "artifact_id": "V0_OSAP_V1_3_0_RC1_STRUCTURAL_RECORD_PARITY_EVIDENCE",
    "version": "0.1",
    "parity_kind": "STRUCTURAL_RECORD_PARITY",
    "theorem_range": "T121-T156",
    "record_count": len(record_evidence),
    "status": "PASS" if not errors else "FAIL",
    "records": record_evidence,
    "limitations": [
        "This is not proof-term identity.",
        "This is not unrestricted semantic equivalence.",
        "This is not checker completeness.",
        "Compilation and symbol presence are evidence only for the encoded statements.",
    ],
    "errors": errors,
}
evidence["evidence_sha256"] = hashlib.sha256(
    json.dumps(record_evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
).hexdigest()

(RELEASE / "RC1_STATEMENT_PARITY_EVIDENCE.json").write_text(
    json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

if errors:
    raise SystemExit("RC1 structural-record parity failed:\n- " + "\n- ".join(errors))

print("PASS: RC1 structural-record parity verified for T121-T156.")
