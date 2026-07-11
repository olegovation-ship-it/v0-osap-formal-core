from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOI = "10.5281/zenodo.21306969"
DOI_URL = "https://doi.org/" + DOI
REPOSITORY = "https://github.com/olegovation-ship-it/v0-osap-formal-core"
RELEASE = REPOSITORY + "/releases/tag/v1.2.0"

manifest = json.loads((ROOT / "release" / "bootstrap_manifest.json").read_text(encoding="utf-8"))
versions = json.loads((ROOT / "release" / "compiler_versions.json").read_text(encoding="utf-8"))
readme = (ROOT / "README.md").read_text(encoding="utf-8")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
release_notes = (ROOT / "release" / "RELEASE_NOTES_v1.2.0.md").read_text(encoding="utf-8")
theorems = (ROOT / "docs" / "theorem_register.md").read_text(encoding="utf-8")

assert manifest["semantic_version"] == "v1.2.0"
assert manifest["status"] == "DUAL_BACKEND_ACCEPTED"
assert re.fullmatch(r"[0-9a-f]{40}", manifest["git_commit"])
assert "pending" not in manifest["lean_version"].lower()
assert "pending" not in manifest["coq_version"].lower()

assert versions["ci_status"] == {
    "coq": "PASS",
    "lean4": "PASS",
    "python_checker": "PASS",
    "release_readiness": "PASS",
    "schema_validation": "PASS",
}

assert "DUAL-BACKEND COMPILER-PASSED" in readme
assert DOI in readme
assert DOI_URL in readme
assert RELEASE in readme
assert "DOI: pending" not in readme

assert "## [1.2.0]" in changelog
assert DOI in changelog

assert 'version: "1.2.0"' in citation
assert f'doi: "{DOI}"' in citation
assert f'repository-code: "{REPOSITORY}"' in citation
assert f'repository-artifact: "{RELEASE}"' in citation

assert DOI in release_notes
assert RELEASE in release_notes
assert "Zenodo DOI: pending" not in release_notes

for theorem_id in range(121, 127):
    assert f"T{theorem_id}" in theorems

assert theorems.count("compiled") >= 12
print("PASS: v1.2.0 compiler-passed closure and DOI citation metadata verified.")
