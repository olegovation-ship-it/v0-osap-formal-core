from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SNAPSHOT="7b38ddd6cb9bcfdc7c5713ba73a2c45d6513fbb8"
REL="release/v1.3.0/V1_3_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json"
def blob(rel): return subprocess.run(["git","show",f"{SNAPSHOT}:{rel}"],cwd=ROOT,check=True,capture_output=True).stdout
def main():
    current=(ROOT/REL).read_bytes(); historical=blob(REL)
    assert current==historical
    m=json.loads(current)
    assert m["state"].endswith("ZENODO_NOT_PUBLISHED")
    assert m["release_actions"]["zenodo_version_created"] is False
    assert "10.5281/zenodo.21346728" not in json.dumps(m,sort_keys=True)
    assert "10.5281/zenodo.21346728" in (ROOT/"CITATION.cff").read_text()
    print("PASS: current Zenodo lifecycle and frozen pre-Zenodo evidence coexist without mutation.")
    return 0
if __name__=="__main__": raise SystemExit(main())
