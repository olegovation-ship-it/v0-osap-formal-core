#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt'
EXACT={'.github/workflows/gate3-cluster-b-wp3.yml','checker/v0_osap_fc1/cluster_b_wp3.py','scripts/build_gate3_cluster_b_wp3.py','scripts/verify_gate3_cluster_b_wp3.py','tests/test_gate3_cluster_b_wp3.py'}
PREFIX=('docs/gate3/cluster_b/WP3_','fixtures/gate3/cluster_b/wp3/','release/v1.4.0/GATE3_CLUSTER_B_WP3_','schemas/v1.4.0/gate3_cluster_b_wp3_')
def owned(rel): return rel in EXACT or any(rel.startswith(p) for p in PREFIX)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def files():
 return sorted([p for p in ROOT.rglob('*') if p.is_file() and p!=LEDGER and owned(p.relative_to(ROOT).as_posix())],key=lambda p:p.relative_to(ROOT).as_posix())
def expected(): return ''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files())
def canonical(p):
 x=json.loads(p.read_text(encoding='utf-8')); return p.read_text(encoding='utf-8')==json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args()
 bad=[p for p in files() if p.suffix=='.json' and not canonical(p)]
 if bad: raise SystemExit('non-canonical JSON: '+','.join(str(p.relative_to(ROOT)) for p in bad))
 e=expected()
 if a.check:
  if not LEDGER.is_file() or LEDGER.read_text(encoding='utf-8')!=e: raise SystemExit('WP3 SHA-256 ledger mismatch')
  print(f'WP3 BUILD CHECK: PASS ({len(files())} hashed files)')
 else:
  LEDGER.parent.mkdir(parents=True,exist_ok=True); LEDGER.write_text(e,encoding='utf-8',newline='\n'); print(f'WP3 LEDGER WRITTEN: {len(files())} files')
 return 0
if __name__=='__main__': raise SystemExit(main())
