#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "e5724fc394b2fbb26d8926b5670b8fd41a62a71c"
CANONICAL_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt"
POST_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_POST_MERGE_SHA256SUMS.txt"
REPAIR_LEDGER = ROOT / "release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SHA256SUMS.txt"
HELPER = ROOT / "scripts/synchronize_v1_4_0_development_wp5.sh"
PAIRS = [('release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture_manifest.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_ACCEPTANCE_GATES.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_acceptance_gates.schema.json')]
FIXTURES = ['fixtures/gate3/cluster_b/wp5_sync_helper_repair/00_identical_0_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/01_main_ahead_1_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/02_main_ahead_2_0.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/03_development_ahead_0_1_rejected.json', 'fixtures/gate3/cluster_b/wp5_sync_helper_repair/04_diverged_1_1_rejected.json']
FIXTURE_SCHEMA = "schemas/v1.4.0/gate3_cluster_b_wp5_sync_helper_repair_fixture.schema.json"
ORIGINAL_HELPER_SHA256 = "6941160612adf4749c52608a9d9beb2e171effb8e678f37e5ee3ee3be81a7287"

def run(*args: str, check: bool = True, text: bool = True):
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=text, check=False)
    if check and cp.returncode:
        err = cp.stderr if text else cp.stderr.decode("utf-8", errors="replace")
        raise RuntimeError("$ " + " ".join(args) + "\n" + cp.stdout + err)
    return cp

def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ledger(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            sha256, rel = line.split("  ", 1)
            out[rel] = sha256
    return out

def main() -> int:
    errors = []
    try:
        if CANONICAL_LEDGER.read_bytes() != run("git", "show", BASELINE + ":" + str(CANONICAL_LEDGER.relative_to(ROOT)), text=False).stdout:
            errors.append("canonical WP5 ledger changed")
        if POST_LEDGER.read_bytes() != run("git", "show", BASELINE + ":" + str(POST_LEDGER.relative_to(ROOT)), text=False).stdout:
            errors.append("WP5 post-merge ledger changed")
    except Exception as exc:
        errors.append("frozen-ledger comparison failed: " + str(exc))

    for document, schema in PAIRS:
        try:
            Draft202012Validator(load(schema)).validate(load(document))
        except Exception as exc:
            errors.append("schema failure " + document + ": " + str(exc))
    fixture_schema = load(FIXTURE_SCHEMA)
    for fixture in FIXTURES:
        try:
            Draft202012Validator(fixture_schema).validate(load(fixture))
        except Exception as exc:
            errors.append("fixture schema failure " + fixture + ": " + str(exc))

    manifest = load("release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_FIXTURE_MANIFEST.json")
    if manifest["fixture_count"] != 5:
        errors.append("fixture count mismatch")
    for row in manifest["fixtures"]:
        if digest(ROOT / row["path"]) != row["sha256"]:
            errors.append("fixture digest mismatch " + row["path"])

    bundle = load("release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_SCHEMA_BUNDLE_MANIFEST.json")
    for row in bundle["pairs"]:
        if digest(ROOT / row["document"]) != row["document_sha256"]:
            errors.append("schema-bundle document mismatch " + row["document"])
        if digest(ROOT / row["schema"]) != row["schema_sha256"]:
            errors.append("schema-bundle schema mismatch " + row["schema"])

    record = load("release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_RECORD.json")
    if record["defect"]["original_helper_sha256"] != ORIGINAL_HELPER_SHA256:
        errors.append("original helper hash record mismatch")
    if record["repair"]["generalized_helper_sha256"] != digest(HELPER):
        errors.append("generalized helper hash mismatch")
    if record["release_actions_authorized"] or record["wp6_authorized"] or record["gate3_decision_authorized"]:
        errors.append("authorization firewall failure")

    gates = load("release/v1.4.0/GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR_ACCEPTANCE_GATES.json")
    if gates["gate_count"] != 18 or any(row["status"] != "PASS" for row in gates["gates"]):
        errors.append("repair acceptance gates failure")

    helper_text = HELPER.read_text(encoding="utf-8")
    for token in ("git merge-base --is-ancestor","git merge --ff-only origin/main","git push origin v1.4.0-development","classify_v1_4_0_development_sync_relation_wp5.py"):
        if token not in helper_text:
            errors.append("helper safety token missing: " + token)
    for token in ("--force","force-with-lease","reset --hard","git rebase","branch -D"):
        if token in helper_text:
            errors.append("forbidden helper token present: " + token)

    try:
        run("python","scripts/build_gate3_cluster_b_wp5_sync_helper_repair.py","--check")
        run("python","release/v1.4.0/tools/patch_wp5_sync_helper_repair_allowlist.py")
        run("python","scripts/replay_gate3_cluster_b_wp5_sync_helper_repair.py")
        run("python","scripts/build_gate3_cluster_b_wp5.py","--check")
        run("python","scripts/verify_gate3_cluster_b_wp5.py")
        run("python","scripts/build_gate3_cluster_b_wp5_post_merge_closeout.py","--check")
        run("python","scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py","--package-only")
    except Exception as exc:
        errors.append("replay/predecessor verification failure: " + str(exc))

    for rel, sha256 in ledger(REPAIR_LEDGER).items():
        if not (ROOT / rel).is_file() or digest(ROOT / rel) != sha256:
            errors.append("repair ledger mismatch " + rel)

    result = {"artifact":"V0_OSAP_GATE3_CLUSTER_B_WP5_SYNC_HELPER_REPAIR","baseline_commit":BASELINE,"changed_path_count":27,"errors":errors,"force_push_authorized":False,"release_actions_authorized":False,"status":"PASS" if not errors else "FAIL","wp6_authorized":False,"gate3_decision_authorized":False}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
