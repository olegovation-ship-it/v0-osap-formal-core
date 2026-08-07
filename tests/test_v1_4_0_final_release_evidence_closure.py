from __future__ import annotations
import importlib.util, json, sys, hashlib, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader; sys.modules[name]=mod; spec.loader.exec_module(mod); return mod
builder=load("v140_builder",ROOT/"scripts/build_v1_4_0_final_release_evidence_closure_manifest.py")
verifier=load("v140_verifier",ROOT/"scripts/verify_v1_4_0_final_release_evidence_closure.py")
class FinalReleaseEvidenceClosureTests(unittest.TestCase):
    def test_exact_surface(self):
        self.assertEqual((len(builder.MODIFIED),len(builder.ADDITIVE),len(builder.EXACT_SURFACE)),(3,10,13))
        self.assertEqual(len(set(builder.EXACT_SURFACE)),13); self.assertEqual(builder.EXACT_SURFACE,verifier.EXACT_SURFACE)
    def test_manifest_self_exclusion_and_determinism(self):
        a=builder.render_manifest(ROOT); b=builder.render_manifest(ROOT); self.assertEqual(a,b)
        m=json.loads(a); self.assertEqual(m["manifest_self_exclusion"]["path"],builder.MANIFEST_PATH)
        self.assertEqual({x["path"] for x in m["files_excluding_self"]},set(builder.EXACT_SURFACE)-{builder.MANIFEST_PATH})
    def test_terminal_publication_and_component_boundaries(self):
        e=json.loads((ROOT/"artifacts/v1_4_0_github_final_release_evidence.json").read_text())
        self.assertEqual(e["state"],verifier.STATE)
        self.assertFalse(e["publication_boundary"]["zenodo_v1_4_0_created"])
        self.assertFalse(e["publication_boundary"]["v1_4_0_doi_finalized"])
        self.assertFalse(e["publication_boundary"]["doi_mutation_performed"])
        self.assertEqual(e["component_version_boundary"]["embedded_checker_project_version"],"0.7.0.dev1")
        self.assertTrue(e["component_version_boundary"]["version_namespaces_separate"])
    def test_workflow_frozen_and_read_only(self):
        d=(ROOT/".github/workflows/v1-4-0-final-release-evidence-closure.yml").read_bytes()
        self.assertEqual(hashlib.sha256(d).hexdigest(),verifier.WORKFLOW_SHA256)
        self.assertIn(b"permissions:\n  contents: read\n",d)
        low=d.lower()
        for tok in [b"workflow_dispatch",b"contents: write",b"gh release",b"zenodo.org/api",b"upload-artifact",b"actions/upload-release-asset",b"softprops/action-gh-release"]:
            self.assertNotIn(tok,low)
    def test_marker_cardinality(self):
        for path,(begin,end) in verifier.MARKERS.items():
            t=(ROOT/path).read_text(); self.assertEqual(t.count(begin),1); self.assertEqual(t.count(end),1)
    def test_verify_baseline_executes_literal_tree_revision(self):
        baseline={path:verifier.remove_block((ROOT/path).read_bytes(),begin,end) for path,(begin,end) in verifier.MARKERS.items()}
        calls=[]
        def fake_git(root,*args,check=True):
            self.assertEqual(Path(root),ROOT); calls.append(args)
            if args==("rev-parse",f"{verifier.BASE}^{{tree}}"): return (verifier.BASE_TREE+"\n").encode()
            if args==("show","-s","--format=%P",verifier.BASE): return (" ".join(verifier.BASE_PARENTS)+"\n").encode()
            if args==("rev-parse",f"{verifier.BASE}:release/v1.4.0"): return (verifier.BASE_RELEASE_TREE+"\n").encode()
            if len(args)==2 and args[0]=="rev-parse" and args[1].startswith(verifier.BASE+":"):
                path=args[1].split(":",1)[1]
                if path in verifier.BASELINE_MODIFIED: return (verifier.BASELINE_MODIFIED[path][0]+"\n").encode()
                if path=="CITATION.cff": return (verifier.CITATION_BLOB+"\n").encode()
                if path=="pyproject.toml": return (verifier.PYPROJECT_BLOB+"\n").encode()
            if len(args)==2 and args[0]=="show" and args[1].startswith(verifier.BASE+":"):
                path=args[1].split(":",1)[1]
                if path in baseline: return baseline[path]
            self.fail("unexpected git call: "+repr(args))
        with patch.object(verifier,"git",side_effect=fake_git): verifier.verify_baseline(ROOT)
        self.assertEqual(calls[0],("rev-parse",f"{verifier.BASE}^{{tree}}"))
        self.assertGreaterEqual(len(calls),10)
    def test_verify_doi_executes_claim_surface_and_rejects_false_claim(self):
        claim_paths=verifier.EXACT_SURFACE[3:9]
        self.assertEqual(len(claim_paths),6)
        self.assertNotIn("scripts/verify_v1_4_0_final_release_evidence_closure.py",claim_paths)
        self.assertNotIn("tests/test_v1_4_0_final_release_evidence_closure.py",claim_paths)
        inserted=[]
        for path,(begin,end) in verifier.MARKERS.items():
            cur=(ROOT/path).read_bytes(); bb=begin.encode(); ee=end.encode()
            start=cur.index(bb); finish=cur.index(ee,start)+len(ee); inserted.append(cur[start:finish])
        verifier.verify_doi(ROOT,inserted)
        with tempfile.TemporaryDirectory() as td:
            tmp=Path(td)
            for rel in claim_paths:
                target=tmp/rel; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes((ROOT/rel).read_bytes())
            injected=tmp/claim_paths[0]
            injected.write_bytes(injected.read_bytes()+b"\nZENODO_V1_4_0_CREATED=YES\n")
            with patch("builtins.print") as out:
                with self.assertRaises(SystemExit): verifier.verify_doi(tmp,inserted)
            out.assert_any_call("FINAL_RELEASE_EVIDENCE_CLOSURE_VERIFICATION=HOLD reason=PUBLICATION_FALSE_CLAIM")
if __name__=="__main__": unittest.main()
