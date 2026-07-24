#!/usr/bin/env python3
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSIFIER = ROOT / "scripts/classify_v1_4_0_development_sync_relation_wp5.py"
MANIFEST = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json"

def load_classifier():
    spec = importlib.util.spec_from_file_location("wp5_sync_classifier", CLASSIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load classifier")
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def replay_fixture(path: Path) -> dict:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    result = load_classifier().classify(fixture["main_ahead"], fixture["development_ahead"])
    actual = {"decision": result.decision, "action": result.action, "allowed": result.allowed, "diagnostic": result.diagnostic}
    expected = {"decision": fixture["expected_decision"], "action": fixture["expected_action"], "allowed": fixture["expected_allowed"], "diagnostic": fixture["expected_diagnostic"]}
    return {"fixture_id": fixture["fixture_id"], "status": "PASS" if actual == expected else "FAIL", "actual": actual, "expected": expected}

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture")
    a = p.parse_args()
    if a.fixture:
        paths = [ROOT / a.fixture]
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        paths = [ROOT / row["path"] for row in manifest["fixtures"]]
    results = [replay_fixture(path) for path in paths]
    out = {"artifact": "V0_OSAP_GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_REPLAY", "fixture_count": len(results), "results": results, "status": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
