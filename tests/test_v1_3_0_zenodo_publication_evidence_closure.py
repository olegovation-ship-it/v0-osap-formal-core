from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE.json"
RECORD = ROOT / "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_RECORD.json"
MANIFEST = ROOT / "release/v1.3.0/V1_3_0_ZENODO_PUBLICATION_EVIDENCE_CLOSURE_MANIFEST.json"

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def test_zenodo_identity_is_exact() -> None:
    evidence = read_json(EVIDENCE)["zenodo_record"]
    assert evidence["record_id"] == 21346728
    assert evidence["doi"] == "10.5281/zenodo.21346728"
    assert evidence["title"] == "V0 OSAP Formal Core v1.3.0 — T121–T156 Stable Release"
    assert evidence["version_display"] == "v1.3.0"
    assert evidence["resource_type"] == "Software"
    assert evidence["access_right"] == "Open"

def test_stable_target_and_historical_version_are_separate() -> None:
    record = read_json(RECORD)
    assert record["stable_release"]["exact_peeled_target"] == (
        "13bf095688bcabd5b090f188e9bd28a16237edeb"
    )
    assert record["immutable_history"]["doi"] == "10.5281/zenodo.21306969"
    assert record["zenodo_publication"]["doi"] == "10.5281/zenodo.21346728"
    assert record["release_actions"]["historical_doi_mutated"] is False
    assert record["release_actions"]["stable_tag_moved"] is False

def test_citation_surface_targets_v1_3_0() -> None:
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert 'doi: "10.5281/zenodo.21346728"' in citation
    assert 'version: "1.3.0"' in citation
    assert "10.5281/zenodo.21346728" in readme
    assert "10.5281/zenodo.21306969" in readme

def test_manifest_and_screenshot_hashes_are_well_formed() -> None:
    manifest = read_json(MANIFEST)
    evidence = read_json(EVIDENCE)
    assert manifest["state"].startswith("ZENODO_PUBLICATION_EVIDENCE_CLOSED")
    assert len(manifest["files"]) >= 20
    for digest in evidence["screenshot_sha256"].values():
        assert len(digest) == 64
        int(digest, 16)
