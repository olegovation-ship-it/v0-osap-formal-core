#!/usr/bin/env python3
"""Fail-closed verifier for v1.4.0 final GitHub Release evidence closure."""
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from pathlib import Path

BASE="75b84e5800686372fb6a19add12c8896f59274ee"
BASE_TREE="8ec377cadaeddfd6bef67dd01d981b83d09c327b"
BASE_PARENTS=["47614ce7891f4895e003cb85e7651b7d043a963d","aeeaeefa5d40bbb26ffe7c9ae02abc75b3636a5d"]
BASE_RELEASE_TREE="45aaeec48443924fa153ac343ab904bac814792f"
CITATION_BLOB="0adb7aaa73a052b8621c3f0d393f6f128cf4bada"
PYPROJECT_BLOB="8e2b30975f15d4147aabb7a50fe8bab3b9ea65a8"
STATE="FINAL_RELEASE_EVIDENCE_CLOSED / STABLE_TAG_CREATED / FINAL_GITHUB_RELEASE_CREATED / ZENODO_NOT_PUBLISHED"
WORKFLOW_SHA256="8cd76121c602b57dc44a080a0afcef5542450f295e807ee3165b53f20db84efe"
MANIFEST_PATH="release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json"
EXACT_SURFACE=['README.md', 'CHANGELOG.md', 'docs/status_and_nonclaims.md', 'artifacts/v1_4_0_github_final_release_evidence.json', 'release/v1.4.0/V1_4_0_GITHUB_FINAL_RELEASE_EVIDENCE.json', 'release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_RECORD.json', 'release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json', 'release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md', 'release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_ACCEPTANCE_GATES.md', 'scripts/build_v1_4_0_final_release_evidence_closure_manifest.py', 'scripts/verify_v1_4_0_final_release_evidence_closure.py', 'tests/test_v1_4_0_final_release_evidence_closure.py', '.github/workflows/v1-4-0-final-release-evidence-closure.yml']
NEW_RELEASE_PATHS={'release/v1.4.0/V1_4_0_GITHUB_FINAL_RELEASE_EVIDENCE.json', 'release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_RECORD.json', 'release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_AND_HISTORICAL_PRESERVATION_REPORT.md', 'release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_ACCEPTANCE_GATES.md', 'release/v1.4.0/V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_MANIFEST.json'}
BASELINE_MODIFIED={
"README.md":("77e00ab3a6de603769e8bd8603cf8b0bd3e8ee57",10923,"ac33412cb23ca1a44b1822ba343678076883582457e16e3597d8db6925b8447d"),
"CHANGELOG.md":("1be8f7cba66d507e69cb73a42e304e75d7e3eea0",9839,"dfa17a0ed02d0552295a1b4e3382e92cc8e70a18b158c2861525e8a70b60256c"),
"docs/status_and_nonclaims.md":("a8cf9f4806ce8155bf9735d4d58d01c207edbbe0",8901,"49cc49f733ac7d53787d3df2a7c606cc18e0872c48290c51583e526010092a1d")}
MARKERS={
"README.md":("<!-- V0_OSAP_V1_4_0_FINAL_RELEASE_EVIDENCE_BEGIN -->","<!-- V0_OSAP_V1_4_0_FINAL_RELEASE_EVIDENCE_END -->"),
"CHANGELOG.md":("<!-- V0_OSAP_V1_4_0_FINAL_RELEASE_EVIDENCE_CHANGELOG_BEGIN -->","<!-- V0_OSAP_V1_4_0_FINAL_RELEASE_EVIDENCE_CHANGELOG_END -->"),
"docs/status_and_nonclaims.md":("<!-- V0_OSAP_V1_4_0_FINAL_RELEASE_EVIDENCE_STATUS_BEGIN -->","<!-- V0_OSAP_V1_4_0_FINAL_RELEASE_EVIDENCE_STATUS_END -->")}
ALLOWED_ZENODO_DOIS={"10.5281/zenodo.21306969","10.5281/zenodo.21346728"}

def fail(reason):
    print("FINAL_RELEASE_EVIDENCE_CLOSURE_VERIFICATION=HOLD reason="+str(reason)); raise SystemExit(1)
def git(root,*args,check=True):
    cp=subprocess.run(["git","-C",str(root),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if check and cp.returncode: fail("GIT_COMMAND_FAILED_"+"_".join(args[:2]))
    return cp.stdout
def sha256(data): return hashlib.sha256(data).hexdigest()
def blob(data): return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
def basebytes(root,path): return git(root,"show",f"{BASE}:{path}")
def current_surface(root):
    tracked={x for x in git(root,"diff","--name-only","--no-renames",BASE,"--").decode().splitlines() if x}
    raw=git(root,"ls-files","--others","--exclude-standard","-z")
    return tracked|{x.decode() for x in raw.split(b"\0") if x}
def remove_block(cur,begin,end):
    bb=begin.encode(); ee=end.encode()
    if cur.count(bb)!=1 or cur.count(ee)!=1: fail("V1_4_MARKER_CARDINALITY")
    s=cur.index(bb); e=cur.index(ee,s)+len(ee)
    if cur[e:e+2]==b"\n\n": e+=2
    elif cur[e:e+1]==b"\n": e+=1
    return cur[:s]+cur[e:]

def verify_baseline(root):
    if git(root,"rev-parse",f"{BASE}^{{tree}}").decode().strip()!=BASE_TREE: fail("BASE_TREE")
    if git(root,"show","-s","--format=%P",BASE).decode().strip().split()!=BASE_PARENTS: fail("BASE_PARENTS")
    if git(root,"rev-parse",f"{BASE}:release/v1.4.0").decode().strip()!=BASE_RELEASE_TREE: fail("BASE_RELEASE_TREE")
    for path,(bsha,n,digest) in BASELINE_MODIFIED.items():
        if git(root,"rev-parse",f"{BASE}:{path}").decode().strip()!=bsha: fail("BASE_BLOB_"+path)
        d=basebytes(root,path)
        if len(d)!=n or sha256(d)!=digest: fail("BASE_BYTES_"+path)
    if git(root,"rev-parse",f"{BASE}:CITATION.cff").decode().strip()!=CITATION_BLOB: fail("BASE_CITATION")
    if git(root,"rev-parse",f"{BASE}:pyproject.toml").decode().strip()!=PYPROJECT_BLOB: fail("BASE_PYPROJECT")

def verify_historical(root):
    raw=git(root,"ls-tree","-r","-z",BASE,"--","release/v1.4.0")
    recs=[r for r in raw.split(b"\0") if r]
    if not recs: fail("HISTORICAL_INVENTORY_EMPTY")
    for rec in recs:
        meta,pathb=rec.split(b"\t",1); mode,typ,bsha=meta.decode().split(); path=pathb.decode()
        if typ!="blob": continue
        p=root/path
        if not p.is_file() or blob(p.read_bytes())!=bsha: fail("HISTORICAL_MUTATED_"+path)
    for path in NEW_RELEASE_PATHS:
        cp=subprocess.run(["git","-C",str(root),"cat-file","-e",f"{BASE}:{path}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if cp.returncode==0: fail("ADDITIVE_EXISTED_AT_BASE_"+path)

def verify_modified(root):
    inserted=[]
    for path,(begin,end) in MARKERS.items():
        cur=(root/path).read_bytes()
        if remove_block(cur,begin,end)!=basebytes(root,path): fail("HISTORICAL_BYTES_"+path)
        s=cur.index(begin.encode()); e=cur.index(end.encode(),s)+len(end.encode()); inserted.append(cur[s:e])
    oldline=next(x for x in basebytes(root,"README.md").splitlines() if b"zenodo.21346728" in x and b"badge/DOI" in x)
    if oldline not in (root/"README.md").read_bytes().splitlines(): fail("README_DOI_TARGET")
    return inserted

def verify_citation_component(root):
    c=(root/"CITATION.cff").read_bytes()
    if blob(c)!=CITATION_BLOB or b"10.5281/zenodo.21346728" not in c: fail("CITATION_MUTATED")
    p=(root/"pyproject.toml").read_bytes()
    if blob(p)!=PYPROJECT_BLOB: fail("PYPROJECT_MUTATED")
    t=p.decode()
    if 'name = "v0-osap-fc1"' not in t or 'version = "0.7.0.dev1"' not in t: fail("COMPONENT_VERSION")

def verify_evidence(root):
    a=json.loads((root/"artifacts/v1_4_0_github_final_release_evidence.json").read_text())
    b=json.loads((root/"release/v1.4.0/V1_4_0_GITHUB_FINAL_RELEASE_EVIDENCE.json").read_text())
    if a!=b: fail("EVIDENCE_DIVERGENCE")
    checks=[
      a["state"]==STATE,a["repository"]["canonical_merge_sha"]==BASE,a["repository"]["tree_sha1"]==BASE_TREE,
      a["pull_request"]["number"]==34 and a["pull_request"]["merged"] is True,
      a["formal_gate3_cluster_b_wp6"]["formally_closed"] is True and a["formal_gate3_cluster_b_wp6"]["final_verdict"]=="PASS",
      a["post_merge_hosted_ci"]["workflow_runs_total"]==29,a["post_merge_hosted_ci"]["workflow_runs_success"]==15,
      a["post_merge_hosted_ci"]["workflow_runs_skipped"]==14,a["post_merge_hosted_ci"]["workflow_runs_failure"]==0,
      a["post_merge_hosted_ci"]["check_runs_total"]==65,
      a["stable_tag"]["object_sha1"]=="21d9a42ceb9985dbcd6330582a8cb80e81d883c5",a["stable_tag"]["peeled_target"]==BASE,
      a["github_release"]["id"]==366706025,a["github_release"]["asset_count"]==4,
      a["github_release"]["body_sha256"]=="530711e7baa7408f51f53844c969020520a0c0bd5c100bfe29275867735623ba",
      a["component_version_boundary"]["embedded_checker_project_version"]=="0.7.0.dev1",
      a["publication_boundary"]["zenodo_v1_4_0_created"] is False,a["publication_boundary"]["v1_4_0_doi_finalized"] is False,
      a["publication_boundary"]["doi_mutation_performed"] is False,a["historical_preservation"]["baseline_release_v1_4_0_tree_sha1"]==BASE_RELEASE_TREE]
    if not all(checks): fail("EVIDENCE_FIELD_MISMATCH")

def verify_doi(root,inserted):
    material=list(inserted)+[(root/p).read_bytes() for p in EXACT_SURFACE[3:9]]
    seen=set()
    for d in material:
        seen.update(m.decode() for m in re.findall(rb"10\.5281/zenodo\.\d+",d))
    if not seen.issubset(ALLOWED_ZENODO_DOIS): fail("UNAUTHORIZED_DOI")
    for d in material:
        if b"ZENODO_V1_4_0_CREATED=YES" in d or b"V1_4_0_DOI_FINALIZED=YES" in d or b"DOI_MUTATION_PERFORMED=YES" in d: fail("PUBLICATION_FALSE_CLAIM")

def verify_workflow(root):
    d=(root/".github/workflows/v1-4-0-final-release-evidence-closure.yml").read_bytes()
    if sha256(d)!=WORKFLOW_SHA256: fail("WORKFLOW_BYTES")
    low=d.lower()
    for tok in [b"workflow_dispatch",b"contents: write",b"gh release",b"zenodo.org/api",b"upload-artifact",b"actions/upload-release-asset",b"softprops/action-gh-release"]:
        if tok in low: fail("WORKFLOW_MUTATION_TOKEN")
    if b"permissions:\n  contents: read\n" not in d: fail("WORKFLOW_PERMISSION")

def verify_manifest(root):
    cp=subprocess.run([sys.executable,str(root/"scripts/build_v1_4_0_final_release_evidence_closure_manifest.py"),"--check","--root",str(root)],
                      stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: fail("MANIFEST_CHECK")
    m=json.loads((root/MANIFEST_PATH).read_text())
    if (m["surface"]["modified_count"],m["surface"]["additive_count"],m["surface"]["total_count"])!=(3,10,13): fail("MANIFEST_COUNTS")
    if m["manifest_self_exclusion"]["path"]!=MANIFEST_PATH: fail("MANIFEST_SELF_EXCLUSION")

def main():
    root=Path(__file__).resolve().parents[1]
    verify_baseline(root)
    surf=current_surface(root)
    if surf!=set(EXACT_SURFACE): fail("EXACT_SURFACE_MISMATCH")
    verify_historical(root)
    inserted=verify_modified(root)
    verify_citation_component(root)
    verify_evidence(root)
    verify_doi(root,inserted)
    verify_workflow(root)
    verify_manifest(root)
    print("PHASE=READ_ONLY_V1_4_0_FINAL_RELEASE_EVIDENCE_CLOSURE_VERIFICATION")
    print("MODIFIED_COUNT=3\nADDITIVE_COUNT=10\nTOTAL_COUNT=13")
    print("HISTORICAL_RELEASE_V1_4_0_PRESERVATION=PASS")
    print("CITATION_CFF_PRESERVATION=PASS")
    print("COMPONENT_VERSION_BOUNDARY=PASS")
    print("ZENODO_V1_4_0_CREATED=NO\nV1_4_0_DOI_FINALIZED=NO\nDOI_MUTATION_PERFORMED=NO")
    print("WORKFLOW_MUTATION_SURFACE=NONE")
    print("FINAL_RELEASE_EVIDENCE_CLOSURE_VERIFICATION=PASS")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
