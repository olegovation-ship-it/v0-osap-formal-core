#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ACCEPTED='1c16ffb529b7e9a43c16739de26ad185c2f4b74c'; MERGE='adda93cae34d6579e8b715d4107ff7f62a6f9c6b'
def run(*a):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False)
    if cp.returncode: raise SystemExit(cp.stderr)
    return cp.stdout.strip()
def main():
    data={'branch':run('git','branch','--show-current'),'local_head':run('git','rev-parse','HEAD'),
          'origin_main':run('git','rev-parse','origin/main'),'origin_development':run('git','rev-parse','origin/v1.4.0-development'),
          'divergence':run('git','rev-list','--left-right','--count','origin/main...origin/v1.4.0-development'),
          'expected_accepted':ACCEPTED,'expected_merge':MERGE,'working_tree_clean':not bool(run('git','status','--porcelain'))}
    print(json.dumps(data,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
