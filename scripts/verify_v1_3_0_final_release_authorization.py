from __future__ import annotations
import argparse
from pathlib import Path
from v1_3_0_final_release_authorization_lib import *
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('--require-tags',action='store_true'); p.add_argument('--allow-stable-tag-created',action='store_true'); a=p.parse_args()
record=load_json(ROOT/'release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_RECORD.json')
manifest=load_json(ROOT/'release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_MANIFEST.json')
meta=load_json(ROOT/'release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_METADATA.json')
assert record['human_state']==EXPECTED_STATE
assert record['stable_target']['tag_name']==FINAL_TAG and record['stable_target']['target_commit']==FINAL_TARGET
assert record['release_actions']['stable_tag_target_authorized'] is True
assert record['release_actions']['stable_tag_created'] is False
assert record['release_actions']['github_final_release_authorized'] is True
assert record['release_actions']['github_final_release_created'] is False
assert record['release_actions']['zenodo_version_authorized'] is False
assert record['candidate_scope']['conditional_theorems']==['T140','T150','T156']
assert record['candidate_scope']['checker_component_version']=='0.7.0.dev1'
rc1sha=sha256_file(ROOT/'release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json')
assert record['authorization_basis']['frozen_rc1_evidence_manifest_sha256']==rc1sha
assert manifest['frozen_rc1_evidence_manifest_sha256']==rc1sha
for rel,expected in manifest['files'].items(): assert sha256_file(ROOT/rel)==expected,rel
assert meta['tagName']==FINAL_TAG and meta['targetCommit']==FINAL_TARGET
assert meta['isDraft'] is False and meta['isPrerelease'] is False and meta['makeLatest'] is True
assert_target_is_ancestor()
if a.require_tags:
    assert tag_exists(RC1_TAG) and tag_target(RC1_TAG)==RC1_TARGET
    assert tag_exists(IMMUTABLE_TAG) and tag_target(IMMUTABLE_TAG)==IMMUTABLE_TARGET
exists=tag_exists(FINAL_TAG)
if a.allow_stable_tag_created:
    if exists: assert tag_target(FINAL_TAG)==FINAL_TARGET
else: assert not exists,f'{FINAL_TAG} already exists'
assert_file_contains(ROOT/'README.md',['FINAL_RELEASE_AUTHORIZED',FINAL_TARGET,FINAL_TAG,'0.7.0.dev1','Zenodo'])
assert_file_contains(ROOT/'docs/status_and_nonclaims.md',[EXPECTED_STATE,FINAL_TARGET,'T140','T150','T156'])
assert 'version = "0.7.0.dev1"' in (ROOT/'pyproject.toml').read_text()
workflow=(ROOT/'.github/workflows/v1-3-0-final-release-authorization.yml').read_text()
for bad in ('git tag ','gh release create','--execute'): assert bad not in workflow,bad
tag_script=(ROOT/'scripts/create_v1_3_0_annotated_tag.py').read_text(); rel_script=(ROOT/'scripts/create_v1_3_0_github_final_release.py').read_text()
assert '--execute' in tag_script and '--confirm-target' in tag_script
assert '--execute' in rel_script and '--confirm-tag' in rel_script and '--verify-tag' in rel_script and '--prerelease' not in rel_script
print('PASS: V0 OSAP v1.3.0 final-release authorization verified; stable tag and final GitHub Release remain uncreated.')
