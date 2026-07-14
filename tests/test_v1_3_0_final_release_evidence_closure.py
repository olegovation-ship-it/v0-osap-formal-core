import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "release/v1.3.0/V1_3_0_GITHUB_FINAL_RELEASE_EVIDENCE.json"
RECORD = ROOT / "release/v1.3.0/V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_RECORD.json"
MANIFEST = ROOT / "release/v1.3.0/V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json"

def test_final_release_evidence_shape():
    value = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert value["stable_tag"]["tagName"] == "v1.3.0"
    assert value["stable_tag"]["isAnnotated"] is True
    assert value["stable_tag"]["peeledTargetCommit"] == (
        "13bf095688bcabd5b090f188e9bd28a16237edeb"
    )
    assert value["release"]["isDraft"] is False
    assert value["release"]["isPrerelease"] is False
    assert value["release"]["isLatest"] is True

def test_closure_record_preserves_zenodo_boundary():
    value = json.loads(RECORD.read_text(encoding="utf-8"))
    assert value["release_actions"]["stable_tag_created"] is True
    assert value["release_actions"]["github_final_release_created"] is True
    assert value["release_actions"]["zenodo_version_authorized"] is False
    assert value["release_actions"]["zenodo_version_created"] is False
    assert value["release_actions"]["doi_changed"] is False
    assert value["immutable_history"]["doi"] == "10.5281/zenodo.21306969"

def test_manifest_tracks_closure_files():
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert value["state"].startswith("FINAL_RELEASE_EVIDENCE_CLOSED")
    assert len(value["files"]) == 22

def test_workflows_are_validation_only():
    for rel in (
        ".github/workflows/v1-3-0-final-release-authorization.yml",
        ".github/workflows/v1-3-0-final-release-evidence-closure.yml",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "gh release create" not in text
        assert "git tag -a" not in text
        assert "--execute" not in text
        assert "fetch-depth: 0" in text

def test_component_and_conditional_boundary():
    assert 'version = "0.7.0.dev1"' in (
        ROOT / "pyproject.toml"
    ).read_text(encoding="utf-8")
    status = (ROOT / "docs/status_and_nonclaims.md").read_text(encoding="utf-8")
    assert all(item in status for item in ("T140", "T150", "T156"))
