#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLASSIFIER=ROOT/'scripts/classify_v1_4_0_development_sync_relation_wp6.py'
MANIFEST=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SYNC_FIXTURE_MANIFEST.json'
def load_classifier():
    spec=importlib.util.spec_from_file_location('wp6_post_merge_sync_classifier',CLASSIFIER)
    if spec is None or spec.loader is None: raise RuntimeError('unable to load classifier')
    mod=importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod); return mod
def replay_fixture(path:Path):
    f=json.loads(path.read_text(encoding='utf-8')); r=load_classifier().classify(f['main_ahead'],f['development_ahead'])
    actual={'decision':r.decision,'action':r.action,'allowed':r.allowed,'diagnostic':r.diagnostic}
    expected={'decision':f['expected_decision'],'action':f['expected_action'],'allowed':f['expected_allowed'],'diagnostic':f['expected_diagnostic']}
    return {'fixture_id':f['fixture_id'],'status':'PASS' if actual==expected else 'FAIL','actual':actual,'expected':expected}
def main():
    p=argparse.ArgumentParser(); p.add_argument('--fixture'); a=p.parse_args()
    if a.fixture: paths=[ROOT/a.fixture]
    else:
        m=json.loads(MANIFEST.read_text(encoding='utf-8')); paths=[ROOT/x['path'] for x in m['fixtures']]
    results=[replay_fixture(x) for x in paths]
    out={'artifact':'V0_OSAP_GATE3_CLUSTER_B_WP6_POST_MERGE_SYNC_REPLAY','fixture_count':len(results),'results':results,'status':'PASS' if all(x['status']=='PASS' for x in results) else 'FAIL'}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
