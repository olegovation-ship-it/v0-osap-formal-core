#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*a):
    cp=subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False); return {'returncode':cp.returncode,'stdout':cp.stdout.strip(),'stderr':cp.stderr.strip()}
def main():
    evidence={'artifact':'V0_OSAP_GATE3_CLUSTER_B_WP6_POST_MERGE_LIVE_EVIDENCE','branch':run('git','branch','--show-current'),'head':run('git','rev-parse','HEAD'),'origin_main':run('git','rev-parse','origin/main'),'origin_development':run('git','rev-parse','origin/v1.4.0-development'),'divergence':run('git','rev-list','--left-right','--count','origin/main...origin/v1.4.0-development'),'merge_and_parents':run('git','show','-s','--format=%H%n%P%n%s','f984b59cec832307bac7270c7d437a789bec99ce'),'worktree':run('git','status','--short')}
    print(json.dumps(evidence,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
