import argparse,subprocess
from pathlib import Path
from v1_3_0_final_release_authorization_lib import *
ROOT=Path(__file__).resolve().parents[1]; MSG=ROOT/'release/v1.3.0/V1_3_0_STABLE_TAG_ANNOTATED_MESSAGE.txt'
p=argparse.ArgumentParser(); p.add_argument('--execute',action='store_true'); p.add_argument('--push',action='store_true'); p.add_argument('--confirm-target',default=''); a=p.parse_args()
assert_target_is_ancestor()
if tag_exists(FINAL_TAG) or remote_tag_exists(FINAL_TAG): raise SystemExit(f'ERROR: {FINAL_TAG} already exists locally or remotely')
cmd=['git','tag','-a',FINAL_TAG,FINAL_TARGET,'-F',str(MSG)]
print('Authorized command:'); print(' '.join(cmd)); print(f'Optional push command: git push origin refs/tags/{FINAL_TAG}'); print(f'Required explicit target confirmation: {FINAL_TARGET}')
if not a.execute: print('DRY RUN: no tag was created.'); raise SystemExit(0)
if a.confirm_target!=FINAL_TARGET: raise SystemExit('ERROR: --execute requires --confirm-target with the full authorized SHA')
assert_clean_worktree(); subprocess.run(cmd,check=True)
if a.push: subprocess.run(['git','push','origin',f'refs/tags/{FINAL_TAG}'],check=True)
print(f'PASS: annotated tag {FINAL_TAG} created at exact target {FINAL_TARGET}.')
