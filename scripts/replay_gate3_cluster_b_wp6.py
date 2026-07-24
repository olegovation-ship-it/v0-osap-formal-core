#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*a):
 cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False)
 if cp.returncode: raise SystemExit(cp.stdout+cp.stderr)
 return cp
if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); x=ap.parse_args()
 run(sys.executable,'scripts/build_gate3_cluster_b_wp6.py','--check')
 r=json.loads((ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP6_REPLAY_RECORD.json').read_text())
 if not r['byte_identical'] or r['run_1_sha256']!=r['run_2_sha256']: raise SystemExit('WP6 replay is not byte-identical')
 print('WP6 TWO-RUN REPLAY: PASS')
