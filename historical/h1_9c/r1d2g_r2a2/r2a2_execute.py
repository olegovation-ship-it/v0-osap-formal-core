from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any, Mapping

AUTHORIZED_SOLVER_HEAD = "084fdb54bc1f58eb4250977030dafff93f88bf6f"
AUTHORIZED_SOLVER_SHA256 = "59f2c18ba9c887a7b0c40e7dea20a35df38f94b274b4fcd0a9826c09fa37d714"
SOURCE_ARTIFACT_ID = 9768876622
SOURCE_ARTIFACT_SHA256 = "4c403f7ae38b89834cc351e7b4a060c05b9e7a6206862b79795265a2304a16fb"

FROZEN_INPUT_SHA256 = {
    "R1d2g_a1_glyph_occurrence_ordinal_ledger.jsonl": "66675ae4a9fd2e804454f7527767cd015f6c69b6b1efc70c53b6d5ca30711925",
    "transition_domain_ledger.jsonl": "a08d3d2445ecd22df63b6950a60df74b1e1e441c26374a985de7e5ebd6374037",
    "key_glyph_exhaustive_backbone_ranks.tsv": "e51968aba6d4c7458ce33e132641cd99be91b2f7416d3ead1ac0590953161025",
    "H1_9C_R1d2g_source_anchor_backbone_assembly.json": "9ec498b24d4f35488612010053d87d684d15a4356ffd28418a75414d2c22996b",
    "source_semantic_contract.json": "78b0b5b32928561c5efa2de3aa20babcaf4c9ec6428b7d2475633fe61c0f0362",
}

FROZEN_IDS: dict[str, dict[str, Any]] = {
    "GP-SH-KN-H": {"blocks": ["1", "2"], "family": "KN", "start_count": 9666, "end_count": 6444, "boundary_hash": "48420504150df0f4fbd33f13cc6aabc6ce68ddeb62901273bc479ce577ccd6ab"},
    "GP-SH-KN-MAIN-A": {"blocks": ["6", "20"], "family": "KN", "start_count": 6444, "end_count": 3222, "boundary_hash": "8e1a6289ac6f8b34559ff256dc7f5c0270805d42b4b1a0003ad87c1f1ea538b8"},
    "GP-SH-KN-MAIN-B": {"blocks": ["20", "25"], "family": "KN", "start_count": 3222, "end_count": 1611, "boundary_hash": "6c82b8b9a2adbb1750d57c6042ccc799dc6e9581c5fefaa69a355037a9ab6f65"},
    "GP-SH-KS-B34": {"blocks": ["3", "4"], "family": "KS", "start_count": 3222, "end_count": 6444, "boundary_hash": "2241f9722604f3d30ca8a0d941ddf8abb0825d84411ad4913b7ccd02f42d7a67"},
    "GP-SH-KS-H": {"blocks": ["1", "2"], "family": "KS", "start_count": 9666, "end_count": 6444, "boundary_hash": "c22f711696eec459ac0c18fed8a00d1584c60768ef99a0897e4ebafef5fd0c9d"},
    "GP-SH-KS-MAIN-A": {"blocks": ["4", "17"], "family": "KS", "start_count": 6444, "end_count": 1611, "boundary_hash": "bb116d00787cf16959cfa23e0d9f7f8194f76138cea888573b9a6d5e461f188c"},
}

EXPECTED_OCCURRENCE_ROWS = 199764
EXPECTED_TRANSITION_ROWS = 56550
EXPECTED_ACCEPTED_TOTAL = 1134
EXPECTED_ACCEPTED_PER_RAIL = 567
EXPECTED_BACKBONES = 616

GUARDS = {
    "max_explored_states": 2_000_000,
    "max_seconds": 600.0,
    "max_disk_bytes": 8 * 1024**3,
    "chunk_record_limit": 50_000,
    "guard_contract": "R2A2_OPERATIONAL_ENVELOPE_V1",
}


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_solver(solver_path: Path):
    observed = sha256_file(solver_path)
    if observed != AUTHORIZED_SOLVER_SHA256:
        raise RuntimeError(f"AUTHORIZED_SOLVER_SHA256_MISMATCH:{observed}")
    spec = importlib.util.spec_from_file_location("r2a1b_authorized_solver", solver_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("SOLVER_IMPORT_SPEC_FAILURE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def endpoint_from_occurrence(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "backbone_id": str(row["backbone_id"]),
        "canonical_topology_ordinal": int(row["canonical_topology_ordinal"]),
        "decoded_block_number": str(row["decoded_block_number"]),
        "glyph_id": str(row["glyph_id"]),
        "band_id": str(row["band_id"]),
        "anchor_payload": {
            "decoded_block_number": str(row["decoded_block_number"]),
            "glyph_id": str(row["glyph_id"]),
            "band_id": str(row["band_id"]),
            "shape_sha256": row.get("shape_sha256"),
        },
    }


def verify_and_load_inputs(report_dir: Path, axis_id: str, rail: str) -> dict[str, Any]:
    if axis_id not in FROZEN_IDS or rail not in {"FX", "I"}:
        raise RuntimeError("NON_FROZEN_AXIS_OR_RAIL")
    paths = {name: report_dir / name for name in FROZEN_INPUT_SHA256}
    observed_hashes: dict[str, str] = {}
    for name, expected in FROZEN_INPUT_SHA256.items():
        p = paths[name]
        if not p.is_file():
            raise RuntimeError(f"MISSING_FROZEN_INPUT:{name}")
        observed = sha256_file(p)
        observed_hashes[name] = observed
        if observed != expected:
            raise RuntimeError(f"FROZEN_INPUT_SHA256_MISMATCH:{name}:{observed}")

    assembly = json.loads(paths["H1_9C_R1d2g_source_anchor_backbone_assembly.json"].read_text(encoding="utf-8"))
    if int(assembly["immutable_parent_backbones"]["count"]) != EXPECTED_BACKBONES:
        raise RuntimeError("BACKBONE_COUNT_ASSEMBLY_MISMATCH")
    c14a = assembly["C14a_transition_domain_completeness"]
    if c14a.get("status") != "PASS" or int(c14a.get("actual_domain_row_count", -1)) != EXPECTED_TRANSITION_ROWS or int(c14a.get("accepted_count", -1)) != EXPECTED_ACCEPTED_TOTAL:
        raise RuntimeError("C14A_FROZEN_CERTIFICATE_MISMATCH")

    frozen = FROZEN_IDS[axis_id]
    source_req = assembly["source_anchor_requirements"].get(axis_id)
    if not source_req or list(map(str, source_req.get("anchors", []))) != frozen["blocks"] or str(source_req.get("family")) != frozen["family"]:
        raise RuntimeError("SOURCE_ANCHOR_REQUIREMENT_MISMATCH")

    contract = json.loads(paths["source_semantic_contract.json"].read_text(encoding="utf-8"))
    semantic = contract["frozen_segment_semantics"][axis_id]
    boundary_hash = sha256_bytes(canonical_json_bytes(semantic))
    if boundary_hash != frozen["boundary_hash"]:
        raise RuntimeError(f"BOUNDARY_SEMANTICS_HASH_MISMATCH:{boundary_hash}")

    path_node_counts: dict[str, int] = {}
    rank_rows = 0
    with paths["key_glyph_exhaustive_backbone_ranks.tsv"].open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rank_rows += 1
            bid = str(row["backbone_id"])
            n = int(row["backbone_node_count"])
            if bid in path_node_counts and path_node_counts[bid] != n:
                raise RuntimeError(f"BACKBONE_NODE_COUNT_CONFLICT:{bid}")
            path_node_counts[bid] = n
    if len(path_node_counts) != EXPECTED_BACKBONES:
        raise RuntimeError(f"BACKBONE_COUNT_RANK_LEDGER_MISMATCH:{len(path_node_counts)}")

    transitions: list[dict[str, Any]] = []
    accepted_total = accepted_rail = 0
    with paths["transition_domain_ledger.jsonl"].open(encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            transitions.append(row)
            if row.get("decision") == "ACCEPT":
                accepted_total += 1
                if row.get("registration_rail") == rail:
                    accepted_rail += 1
    if len(transitions) != EXPECTED_TRANSITION_ROWS or accepted_total != EXPECTED_ACCEPTED_TOTAL or accepted_rail != EXPECTED_ACCEPTED_PER_RAIL:
        raise RuntimeError(f"TRANSITION_DOMAIN_COUNT_MISMATCH:{len(transitions)}:{accepted_total}:{accepted_rail}")

    start_block, end_block = frozen["blocks"]
    starts: list[dict[str, Any]] = []
    ends: list[dict[str, Any]] = []
    occurrence_rows = 0
    with paths["R1d2g_a1_glyph_occurrence_ordinal_ledger.jsonl"].open(encoding="utf-8") as f:
        for line in f:
            occurrence_rows += 1
            row = json.loads(line)
            if row.get("axis_id") != axis_id or row.get("registration_rail") != rail:
                continue
            block = str(row.get("decoded_block_number"))
            if block == start_block:
                starts.append(endpoint_from_occurrence(row))
            if block == end_block:
                ends.append(endpoint_from_occurrence(row))
    if occurrence_rows != EXPECTED_OCCURRENCE_ROWS:
        raise RuntimeError(f"OCCURRENCE_LEDGER_ROW_COUNT_MISMATCH:{occurrence_rows}")
    if len(starts) != frozen["start_count"] or len(ends) != frozen["end_count"]:
        raise RuntimeError(f"SOURCE_INVENTORY_COUNT_MISMATCH:{len(starts)}:{len(ends)}")
    if len({x["backbone_id"] for x in starts}) != EXPECTED_BACKBONES or len({x["backbone_id"] for x in ends}) != EXPECTED_BACKBONES:
        raise RuntimeError("SOURCE_INVENTORY_BACKBONE_COVERAGE_MISMATCH")

    return {
        "transitions": transitions,
        "starts": starts,
        "ends": ends,
        "path_node_counts": path_node_counts,
        "boundary_hash": boundary_hash,
        "input_hashes": observed_hashes,
        "input_validation": {
            "status": "PASS",
            "axis_id": axis_id,
            "rail": rail,
            "source_start_block": start_block,
            "source_end_block": end_block,
            "start_anchor_inventory_count": len(starts),
            "end_anchor_inventory_count": len(ends),
            "start_backbone_coverage": len({x["backbone_id"] for x in starts}),
            "end_backbone_coverage": len({x["backbone_id"] for x in ends}),
            "occurrence_ledger_row_count": occurrence_rows,
            "transition_domain_row_count": len(transitions),
            "accepted_transition_count_total": accepted_total,
            "accepted_transition_count_rail": accepted_rail,
            "backbone_count": len(path_node_counts),
            "rank_ledger_row_count": rank_rows,
            "frozen_boundary_semantics_hash": boundary_hash,
        },
    }


def gzip_verified(uncompressed: Path, expected_uncompressed_sha256: str) -> dict[str, Any]:
    if sha256_file(uncompressed) != expected_uncompressed_sha256:
        raise RuntimeError("PRE_GZIP_FINAL_SET_SHA256_MISMATCH")
    gz_path = uncompressed.with_suffix(uncompressed.suffix + ".gz")
    with uncompressed.open("rb") as src, gzip.GzipFile(filename=str(gz_path), mode="wb", compresslevel=6, mtime=0) as dst:
        shutil.copyfileobj(src, dst, length=1 << 20)
    h = hashlib.sha256()
    count = 0
    with gzip.open(gz_path, "rb") as f:
        for line in f:
            h.update(line)
            count += 1
    if h.hexdigest() != expected_uncompressed_sha256:
        raise RuntimeError("POST_GZIP_DECOMPRESSION_SHA256_MISMATCH")
    return {
        "compressed_path": str(gz_path),
        "compressed_sha256": sha256_file(gz_path),
        "compressed_size_bytes": gz_path.stat().st_size,
        "decompressed_sha256_verified": h.hexdigest(),
        "decompressed_record_count": count,
    }


def write_manifest(root: Path, files: list[Path], manifest: Path) -> None:
    rels = sorted({str(p.relative_to(root)) for p in files if p.is_file() and p != manifest})
    manifest.write_text("".join(f"{sha256_file(root / rel)}  {rel}\n" for rel in rels), encoding="utf-8")
    if manifest.name in manifest.read_text(encoding="utf-8"):
        raise RuntimeError("SHA_MANIFEST_SELF_REFERENCE")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", required=True)
    ap.add_argument("--rail", required=True, choices=["FX", "I"])
    ap.add_argument("--source-report-dir", required=True, type=Path)
    ap.add_argument("--solver-path", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    safe = args.axis.replace("/", "_") + "__" + args.rail
    run_record_path = args.output_dir / f"{safe}.run_record.json"
    manifest_path = args.output_dir / f"{safe}.SHA256.txt"
    record: dict[str, Any] = {
        "schema_version": "H1.9C-R1d2g-R2A2-authoritative-six-ID-execution-v1",
        "stage": "H1.9C-R1d2g-R2A2",
        "mode": "BOUNDED_REAL_DOMAIN_MAPPING_RESOURCE_EXHAUSTION_EXECUTION",
        "axis_id": args.axis,
        "rail": args.rail,
        "authorized_solver_head": AUTHORIZED_SOLVER_HEAD,
        "authorized_solver_sha256": AUTHORIZED_SOLVER_SHA256,
        "source_artifact_id": SOURCE_ARTIFACT_ID,
        "source_artifact_sha256": SOURCE_ARTIFACT_SHA256,
        "operational_guards": GUARDS,
        "transport": {
            "github_actions": bool(os.environ.get("GITHUB_ACTIONS")),
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "github_workflow": os.environ.get("GITHUB_WORKFLOW"),
            "orchestration_sha": os.environ.get("GITHUB_SHA"),
            "python": sys.version,
            "platform": platform.platform(),
        },
        "scientific_firewall": {
            "six_resource_exhaustion_IDs_only": True,
            "solver_semantics_mutated": False,
            "geometry_promotion": False,
        },
    }
    try:
        solver = load_solver(args.solver_path)
        restored = verify_and_load_inputs(args.source_report_dir, args.axis, args.rail)
        record["input_hashes"] = restored["input_hashes"]
        record["input_validation"] = restored["input_validation"]
        result = solver.solve_prepared_axis_streaming(
            axis_id=args.axis,
            rail=args.rail,
            prerequisite_ready=True,
            prerequisite_blockers=[],
            transition_rows=restored["transitions"],
            starts=restored["starts"],
            ends=restored["ends"],
            supporting_glyphs=[],
            require_supporting_occurrence=False,
            path_node_counts=restored["path_node_counts"],
            boundary_hash=restored["boundary_hash"],
            frozen_transition_domain_sha256=FROZEN_INPUT_SHA256["transition_domain_ledger.jsonl"],
            frozen_occurrence_ledger_sha256=FROZEN_INPUT_SHA256["R1d2g_a1_glyph_occurrence_ordinal_ledger.jsonl"],
            output_dir=args.output_dir,
            guards=solver.ResourceGuards(
                max_explored_states=GUARDS["max_explored_states"],
                max_seconds=GUARDS["max_seconds"],
                max_disk_bytes=GUARDS["max_disk_bytes"],
            ),
            chunk_record_limit=GUARDS["chunk_record_limit"],
        )
        record["C14b"] = result.get("C14b")
        if result.get("C14b") == "PASS":
            cert = dict(result["certificate"])
            if not result.get("certificate_persisted_and_verified"):
                raise RuntimeError("CERTIFICATE_NOT_PERSISTED_VERIFIED")
            final_path = Path(result["canonical_set_path"])
            cert_path = Path(result["certificate_path"])
            gz = gzip_verified(final_path, str(cert["final_canonical_set_sha256"]))
            if int(gz["decompressed_record_count"]) != int(cert["unique_canonical_mapping_count"]):
                raise RuntimeError("GZIP_RECORD_COUNT_MISMATCH")
            record["certificate"] = cert
            record["certificate_path"] = cert_path.name
            record["compressed_canonical_set"] = {**gz, "compressed_path": Path(gz["compressed_path"]).name}
            final_path.unlink()
            record["claim_grade_mapping_set_persisted_as_lossless_gzip"] = True
        else:
            record["resource_exhaustion_reason"] = result.get("resource_exhaustion_reason")
            record["resource_detail"] = result.get("resource_detail")
            record["error"] = result.get("error")
            record["partial_outputs_claim_grade"] = bool(result.get("partial_outputs_claim_grade", False))
        record["execution_verdict"] = record["C14b"]
    except Exception as exc:
        record["C14b"] = "FAIL_IMPLEMENTATION"
        record["execution_verdict"] = "FAIL_IMPLEMENTATION"
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["partial_outputs_claim_grade"] = False
        for p in args.output_dir.glob(f"{args.axis}__{args.rail}.*"):
            if p.name not in {run_record_path.name, manifest_path.name}:
                p.unlink(missing_ok=True)
    run_record_path.write_bytes(canonical_json_bytes(record) + b"\n")
    claim_files = [p for p in args.output_dir.iterdir() if p.is_file() and p != manifest_path]
    write_manifest(args.output_dir, claim_files, manifest_path)
    print(json.dumps(record, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
