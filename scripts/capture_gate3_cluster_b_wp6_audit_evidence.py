#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*a):
 cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False)
 if cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
 return cp.stdout
if __name__=='__main__':
 run(sys.executable,'scripts/build_gate3_cluster_b_wp6.py','--check')
 run(sys.executable,'scripts/replay_gate3_cluster_b_wp6.py','--check')
 run(sys.executable,'scripts/verify_gate3_cluster_b_wp6.py','--job','full')
 print(json.dumps({'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP6_AUDIT_CAPTURE','status':'PASS','gate3_closed':False,'release_authorized':False},sort_keys=True,indent=2))
