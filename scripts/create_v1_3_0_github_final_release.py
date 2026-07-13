import argparse,subprocess
from pathlib import Path
from v1_3_0_final_release_authorization_lib import *
ROOT=Path(__file__).resolve().parents[1]; NOTES=ROOT/'release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_NOTES.md'; TITLE='V0 OSAP v1.3.0 — Stable Release'
p=argparse.ArgumentParser(); p.add_argument('--execute',action='store_true'); p.add_argument('--confirm-tag',default=''); a=p.parse_args()
if not tag_exists(FINAL_TAG): raise SystemExit(f'ERROR: local annotated tag {FINAL_TAG} is missing')
if tag_target(FINAL_TAG)!=FINAL_TARGET: raise SystemExit('ERROR: local stable tag target mismatch')
if not remote_tag_exists(FINAL_TAG): raise SystemExit(f'ERROR: remote tag {FINAL_TAG} is missing')
cmd=['gh','release','create',FINAL_TAG,'--repo',REPOSITORY,'--title',TITLE,'--notes-file',str(NOTES),'--verify-tag','--latest']
print('Authorized command:'); print(' '.join(cmd)); print(f'Required explicit tag confirmation: {FINAL_TAG}')
if not a.execute: print('DRY RUN: no GitHub final release was created.'); raise SystemExit(0)
if a.confirm_tag!=FINAL_TAG: raise SystemExit(f'ERROR: --execute requires --confirm-tag {FINAL_TAG}')
subprocess.run(cmd,check=True); print(f'PASS: GitHub final release created for {FINAL_TAG}.')
