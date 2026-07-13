from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

REPOSITORY='olegovation-ship-it/v0-osap-formal-core'; FINAL_TARGET='13bf095688bcabd5b090f188e9bd28a16237edeb'; FINAL_TAG='v1.3.0'
RC1_TAG='v1.3.0-rc1'; RC1_TARGET='cf9a05b46b9b6f29cd85942f99155f89a49817a7'; IMMUTABLE_TAG='v1.2.0'
IMMUTABLE_TARGET='befa094ca3db4d5f28f5dcfbfdc4ed8a745972f3'; IMMUTABLE_DOI='10.5281/zenodo.21306969'; EXPECTED_STATE='FINAL_RELEASE_AUTHORIZED / STABLE_TAG_NOT_CREATED / FINAL_GITHUB_RELEASE_NOT_CREATED / ZENODO_NOT_PUBLISHED'

def run(*args,check=True): return subprocess.run(args,check=check,text=True,capture_output=True)
def git(*args,check=True): return run('git',*args,check=check).stdout.strip()
def sha256_file(path:Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def load_json(path:Path): return json.loads(path.read_text(encoding='utf-8'))
def dump_json(path:Path,value): path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def tag_target(tag): return git('rev-list','-n','1',tag)
def tag_exists(tag): return bool(git('tag','--list',tag))
def remote_tag_exists(tag):
    r=run('git','ls-remote','--tags','origin',f'refs/tags/{tag}',check=False)
    return r.returncode==0 and bool(r.stdout.strip())
def assert_clean_worktree():
    if git('status','--porcelain'): raise SystemExit('ERROR: worktree is not clean')
def assert_target_is_ancestor(target=FINAL_TARGET):
    if run('git','merge-base','--is-ancestor',target,'HEAD',check=False).returncode!=0:
        raise SystemExit(f'ERROR: authorized target {target} is not an ancestor of HEAD')
def assert_file_contains(path:Path,needles):
    text=path.read_text(encoding='utf-8')
    for needle in needles:
        if needle not in text: raise AssertionError(f'{path} missing required text: {needle}')
