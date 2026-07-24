from pathlib import Path
import json, subprocess
ROOT=Path(__file__).resolve().parents[1]
def run(*a):
    return subprocess.run(a,cwd=ROOT,capture_output=True,text=True,check=False)
def test_wp5_post_merge_closeout():
    cp=run('python','scripts/verify_gate3_cluster_b_wp5_post_merge_closeout.py','--package-only')
    assert cp.returncode==0, cp.stdout+cp.stderr
    obj=json.loads(cp.stdout)
    assert obj['status']=='PASS'
    assert obj['release_actions_authorized'] is False
    assert obj['wp6_authorized'] is False
