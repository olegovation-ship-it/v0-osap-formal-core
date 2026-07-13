import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_exact_target():
 r=json.loads((ROOT/'release/v1.3.0/V1_3_0_FINAL_RELEASE_AUTHORIZATION_RECORD.json').read_text()); assert r['stable_target']['tag_name']=='v1.3.0'; assert r['stable_target']['target_commit']=='13bf095688bcabd5b090f188e9bd28a16237edeb'; assert r['release_actions']['stable_tag_created'] is False
def test_release_metadata():
 m=json.loads((ROOT/'release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_METADATA.json').read_text()); assert m['isDraft'] is False; assert m['isPrerelease'] is False; assert m['makeLatest'] is True
def test_dry_run_first():
 t=(ROOT/'scripts/create_v1_3_0_annotated_tag.py').read_text(); r=(ROOT/'scripts/create_v1_3_0_github_final_release.py').read_text(); assert 'DRY RUN: no tag was created.' in t and '--confirm-target' in t; assert 'DRY RUN: no GitHub final release was created.' in r and '--confirm-tag' in r
def test_workflow_validation_only():
 w=(ROOT/'.github/workflows/v1-3-0-final-release-authorization.yml').read_text(); assert 'git tag ' not in w; assert 'gh release create' not in w; assert '--execute' not in w
def test_component_version_preserved(): assert 'version = "0.7.0.dev1"' in (ROOT/'pyproject.toml').read_text()
