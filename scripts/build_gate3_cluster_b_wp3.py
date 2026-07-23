#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CANONICAL_LEDGER=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_SHA256SUMS.txt'
SUCCESSOR_LEDGER=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt'
EXACT={'.github/workflows/gate3-cluster-b-wp3.yml','checker/v0_osap_fc1/cluster_b_wp3.py','scripts/build_gate3_cluster_b_wp3.py','scripts/verify_gate3_cluster_b_wp3.py','tests/test_gate3_cluster_b_wp3.py'}
PREFIX=('docs/gate3/cluster_b/WP3_','fixtures/gate3/cluster_b/wp3/','release/v1.4.0/GATE3_CLUSTER_B_WP3_','schemas/v1.4.0/gate3_cluster_b_wp3_')
POST_MERGE_EXACT={'.github/workflows/gate3-cluster-b-wp3-post-merge-closeout.yml', 'tests/test_gate3_cluster_b_wp3_post_merge_closeout.py', 'release/v1.4.0/tools/patch_wp3_post_merge_allowlist.py', 'scripts/capture_gate3_cluster_b_wp3_post_merge_evidence.py', 'scripts/synchronize_v1_4_0_development_wp3.sh', 'scripts/verify_gate3_cluster_b_wp3_post_merge_closeout.py', 'scripts/build_gate3_cluster_b_wp3_post_merge_closeout.py'}
MARKER='WP3_POST_MERGE_SUCCESSOR_LEDGER_COMPATIBILITY_V0_1'
def owned(rel): return rel in EXACT or any(rel.startswith(p) for p in PREFIX)
def post_merge(rel):
 return rel in POST_MERGE_EXACT or 'WP3_POST_MERGE_' in rel or 'WP3_DEVELOPMENT_BRANCH_SYNCHRONIZATION_' in rel or 'gate3_cluster_b_wp3_post_merge_' in rel or 'gate3_cluster_b_wp3_development_branch_synchronization_' in rel
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def files():
 return sorted([p for p in ROOT.rglob('*') if p.is_file() and p not in {CANONICAL_LEDGER,SUCCESSOR_LEDGER} and owned(p.relative_to(ROOT).as_posix()) and not post_merge(p.relative_to(ROOT).as_posix())],key=lambda p:p.relative_to(ROOT).as_posix())
def expected(): return ''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files())
def canonical(p):
 x=json.loads(p.read_text(encoding='utf-8')); return p.read_text(encoding='utf-8')==json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
def parse(value):
 out={}
 for line in value.splitlines():
  if line.strip() and not line.lstrip().startswith('#'):
   d,r=line.split('  ',1); out[r]=d
 return out
def compatibility_errors(value):
 if not CANONICAL_LEDGER.is_file(): return ['missing canonical WP3 SHA-256 ledger']
 historical_text=CANONICAL_LEDGER.read_text(encoding='utf-8')
 if historical_text==value: return []
 if not SUCCESSOR_LEDGER.is_file(): return ['canonical WP3 ledger differs and successor ledger is missing']
 historical,current,successor=parse(historical_text),parse(value),parse(SUCCESSOR_LEDGER.read_text(encoding='utf-8'))
 errors=[]
 for rel,old in historical.items():
  now=current.get(rel)
  if now is None: errors.append('canonical WP3 path disappeared: '+rel)
  elif now!=old and successor.get(rel)!=now: errors.append('successor ledger does not attest changed WP3 path: '+rel)
 for rel,now in current.items():
  if rel not in historical and successor.get(rel)!=now: errors.append('successor ledger does not attest new canonical WP3 path: '+rel)
 return errors
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args()
 bad=[p for p in files() if p.suffix=='.json' and not canonical(p)]
 if bad: raise SystemExit('non-canonical JSON: '+','.join(str(p.relative_to(ROOT)) for p in bad))
 e=expected(); errors=[]
 if a.check: errors=compatibility_errors(e)
 elif not SUCCESSOR_LEDGER.is_file(): CANONICAL_LEDGER.write_text(e,encoding='utf-8',newline='\n')
 else: errors=compatibility_errors(e)
 if errors: raise SystemExit('; '.join(errors))
 print(f'WP3 BUILD {"CHECK" if a.check else "WRITE"}: PASS ({len(files())} canonical files; successor-compatible)')
 return 0
if __name__=='__main__': raise SystemExit(main())
