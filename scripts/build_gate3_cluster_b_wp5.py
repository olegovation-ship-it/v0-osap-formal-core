#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
BASELINE='7b497f197652874164e00fe9c0ef7f67e760c979'; DATE='2026-07-23'
EVIDENCE_INPUT_PATHS=['docs/gate3/cluster_b/BASELINE_AUDIT_AND_BUILD_SPECIFICATION_v0.1.md', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP0_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP1_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_SEMANTICS_PROFILE.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP2_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_ADAPTER_BINDING_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_EXTENSION_RULE_REGISTRY_T157_T162.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP3_POST_MERGE_SHA256SUMS.txt', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_DUAL_BACKEND_PROOF_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_STATEMENT_PARITY_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_FROZEN_UPSTREAM_PRESERVATION_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP4_POST_MERGE_SHA256SUMS.txt']
SCHEMA_PAIRS=[('release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_baseline_lock.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_ci_job_matrix.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_input_manifest.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_fixture_manifest.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_preservation_firewall.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_replay_record.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_acceptance_gates.schema.json'), ('release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json')]
IMPLEMENTATION_PATHS=['.github/workflows/gate3-cluster-b-wp5.yml', 'docs/gate3/cluster_b/WP5_BUILD_SPECIFICATION.md', 'docs/gate3/cluster_b/WP5_CI_INTEGRATION_AND_DETERMINISTIC_EVIDENCE_MANIFESTS.md', 'fixtures/gate3/cluster_b/wp5/01_valid_canonical_evidence.json', 'fixtures/gate3/cluster_b/wp5/02_unordered_evidence_paths_rejected.json', 'fixtures/gate3/cluster_b/wp5/03_duplicate_evidence_path_rejected.json', 'fixtures/gate3/cluster_b/wp5/04_sha256_mismatch_rejected.json', 'fixtures/gate3/cluster_b/wp5/05_predecessor_chain_break_rejected.json', 'fixtures/gate3/cluster_b/wp5/06_release_action_rejected.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_ACCEPTANCE_GATES.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BASELINE_LOCK.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_CI_JOB_MATRIX.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_PRESERVATION_FIREWALL.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json', 'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt', 'release/v1.4.0/tools/patch_wp5_allowlist.py', 'release/v1.4.0/tools/patch_wp5_build_spec_allowlist.py', 'schemas/v1.4.0/gate3_cluster_b_wp5_acceptance_gates.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_baseline_lock.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_build_plan.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_ci_job_matrix.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_fixture.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_evidence_input_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_fixture_manifest.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_preservation_firewall.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_replay_record.schema.json', 'schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json', 'scripts/build_gate3_cluster_b_wp5.py', 'scripts/replay_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5.py', 'scripts/verify_gate3_cluster_b_wp5_build_spec.py', 'tests/test_gate3_cluster_b_wp5.py', 'tests/test_gate3_cluster_b_wp5_build_spec.py']
def jd(o): return json.dumps(o,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
def canonical(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
def digest_bytes(b: bytes): return hashlib.sha256(b).hexdigest()
def digest_path(p: Path): return digest_bytes(p.read_bytes())
def run_bytes(*args: str) -> bytes:
    cp=subprocess.run(args,cwd=ROOT,capture_output=True,check=False)
    if cp.returncode: raise SystemExit(cp.stderr.decode('utf-8',errors='replace'))
    return cp.stdout
def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def build_fixture_manifest():
    rows=[]
    for rel in sorted(str(p.relative_to(ROOT)) for p in (ROOT/'fixtures/gate3/cluster_b/wp5').glob('*.json')):
        obj=load(rel); rows.append({'fixture_id':obj['fixture_id'],'path':rel,'sha256':digest_path(ROOT/rel),'expected_status':obj['expected_status']})
    return {'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST','version':'0.1','date':DATE,'fixture_count':len(rows),'fixtures':rows,'semantic_model_fixture_count_added':0}
def build_evidence():
    rows=[]
    for rel in sorted(EVIDENCE_INPUT_PATHS):
        hist=run_bytes('git','show',f'{BASELINE}:{rel}'); cur=(ROOT/rel).read_bytes()
        if hist!=cur: raise SystemExit('frozen evidence input changed: '+rel)
        rows.append({'path':rel,'sha256':digest_bytes(hist),'source_commit':BASELINE})
    obj={'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST','version':'0.1','date':DATE,'baseline_commit':BASELINE,'input_count':len(rows),'inputs':rows,'generation_state':'GENERATED_AND_LOCKED','canonical_sha256':None}
    cp=json.loads(json.dumps(obj)); cp['canonical_sha256']=None; obj['canonical_sha256']=digest_bytes(canonical(cp)); return obj
def build_replay(evidence):
    plan=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_BUILD_PLAN.json')
    bundle={'baseline_commit':BASELINE,'evidence_inputs':evidence['inputs'],'ci_job_ids':[x['job_id'] for x in plan['ci_jobs']],'acceptance_gate_ids':plan['acceptance_gate_ids'],'theorem_ids':plan['inherited_cluster_theorem_ids']+plan['locked_extension_theorem_ids'],'semantic_role_ids':plan['semantic_role_ids'],'release_authorization':'NONE','wp6_decision':'NOT_PERFORMED'}
    b1=canonical(bundle); b2=canonical(json.loads(b1.decode('utf-8')))
    return {'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP5_REPLAY_RECORD','version':'0.1','date':DATE,'baseline_commit':BASELINE,'run_count':2,'serialization_profile':'V0_OSAP_CJ_1_SORTED_UTF8_COMPACT','run_1_sha256':digest_bytes(b1),'run_2_sha256':digest_bytes(b2),'bundle_size_bytes':len(b1),'byte_identical':b1==b2,'canonical_bundle_sha256':digest_bytes(b1),'generation_state':'GENERATED_AND_LOCKED'}
def build_schema_bundle():
    rows=[]
    for doc,sch in SCHEMA_PAIRS:
        rows.append({'document':doc,'document_sha256':digest_path(ROOT/doc),'schema':sch,'schema_sha256':digest_path(ROOT/sch)})
    return {'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST','version':'0.1','date':DATE,'pair_count':len(rows),'pairs':rows,'generation_state':'GENERATED_AND_LOCKED'}
def build_ledger():
    rows=[]
    for rel in IMPLEMENTATION_PATHS:
        if rel.endswith('GATE3_CLUSTER_B_WP5_SHA256SUMS.txt'): continue
        p=ROOT/rel
        if not p.is_file(): raise SystemExit('missing WP5 allowlist path '+rel)
        rows.append(digest_path(p)+'  '+rel)
    return '\n'.join(rows)+'\n'
def validate_records():
    for doc,sch in SCHEMA_PAIRS:
        errs=sorted(Draft202012Validator(load(sch)).iter_errors(load(doc)),key=lambda e:list(e.path))
        if errs: raise SystemExit(f'schema failure {doc}: {errs[0].message}')
    fixture_schema=load('schemas/v1.4.0/gate3_cluster_b_wp5_evidence_fixture.schema.json')
    manifest=load('release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json')
    if manifest['fixture_count']!=6 or len(manifest['fixtures'])!=6: raise SystemExit('WP5 fixture cardinality mismatch')
    seen=set()
    for row in manifest['fixtures']:
        if row['path'] in seen: raise SystemExit('duplicate WP5 fixture path '+row['path'])
        seen.add(row['path'])
        fixture=load(row['path'])
        errs=sorted(Draft202012Validator(fixture_schema).iter_errors(fixture),key=lambda e:list(e.path))
        if errs: raise SystemExit('fixture schema failure '+row['path']+': '+errs[0].message)
        if fixture['fixture_id']!=row['fixture_id'] or fixture['expected_status']!=row['expected_status']: raise SystemExit('fixture manifest identity mismatch '+row['path'])
        if digest_path(ROOT/row['path'])!=row['sha256']: raise SystemExit('fixture manifest digest mismatch '+row['path'])
def expected_outputs():
    fixture=build_fixture_manifest()
    # fixture manifest must be written before its hash is used in the schema bundle
    return fixture
def generate():
    (ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json').write_text(jd(build_fixture_manifest()),encoding='utf-8')
    evidence=build_evidence(); (ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json').write_text(jd(evidence),encoding='utf-8')
    replay=build_replay(evidence); (ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json').write_text(jd(replay),encoding='utf-8')
    # First schema bundle uses all now-final documents except itself, whose hash would recurse. It records a null-self policy by excluding itself from pairs.
    pairs=[x for x in SCHEMA_PAIRS if not x[0].endswith('SCHEMA_BUNDLE_MANIFEST.json')]
    rows=[]
    for doc,sch in pairs: rows.append({'document':doc,'document_sha256':digest_path(ROOT/doc),'schema':sch,'schema_sha256':digest_path(ROOT/sch)})
    sb={'artifact_id':'V0_OSAP_GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST','version':'0.1','date':DATE,'pair_count':len(SCHEMA_PAIRS),'pairs':rows+[{'document':'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json','document_sha256':'SELF_EXCLUDED','schema':'schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json','schema_sha256':digest_path(ROOT/'schemas/v1.4.0/gate3_cluster_b_wp5_schema_bundle_manifest.schema.json')}],'generation_state':'GENERATED_AND_LOCKED'}
    (ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json').write_text(jd(sb),encoding='utf-8')
    (ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt').write_text(build_ledger(),encoding='utf-8')
def check():
    with tempfile.TemporaryDirectory() as td:
        # Capture current generated bytes, regenerate, and require exact stability.
        rels=['release/v1.4.0/GATE3_CLUSTER_B_WP5_FIXTURE_MANIFEST.json','release/v1.4.0/GATE3_CLUSTER_B_WP5_EVIDENCE_INPUT_MANIFEST.json','release/v1.4.0/GATE3_CLUSTER_B_WP5_REPLAY_RECORD.json','release/v1.4.0/GATE3_CLUSTER_B_WP5_SCHEMA_BUNDLE_MANIFEST.json','release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt']
        before={r:(ROOT/r).read_bytes() for r in rels}
        generate()
        after={r:(ROOT/r).read_bytes() for r in rels}
        if before!=after: raise SystemExit('WP5 generated artifacts are not canonical; run builder without --check')
    validate_records()
    ledger={}
    for line in (ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt').read_text().splitlines():
        h,r=line.split('  ',1); ledger[r]=h
    expected=set(IMPLEMENTATION_PATHS)-{'release/v1.4.0/GATE3_CLUSTER_B_WP5_SHA256SUMS.txt'}
    if set(ledger)!=expected: raise SystemExit('WP5 ledger path set mismatch')
    for rel,h in ledger.items():
        if digest_path(ROOT/rel)!=h: raise SystemExit('WP5 ledger digest mismatch '+rel)
def main():
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); a=p.parse_args()
    if a.check: check()
    else: generate(); validate_records()
    print('WP5 BUILD: PASS ('+('canonical check' if a.check else 'generated')+')')
    return 0
if __name__=='__main__': raise SystemExit(main())
