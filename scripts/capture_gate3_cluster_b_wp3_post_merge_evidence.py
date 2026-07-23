#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_HOSTED_CI_EVIDENCE.json'
def canonical_sha(obj):
 cp=json.loads(json.dumps(obj)); cp['canonical_sha256']=None
 return hashlib.sha256(json.dumps(cp,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); ap.parse_args()
 obj=json.loads(PATH.read_text(encoding='utf-8'))
 errors=[]
 if obj.get('source_pr')!=25 or obj.get('source_head_sha')!='380b5a59dd9e68ad3c67e26c01ac01bdc9e11cfe' or obj.get('merge_commit')!='3a3100d88772f3613192db200918d392885a3961': errors.append('identity mismatch')
 if obj.get('check_summary')!={'success':29,'failure':0,'pending':0,'skipped':0,'total':29}: errors.append('check summary mismatch')
 if obj.get('canonical_sha256')!=canonical_sha(obj): errors.append('canonical evidence hash mismatch')
 if errors: raise SystemExit('; '.join(errors))
 print('WP3 POST-MERGE EVIDENCE CHECK: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
