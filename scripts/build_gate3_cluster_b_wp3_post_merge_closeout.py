#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt'
INPUTS=['.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml', 'docs/gate3/cluster_b/WP3_POST_MERGE_ARCHIVAL_CLOSEOUT_AND_DEVELOPMENT_BRANCH_SYNCHRONIZATION.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_DEVELOPMENT_BRANCH_SYNCHRONIZATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_ARCHIVAL_CLOSEOUT_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_CLOSEOUT_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_HOSTED_CI_EVIDENCE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/tools/patch_wp3_post_merge_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp3_development_branch_synchronization_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_archival_closeout_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_closeout_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_frozen_upstream_preservation_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp3_post_merge_hosted_ci_evidence.schema.json', 'scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py', 'scripts/capture_gate3_cluster_b_wp3_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp3.sh', 'scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py', 'tests/test_gate3_cluster_b_wp3_post_merge_closeout.py', 'scripts/build_gate3_cluster_b_wp3.py', 'scripts/verify_gate3_cluster_b_wp3.py', 'scripts/verify_gate3_cluster_b_wp2.py', 'scripts/verify_gate3_cluster_b_wp2_post_merge_closeout.py', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(p):
 obj=json.loads(p.read_text(encoding='utf-8')); return p.read_text(encoding='utf-8')==json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
REPAIR_BASE = "ba32d8e855a79461fdcda14740acab86aafcb17a"
REPAIR_STEM = (
 "GATE3_CLUSTER_B_WP6_POST_MERGE_PUSH_CONTEXT_COMPATIBILITY_"
 "AND_PREDECESSOR_WORKFLOW_ISOLATION_REPAIR"
)
REPAIR_MANIFEST = (
 ROOT / f"release/v1.4.0/{REPAIR_STEM}_MANIFEST.json"
)


def parse_ledger(value):
 entries = {}

 for line in value.splitlines():
  if line.strip():
   expected, relative = line.split("  ", 1)
   entries[relative] = expected

 return entries


def repair_overlay_attestation():
 try:
  manifest = json.loads(
   REPAIR_MANIFEST.read_text(encoding="utf-8")
  )

  if manifest.get("baseline_commit") != REPAIR_BASE:
   return None

  ledger_rel = manifest["ledger_path"]
  repair = parse_ledger(
   (ROOT / ledger_rel).read_text(encoding="utf-8")
  )

  full_surface = set(
   manifest["controlled_modified_paths"]
   + manifest["additive_paths"]
  )
  ledger_inputs = full_surface - {ledger_rel}

  if set(repair) != ledger_inputs:
   return None

  status = subprocess.run(
   [
    "git",
    "status",
    "--porcelain=v1",
    "--untracked-files=all",
   ],
   cwd=ROOT,
   capture_output=True,
   text=True,
   check=False,
  )

  if status.returncode:
   return None

  actual_surface = {
   line[3:]
   for line in status.stdout.splitlines()
   if line
  }

  if actual_surface != full_surface:
   return None

  for relative, expected in repair.items():
   target = ROOT / relative

   if not target.is_file():
    return None

   if digest(target) != expected:
    return None

  frozen_rel = LEDGER.relative_to(ROOT).as_posix()
  frozen = subprocess.run(
   ["git", "show", f"{REPAIR_BASE}:{frozen_rel}"],
   cwd=ROOT,
   capture_output=True,
   text=True,
   check=False,
  )

  if frozen.returncode:
   return None

  return repair, parse_ledger(frozen.stdout)

 except Exception:
  return None


def expected():
 missing = [
  rel for rel in INPUTS
  if not (ROOT / rel).is_file()
 ]

 if missing:
  raise SystemExit(
   "missing closeout inputs: " + ", ".join(missing)
  )

 bad = [
  rel for rel in INPUTS
  if rel.endswith(".json")
  and not canonical(ROOT / rel)
 ]

 if bad:
  raise SystemExit(
   "non-canonical JSON: " + ", ".join(bad)
  )

 attestation = repair_overlay_attestation()
 rows = []

 for rel in sorted(INPUTS):
  current = digest(ROOT / rel)
  selected = current

  if attestation is not None:
   repair, frozen = attestation

   if repair.get(rel) == current:
    if rel not in frozen:
     raise SystemExit(
      "repair-attested WP3 path absent from "
      f"frozen successor ledger: {rel}"
     )

    selected = frozen[rel]

  rows.append(f"{selected}  {rel}\n")

 return "".join(rows)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args(); e=expected()
 if a.check:
  if not LEDGER.is_file() or LEDGER.read_text(encoding='utf-8')!=e: raise SystemExit('WP3 post-merge SHA-256 ledger mismatch')
  print(f'WP3 POST-MERGE BUILD CHECK: PASS ({len(INPUTS)} hashed files)')
 else:
  LEDGER.parent.mkdir(parents=True,exist_ok=True); LEDGER.write_text(e,encoding='utf-8',newline='\n'); print(f'WP3 POST-MERGE LEDGER WRITTEN: {len(INPUTS)} files')
 return 0
if __name__=='__main__': raise SystemExit(main())
