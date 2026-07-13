from pathlib import Path
from v1_3_0_final_release_authorization_lib import *
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_MANIFEST.json'
FILES=['README.md','CHANGELOG.md','docs/status_and_nonclaims.md','pyproject.toml',
'release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json','release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_RECORD.json',
    "scripts/verify_rc1_gate_audit.py",
    "scripts/verify_rc1_release_evidence_closure.py",
    "tests/test_rc1_release_evidence_closure.py",
'release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_AND_STABLE_TAG_PREPARATION_SPECIFICATION.md',
'release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_GATES.md','release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_RECORD.json',
'release/v1.3.0/V1_3_0_STABLE_TAG_ANNOTATED_MESSAGE.txt','release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_NOTES.md',
'release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_METADATA.json','scripts/v1_3_0_final_release_authorization_lib.py',
'scripts/build_v1_3_0_final_release_authorization_manifest.py','scripts/verify_v1_3_0_final_release_authorization.py',
'scripts/create_v1_3_0_annotated_tag.py','scripts/create_v1_3_0_github_final_release.py',
    "release/v1.3.0/RC1_RELEASE_MANIFEST.json",
    "scripts/verify_rc1_release_closure.py",
    "scripts/verify_rc1_tag_authorization.py",
'tests/test_v1_3_0_final_release_authorization.py','.github/workflows/v1-3-0-final-release-authorization.yml']
missing=[x for x in FILES if not (ROOT/x).is_file()]
if missing: raise SystemExit('ERROR: missing manifest inputs: '+', '.join(missing))
manifest={'artifact_id':'V0_OSAP_V1_3_0_FINAL_RELEASE_AUTHORIZATION_MANIFEST','version':'0.1','date':'2026-07-13',
'state':'FINAL_RELEASE_AUTHORIZED_STABLE_TAG_NOT_CREATED_FINAL_GITHUB_RELEASE_NOT_CREATED_ZENODO_NOT_PUBLISHED',
'repository':REPOSITORY,'stable_tag':FINAL_TAG,'exact_authorized_target':FINAL_TARGET,'rc1_tag':RC1_TAG,'rc1_target':RC1_TARGET,
'immutable_history':{'tag':IMMUTABLE_TAG,'target_commit':IMMUTABLE_TARGET,'doi':IMMUTABLE_DOI},
'frozen_rc1_evidence_manifest_sha256':sha256_file(ROOT/'release/v1.3.0/RC1_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json'),
'files':{x:sha256_file(ROOT/x) for x in FILES},
'release_actions':{'stable_tag_target_authorized':True,'stable_tag_created':False,'github_final_release_authorized':True,'github_final_release_created':False,'zenodo_version_authorized':False,'zenodo_version_created':False,'doi_changed':False}}
dump_json(OUT,manifest)
print(f'PASS: final-release authorization manifest generated with {len(FILES)} hashed files.')
