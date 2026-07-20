#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

BASE = "f79bc16da3a4aa53c1e0cbbbbb65f003fea42e15"
BASE_COMMIT_OBJECT = f"{BASE}^{{commit}}"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
TARGET_BRANCH = "v1.4.0-development"
RESERVED = {"T157", "T158", "T159", "T160", "T161", "T162"}
REGISTRY_PATH = "release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_REGISTRY_T157_T162.json"
CLOSED_WP0_RECORD_PREFIX = "release/v1.4.0/GATE3_CLUSTER_B_WP0_"

ALLOWED_FILES = {
    ".github/workflows/gate3-cluster-b-wp1.yml",
    "scripts/build_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp1.py",
    "tests/test_gate3_cluster_b_wp1.py",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0.py",
}
ALLOWED_DIRECTORIES = (
    "docs/gate3/cluster_b/",
    "release/v1.4.0/",
    "schemas/v1.4.0/",
)

PAIRS = [
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_BASELINE_LOCK.json", "schemas/v1.4.0/gate3_cluster_b_wp1_baseline_lock.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_THEOREM_ID_COLLISION_AUDIT.json", "schemas/v1.4.0/gate3_cluster_b_wp1_collision_audit.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_SEMANTIC_ROLE_MAP.json", "schemas/v1.4.0/gate3_cluster_b_wp1_semantic_role_map.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_CANONICAL_GLOSSARY.json", "schemas/v1.4.0/gate3_cluster_b_wp1_glossary.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_CANONICAL_CONTRACTS.json", "schemas/v1.4.0/gate3_cluster_b_wp1_contracts.schema.json"),
    (REGISTRY_PATH, "schemas/v1.4.0/gate3_cluster_b_wp1_theorem_registry.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_DEPENDENCY_DAG.json", "schemas/v1.4.0/gate3_cluster_b_wp1_dependency_dag.schema.json"),
    ("release/v1.4.0/GATE3_CLUSTER_B_WP1_ACCEPTANCE_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp1_acceptance_gates.schema.json"),
]


def run(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    p = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{p.stderr.strip()}")
    return p.stdout.strip()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def statement_hash(text: str) -> str:
    normalized = " ".join(text.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def iter_objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_objects(child)


def collision_scan(repo: Path) -> list[str]:
    collisions: list[str] = []
    for path in repo.rglob("*.json"):
        rel = path.relative_to(repo).as_posix()
        try:
            data = load(path)
        except Exception:
            continue
        for obj in iter_objects(data):
            tid = obj.get("theorem_id")
            is_owner = isinstance(tid, str) and tid in RESERVED and "canonical_name" in obj and "formal_signature" in obj
            if is_owner and rel != REGISTRY_PATH:
                collisions.append(f"duplicate ownership record {tid} at {rel}")
    declaration = re.compile(r"\b(?:theorem|lemma|def|Theorem|Lemma|Definition)\s+(?:V0OSAP\.)?(T15[7-9]|T16[0-2])(?:_[A-Za-z0-9_']*)?(?=\s|[:({])")
    for root in (repo / "lean", repo / "coq"):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".lean", ".v"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                for match in declaration.finditer(text):
                    collisions.append(f"formal declaration {match.group(1)} at {path.relative_to(repo).as_posix()}")
    return sorted(set(collisions))


def validate_schemas(repo: Path) -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema dependency unavailable; schema validation was not executed"]
    for doc_rel, schema_rel in PAIRS:
        doc, schema = repo / doc_rel, repo / schema_rel
        if not doc.is_file(): errors.append(f"missing {doc_rel}"); continue
        if not schema.is_file(): errors.append(f"missing {schema_rel}"); continue
        if jsonschema:
            try: jsonschema.Draft202012Validator(load(schema)).validate(load(doc))
            except Exception as exc: errors.append(f"schema failure {doc_rel}: {exc}")
    manifest = load(repo / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SCHEMA_BUNDLE_MANIFEST.json")
    if manifest.get("schema_count") != 8 or len(manifest.get("schemas", [])) != 8:
        errors.append("schema bundle count mismatch")
    return errors


def dag_errors(dag: dict) -> list[str]:
    errors: list[str] = []
    nodes = {n["theorem_id"]: n for n in dag["nodes"]}
    external = {n["theorem_id"] for n in dag["external_dependencies"]}
    for tid, node in nodes.items():
        for dep in node.get("requires", []):
            if dep not in nodes and dep not in external:
                errors.append(f"undeclared dependency {tid} -> {dep}")
    visiting: set[str] = set(); done: set[str] = set()
    def visit(tid: str):
        if tid in visiting: errors.append(f"cycle at {tid}"); return
        if tid in done: return
        visiting.add(tid)
        for dep in nodes[tid].get("requires", []):
            if dep in nodes: visit(dep)
        visiting.remove(tid); done.add(tid)
    for tid in nodes: visit(tid)
    return errors


def validate_records(repo: Path) -> list[str]:
    errors = validate_schemas(repo)
    lock = load(repo / PAIRS[0][0])
    if lock["wp1_start"]["exact_commit"] != BASE: errors.append("WP1 baseline mismatch")
    if lock["target_branch"] != TARGET_BRANCH: errors.append("target branch mismatch")
    auth = lock["wp1_authorization"]
    if set(auth["reserved_theorem_ids"]) != RESERVED: errors.append("reserved theorem range mismatch")
    if auth["release_actions_authorized"]: errors.append("release action authorized")
    if auth["closed_wp0_record_mutation_authorized"]: errors.append("WP0 record mutation authorized")

    registry = load(repo / REGISTRY_PATH)
    recs = registry["records"]
    ids = [r["theorem_id"] for r in recs]
    if len(recs) != 6 or set(ids) != RESERVED or len(ids) != len(set(ids)): errors.append("theorem registry ID closure failure")
    names = [r["canonical_name"] for r in recs]
    if len(names) != len(set(names)): errors.append("duplicate canonical theorem name")
    conditional = {r["theorem_id"] for r in recs if r["conditional"]}
    if conditional != {"T158", "T160"}: errors.append(f"conditional theorem set mismatch: {sorted(conditional)}")
    for r in recs:
        if r["statement_sha256"] != statement_hash(r["formal_signature"]): errors.append(f"statement hash mismatch {r['theorem_id']}")
        if r["proof_status"] != "DEFERRED_TO_WP4_NOT_CLAIMED": errors.append(f"proof status overclaim {r['theorem_id']}")
        if r["id_status"] != "ACCEPTED_FOR_CANONICALIZATION_PENDING_WP1_MERGE": errors.append(f"ID status mismatch {r['theorem_id']}")
    roles = load(repo / PAIRS[2][0])
    if roles["required_role_count"] != 7 or len(roles["roles"]) != 7 or not roles["owner_assignment_complete"]: errors.append("semantic role closure failure")
    if any(not r["registry_coverage"].startswith("COMPLETE") for r in roles["roles"]): errors.append("incomplete semantic role owner")
    contracts = load(repo / PAIRS[4][0])
    if {c["owner_theorem_id"] for c in contracts["contracts"]} != RESERVED: errors.append("contract ownership mismatch")
    errors += dag_errors(load(repo / PAIRS[6][0]))
    collisions = collision_scan(repo)
    recorded = load(repo / PAIRS[1][0])
    if collisions: errors.extend(collisions)
    if recorded["collisions"] != collisions or recorded["audit_status"] != ("PASS" if not collisions else "FAIL"):
        errors.append("collision audit record is stale")
    gates = load(repo / PAIRS[7][0])
    if gates["gate_count"] != 16 or any(g["status"] != "PASS" for g in gates["gates"]): errors.append("acceptance gate failure")
    if gates["release_actions_authorized"]: errors.append("release action gate failure")
    return errors


def ledger_errors(repo: Path) -> list[str]:
    ledger = repo / "release/v1.4.0/GATE3_CLUSTER_B_WP1_SHA256SUMS.txt"
    if not ledger.is_file(): return ["missing WP1 SHA256 ledger"]
    errors: list[str] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        expected, rel = line.split("  ", 1)
        path = repo / rel
        if not path.is_file(): errors.append(f"ledger missing file {rel}"); continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected: errors.append(f"SHA256 mismatch: {rel}")
    return errors


def canonical_path(value: str) -> str:
    path = value.strip().replace("\\", "/")
    while path.startswith("./"): path = path[2:]
    return path


def is_allowed_path(value: str) -> bool:
    path = canonical_path(value)
    return path in ALLOWED_FILES or any(path.startswith(prefix) for prefix in ALLOWED_DIRECTORIES)


def git_checks(repo: Path, allow_main: bool) -> list[str]:
    errors: list[str] = []
    if not (repo / ".git").exists(): return ["not a git repository"]
    branch = run("git","branch","--show-current",cwd=repo,check=False)
    effective = branch or os.environ.get("GITHUB_HEAD_REF","") or os.environ.get("GITHUB_REF_NAME","")
    if effective != TARGET_BRANCH and not (allow_main and effective == "main"): errors.append(f"unexpected branch {effective!r}")
    try:
        run("git","cat-file","-e",BASE_COMMIT_OBJECT,cwd=repo)
        if run("git","merge-base","HEAD",BASE,cwd=repo) != BASE: errors.append("branch is not rooted at WP1 baseline")
        if run("git","rev-parse","refs/tags/v1.3.0^{}",cwd=repo) != TAG_TARGET: errors.append("stable v1.3.0 tag target changed")
    except RuntimeError as exc: errors.append(str(exc))
    changed = set(run("git","-c","core.quotePath=false","diff","--name-only","--no-renames",BASE,"--",cwd=repo,check=False).splitlines())
    changed.update(run("git","-c","core.quotePath=false","ls-files","--others","--exclude-standard",cwd=repo,check=False).splitlines())
    changed.discard("")
    for raw in sorted(changed):
        path = canonical_path(raw)
        if path.startswith(CLOSED_WP0_RECORD_PREFIX): errors.append(f"closed WP0 record changed: {path}")
        if not is_allowed_path(path): errors.append(f"path outside WP1 allowlist: {path}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--package-only", action="store_true")
    ap.add_argument("--allow-main", action="store_true")
    ns = ap.parse_args()
    repo = Path(ns.repo).resolve()
    errors = validate_records(repo) + ledger_errors(repo)
    if not ns.package_only: errors += git_checks(repo, ns.allow_main)
    result = {
        "artifact":"V0_OSAP_GATE3_CLUSTER_B_WP1",
        "status":"PASS" if not errors else "FAIL",
        "decision":"READY_FOR_HOSTED_CI" if not errors else "HOLD_WITH_BLOCKERS",
        "baseline":BASE,
        "target_branch":TARGET_BRANCH,
        "theorem_ids":sorted(RESERVED),
        "semantic_roles":"7/7" if not errors else "CHECK_FAILED",
        "release_actions_authorized":False,
        "errors":errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
