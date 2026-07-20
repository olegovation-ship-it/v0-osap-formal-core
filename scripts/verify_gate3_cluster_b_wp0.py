#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BASE = "a13a96fda4964dde1719c7d014f11878e1103b20"
TAG_TARGET = "13bf095688bcabd5b090f188e9bd28a16237edeb"
TARGET_BRANCH = "v1.4.0-development"
IPEC = "5474a2c6a3e1c274d17f674889d427c1c91572f7"
VALIDATOR = "3540f47198140ca0a3612f247cfe356fa7fba2cb"

ALLOWED_PREFIXES = (
    ".github/workflows/gate3-cluster-b-wp0.yml",
    "docs/gate3/cluster_b/",
    "release/v1.4.0/",
    "schemas/v1.4.0/",
    "scripts/bootstrap_gate3_cluster_b_wp0.sh",
    "scripts/verify_gate3_cluster_b_wp0.py",
    "tests/test_gate3_cluster_b_wp0.py",
)
FORBIDDEN_PREFIXES = (
    "release/v1.3.0/", "checker/", "lean/", "coq/", "fixtures/", "schemas/v1.1/"
)


def run(*args: str, check: bool = True) -> str:
    p = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{p.stderr.strip()}")
    return p.stdout.strip()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_json(repo: Path) -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    pairs = [
        ("release/v1.4.0/GATE3_CLUSTER_B_WP0_BASELINE_LOCK.json", "schemas/v1.4.0/gate3_cluster_b_wp0_baseline_lock.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP0_BRANCH_BOOTSTRAP_SPEC.json", "schemas/v1.4.0/gate3_cluster_b_wp0_branch_bootstrap.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP0_FROZEN_UPSTREAM_PRESERVATION_RECORD.json", "schemas/v1.4.0/gate3_cluster_b_wp0_preservation_record.schema.json"),
        ("release/v1.4.0/GATE3_CLUSTER_B_WP0_ACCEPTANCE_GATES.json", "schemas/v1.4.0/gate3_cluster_b_wp0_acceptance_gates.schema.json"),
    ]
    for doc_rel, schema_rel in pairs:
        doc_path, schema_path = repo / doc_rel, repo / schema_rel
        if not doc_path.is_file(): errors.append(f"missing {doc_rel}"); continue
        if not schema_path.is_file(): errors.append(f"missing {schema_rel}"); continue
        doc, schema = load(doc_path), load(schema_path)
        if jsonschema:
            try: jsonschema.Draft202012Validator(schema).validate(doc)
            except Exception as exc: errors.append(f"schema failure {doc_rel}: {exc}")
    lock = load(repo / pairs[0][0])
    if lock["branch_start"]["exact_commit"] != BASE: errors.append("baseline commit mismatch")
    if lock["target_branch"] != TARGET_BRANCH: errors.append("target branch mismatch")
    if any(lock["release_actions_authorized"].values()): errors.append("release action was authorized")
    frozen = {x["artifact"]: x for x in lock["frozen_upstreams"]}
    if frozen["V0 Integrated Proof-Evidence Contract v0.1"]["exact_commit"] != IPEC: errors.append("IPEC pin mismatch")
    if frozen["V0 Validator Core v0.12"]["exact_tag_target"] != VALIDATOR: errors.append("Validator pin mismatch")
    preservation = load(repo / pairs[2][0])
    if preservation["canonical_new_theorem_ids_authorized"] != []: errors.append("WP0 canonicalized theorem IDs")
    if preservation["release_actions_authorized"] is not False: errors.append("WP0 release firewall failure")
    gates = load(repo / pairs[3][0])
    if gates["gate_count"] != 14 or len(gates["gates"]) != 14: errors.append("acceptance gate count mismatch")
    return errors


def git_checks(repo: Path, allow_main: bool) -> list[str]:
    errors: list[str] = []
    if not (repo / ".git").exists():
        return ["not a git repository"]
    branch = run("git", "-C", str(repo), "branch", "--show-current")
    if branch != TARGET_BRANCH and not (allow_main and branch == "main"):
        errors.append(f"unexpected branch {branch!r}")
    try:
        run("git", "-C", str(repo), "cat-file", "-e", f"{BASE}^{{commit}}")
        merge_base = run("git", "-C", str(repo), "merge-base", "HEAD", BASE)
        if merge_base != BASE: errors.append(f"branch is not rooted at exact baseline: {merge_base}")
        tag = run("git", "-C", str(repo), "rev-parse", "refs/tags/v1.3.0^{}")
        if tag != TAG_TARGET: errors.append(f"stable tag target mismatch: {tag}")
    except RuntimeError as exc:
        errors.append(str(exc))
    changed = set()
    out = run("git", "-C", str(repo), "diff", "--name-only", BASE, check=False)
    changed.update(x for x in out.splitlines() if x)
    status = run("git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all", check=False)
    for line in status.splitlines():
        if len(line) >= 4:
            path = line[3:]
            if " -> " in path: path = path.split(" -> ", 1)[1]
            changed.add(path)
    for path in sorted(changed):
        if path.startswith(FORBIDDEN_PREFIXES): errors.append(f"forbidden path changed: {path}")
        if not any(path == p or path.startswith(p) for p in ALLOWED_PREFIXES):
            errors.append(f"path outside WP0 allowlist: {path}")
    return errors


def ls_remote(repo_url: str, *refs: str) -> dict[str, str]:
    out = run("git", "ls-remote", repo_url, *refs)
    return {ref: sha for sha, ref in (line.split("\t", 1) for line in out.splitlines() if line)}


def online_checks() -> list[str]:
    errors: list[str] = []
    ipec = ls_remote(
        "https://github.com/olegovation-ship-it/v0-integrated-proof-evidence-contract.git",
        "refs/heads/main", "refs/heads/gate2-development"
    )
    if ipec.get("refs/heads/main") != IPEC: errors.append("remote IPEC main pin mismatch")
    if ipec.get("refs/heads/gate2-development") != IPEC: errors.append("remote IPEC development pin mismatch")
    val = ls_remote(
        "https://github.com/olegovation-ship-it/v0-validator-core.git",
        "refs/tags/v0.12-compiler-passed-freeze", "refs/tags/v0.12-compiler-passed-freeze^{}"
    )
    observed = val.get("refs/tags/v0.12-compiler-passed-freeze^{}") or val.get("refs/tags/v0.12-compiler-passed-freeze")
    if observed != VALIDATOR: errors.append(f"remote Validator tag pin mismatch: {observed}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--package-only", action="store_true")
    ap.add_argument("--allow-main", action="store_true")
    ap.add_argument("--online", action="store_true")
    ns = ap.parse_args()
    repo = Path(ns.repo).resolve()
    errors = validate_json(repo)
    if not ns.package_only:
        errors += git_checks(repo, ns.allow_main)
    if ns.online:
        errors += online_checks()
    result = {
        "status": "PASS" if not errors else "FAIL",
        "artifact": "V0_OSAP_GATE3_CLUSTER_B_WP0",
        "branch": TARGET_BRANCH,
        "baseline": BASE,
        "stable_tag_target": TAG_TARGET,
        "online_checked": bool(ns.online),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
