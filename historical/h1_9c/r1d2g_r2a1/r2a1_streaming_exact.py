from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence
import hashlib
import heapq
import json
import os
import shutil
import tempfile
import time

R2A1_SCHEMA_VERSION = "H1.9C-R1d2g-R2A1b-exact-streaming-disk-certificate-v2"
MAPPING_SIGNATURE_SCHEMA_VERSION = "H1.9C-R1d2g-a-canonical-mapping-signature-v1"
ALLOWED_RAILS = ("FX", "I")


class ResourceExhaustion(RuntimeError):
    def __init__(self, reason: str, detail: Mapping[str, Any] | None = None):
        super().__init__(reason)
        self.reason = str(reason)
        self.detail = dict(detail or {})


class HashPrefixCollision(RuntimeError):
    pass


class ImplementationInvariantError(RuntimeError):
    pass


@dataclass(frozen=True)
class ResourceGuards:
    max_explored_states: int | None = 2_000_000
    max_seconds: float | None = 600.0
    max_disk_bytes: int | None = None


@dataclass
class EnumerationStats:
    accepted_transition_count: int = 0
    explored_state_count: int = 0
    simple_chain_count: int = 0
    repeated_fragment_prunes: int = 0
    impossible_endpoint_type_prunes: int = 0
    chain_iterator_naturally_exhausted: bool = False
    mapping_expansion_naturally_exhausted: bool = False
    raw_mapping_candidate_count: int = 0
    supporting_filter_rejection_count: int = 0


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


def verify_final_canonical_set(
    path: Path, *, expected_sha256: str, expected_unique_count: int
) -> dict[str, Any]:
    """Re-read the durable final set and independently verify bytes, count and order."""
    path = Path(path)
    h = hashlib.sha256()
    count = 0
    previous: tuple[str, str, bytes] | None = None
    with path.open("rb") as f:
        for raw in f:
            h.update(raw)
            if not raw.endswith(b"\n"):
                raise ImplementationInvariantError("final canonical set line missing newline")
            payload = canonical_json_bytes(json.loads(raw.decode("utf-8")))
            full = sha256_bytes(payload)
            record = ("M_" + full[:32], full, payload)
            if previous is not None and record <= previous:
                raise ImplementationInvariantError(
                    "final canonical set is not strictly sorted and duplicate-free"
                )
            previous = record
            count += 1
    observed_sha256 = h.hexdigest()
    if observed_sha256 != str(expected_sha256):
        raise ImplementationInvariantError(
            f"final canonical set SHA-256 mismatch: {observed_sha256} != {expected_sha256}"
        )
    if count != int(expected_unique_count):
        raise ImplementationInvariantError(
            f"final canonical set count mismatch: {count} != {expected_unique_count}"
        )
    return {
        "verified": True,
        "sha256": observed_sha256,
        "unique_count": count,
    }


def _certificate_payload_sha256(certificate: Mapping[str, Any]) -> str:
    payload = {k: v for k, v in certificate.items() if k != "certificate_sha256"}
    return sha256_bytes(canonical_json_bytes(payload))


def _write_verified_certificate(path: Path, certificate: Mapping[str, Any]) -> Path:
    """Persist deterministic certificate bytes, then re-read and verify before PASS cleanup."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    expected = dict(certificate)
    expected_sha = str(expected.get("certificate_sha256", ""))
    if not expected_sha or expected_sha != _certificate_payload_sha256(expected):
        raise ImplementationInvariantError("certificate SHA-256 pre-write verification failed")
    blob = canonical_json_bytes(expected) + b"\n"
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        tmp_path.write_bytes(blob)
        os.replace(tmp_path, path)
        observed_blob = path.read_bytes()
        if observed_blob != blob:
            raise ImplementationInvariantError("certificate byte re-read mismatch")
        observed = json.loads(observed_blob.decode("utf-8"))
        if canonical_json_bytes(observed) != canonical_json_bytes(expected):
            raise ImplementationInvariantError("certificate semantic re-read mismatch")
        if str(observed.get("certificate_sha256", "")) != _certificate_payload_sha256(observed):
            raise ImplementationInvariantError("certificate SHA-256 re-read verification failed")
    except Exception:
        tmp_path.unlink(missing_ok=True)
        path.unlink(missing_ok=True)
        raise
    return path


def _cleanup_claim_outputs(output_dir: Path, stem: str) -> None:
    root = Path(output_dir)
    for suffix in (".canonical.jsonl", ".c14b_certificate.json"):
        (root / f"{stem}{suffix}").unlink(missing_ok=True)


def canonical_mapping_object(mapping: Mapping[str, Any]) -> dict[str, Any]:
    """Frozen R1d2g canonical mapping identity; semantics intentionally unchanged."""
    spans = [
        {
            "path_id": str(x["path_id"]),
            "ordinal_start": int(x["ordinal_start"]),
            "ordinal_end": int(x["ordinal_end"]),
        }
        for x in mapping.get("fragment_spans", [])
    ]
    transitions = [
        {"transition_core_id": str(x["transition_core_id"])}
        for x in mapping.get("transitions", [])
    ]
    return {
        "schema_version": MAPPING_SIGNATURE_SCHEMA_VERSION,
        "axis_id": str(mapping["axis_id"]),
        "fragment_spans": spans,
        "transitions": transitions,
        "source_start_anchor": mapping.get("source_start_anchor"),
        "source_end_anchor": mapping.get("source_end_anchor"),
        "frozen_boundary_semantics_hash": mapping.get("frozen_boundary_semantics_hash"),
    }


def full_mapping_sha256(mapping: Mapping[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(canonical_mapping_object(mapping)))


def canonical_mapping_signature(mapping: Mapping[str, Any]) -> str:
    return "M_" + full_mapping_sha256(mapping)[:32]


def _normalized_transition_identity(row: Mapping[str, Any]) -> bytes:
    # Exact duplicate rows with the same transition_id are redundant. If the same ID
    # carries different content, fail rather than silently choosing one representation.
    return canonical_json_bytes(dict(row))


def _accepted_adjacency(
    rows: Sequence[Mapping[str, Any]], rail: str
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]], int]:
    if rail not in ALLOWED_RAILS:
        raise ImplementationInvariantError(f"unsupported rail: {rail}")
    by_tid: dict[str, dict[str, Any]] = {}
    fingerprints: dict[str, bytes] = {}
    for raw in rows:
        r = dict(raw)
        if r.get("registration_rail") != rail or r.get("decision") != "ACCEPT":
            continue
        tid = str(r["transition_id"])
        fp = _normalized_transition_identity(r)
        if tid in fingerprints and fingerprints[tid] != fp:
            raise ImplementationInvariantError(f"transition_id content conflict: {tid}")
        fingerprints[tid] = fp
        by_tid[tid] = r
    adj: dict[str, list[dict[str, Any]]] = {}
    for tid in sorted(by_tid):
        r = by_tid[tid]
        a, b = str(r["source_path_id"]), str(r["destination_path_id"])
        adj.setdefault(a, []).append(r)
        adj.setdefault(b, []).append(r)
    for k in adj:
        adj[k].sort(key=lambda x: str(x["transition_id"]))
    return adj, by_tid, len(by_tid)


def _other(row: Mapping[str, Any], path_id: str) -> str:
    a, b = str(row["source_path_id"]), str(row["destination_path_id"])
    if path_id == a:
        return b
    if path_id == b:
        return a
    raise ImplementationInvariantError("nonincident transition")


def _terminal_on_path(row: Mapping[str, Any], path_id: str) -> str:
    if str(row["source_path_id"]) == path_id:
        return str(row["source_terminal"])
    if str(row["destination_path_id"]) == path_id:
        return str(row["destination_terminal"])
    raise ImplementationInvariantError("nonincident transition")


def iter_simple_fragment_chains_exact_guarded(
    *,
    transition_rows: Sequence[Mapping[str, Any]],
    rail: str,
    start_path_ids: Sequence[str],
    end_path_ids: Sequence[str],
    guards: ResourceGuards,
    stats: EnumerationStats,
) -> Iterator[dict[str, Any]]:
    """Stream the frozen endpoint-compatible simple-path domain exactly.

    This is the R2A1 streaming equivalent of R1d2g-a1's eager chain enumerator.
    PASS may only be asserted by a caller after the iterator reaches natural exhaustion.
    """
    t0 = time.monotonic()
    adj, _lookup, accepted_count = _accepted_adjacency(transition_rows, rail)
    stats.accepted_transition_count = accepted_count
    starts = sorted(set(str(x) for x in start_path_ids))
    ends = set(str(x) for x in end_path_ids)

    for start in starts:
        stack: list[tuple[str, tuple[str, ...], tuple[str, ...], str | None]] = [
            (start, (start,), (), None)
        ]
        while stack:
            elapsed = time.monotonic() - t0
            if guards.max_seconds is not None and elapsed > guards.max_seconds:
                raise ResourceExhaustion(
                    "TIMEOUT",
                    {
                        "explored_states": stats.explored_state_count,
                        "simple_chains": stats.simple_chain_count,
                    },
                )
            if (
                guards.max_explored_states is not None
                and stats.explored_state_count >= guards.max_explored_states
            ):
                raise ResourceExhaustion(
                    "STATE_BUDGET",
                    {
                        "explored_states": stats.explored_state_count,
                        "simple_chains": stats.simple_chain_count,
                    },
                )
            cur, paths, tids, arrival_terminal = stack.pop()
            stats.explored_state_count += 1
            if cur in ends:
                stats.simple_chain_count += 1
                yield {
                    "registration_rail": rail,
                    "ordered_path_ids": list(paths),
                    "ordered_transition_ids": list(tids),
                }
                continue

            for tr in reversed(adj.get(cur, [])):
                out_terminal = _terminal_on_path(tr, cur)
                if arrival_terminal is not None and out_terminal == arrival_terminal:
                    stats.impossible_endpoint_type_prunes += 1
                    continue
                nxt = _other(tr, cur)
                if nxt in paths:
                    stats.repeated_fragment_prunes += 1
                    continue
                next_arrival = _terminal_on_path(tr, nxt)
                stack.append(
                    (
                        nxt,
                        paths + (nxt,),
                        tids + (str(tr["transition_id"]),),
                        next_arrival,
                    )
                )

    stats.chain_iterator_naturally_exhausted = True


def _terminal_ordinal(terminal: str, path_node_counts: Mapping[str, int], path_id: str) -> int:
    n = int(path_node_counts[path_id])
    if n < 1:
        raise ImplementationInvariantError(f"invalid node count for {path_id}")
    if terminal == "T0":
        return 1
    if terminal == "T1":
        return n
    raise ImplementationInvariantError(f"unknown terminal {terminal}")


def mapping_from_chain_frozen(
    axis_id: str,
    chain: Mapping[str, Any],
    start_occ: Mapping[str, Any],
    end_occ: Mapping[str, Any],
    transition_lookup: Mapping[str, Mapping[str, Any]],
    boundary_hash: str,
    path_node_counts: Mapping[str, int],
    supporting_glyphs: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Byte-semantic clone of the frozen R1d2g-a1 mapping constructor."""
    paths = list(chain["ordered_path_ids"])
    tids = list(chain["ordered_transition_ids"])
    a0 = int(start_occ["canonical_topology_ordinal"])
    a1 = int(end_occ["canonical_topology_ordinal"])
    spans: list[dict[str, Any]] = []
    if len(paths) == 1:
        if paths[0] != start_occ["backbone_id"] or paths[0] != end_occ["backbone_id"]:
            raise ImplementationInvariantError("single-path anchor mismatch")
        spans = [
            {
                "path_id": paths[0],
                "ordinal_start": min(a0, a1),
                "ordinal_end": max(a0, a1),
            }
        ]
    else:
        first_tr = transition_lookup[tids[0]]
        st = _terminal_on_path(first_tr, paths[0])
        sto = _terminal_ordinal(st, path_node_counts, paths[0])
        spans.append(
            {
                "path_id": paths[0],
                "ordinal_start": min(a0, sto),
                "ordinal_end": max(a0, sto),
            }
        )
        for i, pid in enumerate(paths[1:-1], 1):
            tin = _terminal_on_path(transition_lookup[tids[i - 1]], pid)
            tout = _terminal_on_path(transition_lookup[tids[i]], pid)
            if tin == tout:
                raise ImplementationInvariantError("IMPOSSIBLE_ENDPOINT_TYPE survived solver")
            oi = _terminal_ordinal(tin, path_node_counts, pid)
            oo = _terminal_ordinal(tout, path_node_counts, pid)
            spans.append(
                {
                    "path_id": pid,
                    "ordinal_start": min(oi, oo),
                    "ordinal_end": max(oi, oo),
                }
            )
        last_tr = transition_lookup[tids[-1]]
        et = _terminal_on_path(last_tr, paths[-1])
        eto = _terminal_ordinal(et, path_node_counts, paths[-1])
        spans.append(
            {
                "path_id": paths[-1],
                "ordinal_start": min(eto, a1),
                "ordinal_end": max(eto, a1),
            }
        )
    transitions = [
        {"transition_core_id": str(transition_lookup[t]["transition_core_id"])} for t in tids
    ]
    return {
        "axis_id": axis_id,
        "fragment_spans": spans,
        "transitions": transitions,
        "source_start_anchor": dict(
            start_occ.get("anchor_payload")
            or {
                "decoded_block_number": start_occ.get("decoded_block_number"),
                "glyph_id": start_occ.get("glyph_id"),
                "band_id": start_occ.get("band_id"),
            }
        ),
        "source_end_anchor": dict(
            end_occ.get("anchor_payload")
            or {
                "decoded_block_number": end_occ.get("decoded_block_number"),
                "glyph_id": end_occ.get("glyph_id"),
                "band_id": end_occ.get("band_id"),
            }
        ),
        "supporting_glyph_occurrences": [dict(x) for x in (supporting_glyphs or [])],
        "frozen_boundary_semantics_hash": boundary_hash,
    }


def mapping_contains_occurrence(mapping: Mapping[str, Any], occurrence: Mapping[str, Any]) -> bool:
    pid = str(occurrence["backbone_id"])
    ordinal = int(occurrence["canonical_topology_ordinal"])
    return any(
        str(s["path_id"]) == pid
        and int(s["ordinal_start"]) <= ordinal <= int(s["ordinal_end"])
        for s in mapping["fragment_spans"]
    )


@dataclass
class ExternalCanonicalSetWriter:
    output_dir: Path
    stem: str
    chunk_record_limit: int = 50_000
    max_disk_bytes: int | None = None
    signature_from_full_digest: Callable[[str], str] = field(
        default=lambda full: "M_" + full[:32]
    )
    _buffer: list[tuple[str, str, bytes]] = field(default_factory=list, init=False)
    _chunks: list[Path] = field(default_factory=list, init=False)
    raw_record_count: int = field(default=0, init=False)
    chunk_local_duplicate_count: int = field(default=0, init=False)
    disk_bytes_written: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.chunk_record_limit < 1:
            raise ValueError("chunk_record_limit must be positive")

    def _guard_disk(self, additional: int) -> None:
        projected = self.disk_bytes_written + int(additional)
        if self.max_disk_bytes is not None and projected > self.max_disk_bytes:
            raise ResourceExhaustion(
                "DISK_BUDGET",
                {"disk_bytes_written": self.disk_bytes_written, "projected_bytes": projected},
            )

    def add(self, mapping: Mapping[str, Any]) -> None:
        canonical = canonical_mapping_object(mapping)
        payload = canonical_json_bytes(canonical)
        full = sha256_bytes(payload)
        signature = str(self.signature_from_full_digest(full))
        self._buffer.append((signature, full, payload))
        self.raw_record_count += 1
        if len(self._buffer) >= self.chunk_record_limit:
            self._flush_chunk()

    def _flush_chunk(self) -> None:
        if not self._buffer:
            return
        rows = sorted(self._buffer)
        self._buffer = []
        chunk_path = self.output_dir / f"{self.stem}.chunk.{len(self._chunks):06d}.tsv"
        last: tuple[str, str, bytes] | None = None
        payloads: list[bytes] = []
        for row in rows:
            if last is not None and row == last:
                self.chunk_local_duplicate_count += 1
                continue
            sig, full, canonical = row
            payloads.append(sig.encode("utf-8") + b"\t" + full.encode("ascii") + b"\t" + canonical + b"\n")
            last = row
        blob = b"".join(payloads)
        self._guard_disk(len(blob))
        chunk_path.write_bytes(blob)
        self.disk_bytes_written += len(blob)
        self._chunks.append(chunk_path)

    @staticmethod
    def _iter_chunk(path: Path) -> Iterator[tuple[str, str, bytes]]:
        with path.open("rb") as f:
            for raw in f:
                raw = raw.rstrip(b"\n")
                sig_b, full_b, canonical = raw.split(b"\t", 2)
                yield sig_b.decode("utf-8"), full_b.decode("ascii"), canonical

    def finalize(self) -> dict[str, Any]:
        self._flush_chunk()
        final_path = self.output_dir / f"{self.stem}.canonical.jsonl"
        if final_path.exists():
            final_path.unlink()
        iterators = [self._iter_chunk(p) for p in self._chunks]
        merged = heapq.merge(*iterators)
        unique_count = 0
        global_duplicate_count = 0
        collision_count = 0
        previous_row: tuple[str, str, bytes] | None = None
        previous_for_signature: tuple[str, str, bytes] | None = None
        h = hashlib.sha256()
        final_bytes = 0
        try:
            with final_path.open("wb") as out:
                for row in merged:
                    sig, full, canonical = row
                    if previous_for_signature is not None and sig == previous_for_signature[0]:
                        if canonical != previous_for_signature[2]:
                            collision_count += 1
                            raise HashPrefixCollision(
                                f"HASH_PREFIX_COLLISION for {sig}: distinct canonical objects"
                            )
                    else:
                        previous_for_signature = row
                    if previous_row is not None and row == previous_row:
                        global_duplicate_count += 1
                        continue
                    line = canonical + b"\n"
                    self._guard_disk(len(line))
                    out.write(line)
                    h.update(line)
                    final_bytes += len(line)
                    unique_count += 1
                    previous_row = row
        except Exception:
            if final_path.exists():
                final_path.unlink()
            raise
        self.disk_bytes_written += final_bytes
        return {
            "external_merge_complete": True,
            "hash_prefix_collision_count": collision_count,
            "raw_canonical_records_received": self.raw_record_count,
            "chunk_local_duplicate_count": self.chunk_local_duplicate_count,
            "global_merge_duplicate_count": global_duplicate_count,
            "exact_duplicate_collapse_count": self.raw_record_count - unique_count,
            "unique_canonical_mapping_count": unique_count,
            "final_canonical_set_path": str(final_path),
            "final_canonical_set_sha256": h.hexdigest(),
            "final_canonical_set_bytes": final_bytes,
            "chunk_count": len(self._chunks),
        }

    def cleanup_chunks(self) -> None:
        for p in self._chunks:
            p.unlink(missing_ok=True)
        self._chunks = []


def solve_prepared_axis_streaming(
    *,
    axis_id: str,
    rail: str,
    prerequisite_ready: bool,
    prerequisite_blockers: Sequence[str],
    transition_rows: Sequence[Mapping[str, Any]],
    starts: Sequence[Mapping[str, Any]],
    ends: Sequence[Mapping[str, Any]],
    supporting_glyphs: Sequence[Mapping[str, Any]],
    require_supporting_occurrence: bool,
    path_node_counts: Mapping[str, int],
    boundary_hash: str,
    frozen_transition_domain_sha256: str,
    frozen_occurrence_ledger_sha256: str,
    output_dir: Path,
    guards: ResourceGuards = ResourceGuards(),
    chunk_record_limit: int = 50_000,
    signature_from_full_digest: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """Exact streaming solver over already-resolved frozen start/end candidate inventories.

    R2A1 deliberately separates source/prerequisite resolution from computational closure.
    The caller must pass the same resolved inventories used by the frozen R1d2g semantics.
    """
    if rail not in ALLOWED_RAILS:
        return {
            "axis_id": axis_id,
            "rail": rail,
            "C14b": "FAIL_IMPLEMENTATION",
            "error": "UNSUPPORTED_RAIL",
        }
    if not prerequisite_ready:
        return {
            "axis_id": axis_id,
            "rail": rail,
            "C14b": "NOT_REACHED_PREREQUISITE_UNRESOLVED",
            "blockers": list(prerequisite_blockers),
        }
    starts = [dict(x) for x in starts]
    ends = [dict(x) for x in ends]
    supporting = [dict(x) for x in supporting_glyphs]
    if not starts or not ends:
        return {
            "axis_id": axis_id,
            "rail": rail,
            "C14b": "NOT_REACHED_PREREQUISITE_UNRESOLVED",
            "blockers": ["NO_ADMISSIBLE_SOURCE_ANCHOR_OCCURRENCE_ON_RAIL_FAMILY_BACKBONES"],
        }

    stats = EnumerationStats()
    starts_by_backbone: dict[str, list[dict[str, Any]]] = {}
    ends_by_backbone: dict[str, list[dict[str, Any]]] = {}
    for row in starts:
        starts_by_backbone.setdefault(str(row["backbone_id"]), []).append(row)
    for row in ends:
        ends_by_backbone.setdefault(str(row["backbone_id"]), []).append(row)
    for d in (starts_by_backbone, ends_by_backbone):
        for key in d:
            d[key].sort(key=canonical_json_bytes)

    _adj, lookup, _accepted = _accepted_adjacency(transition_rows, rail)
    writer = ExternalCanonicalSetWriter(
        output_dir=Path(output_dir),
        stem=f"{axis_id}__{rail}",
        chunk_record_limit=chunk_record_limit,
        max_disk_bytes=guards.max_disk_bytes,
        signature_from_full_digest=(
            signature_from_full_digest
            if signature_from_full_digest is not None
            else (lambda full: "M_" + full[:32])
        ),
    )
    t0 = time.monotonic()
    try:
        chains = iter_simple_fragment_chains_exact_guarded(
            transition_rows=transition_rows,
            rail=rail,
            start_path_ids=sorted(starts_by_backbone),
            end_path_ids=sorted(ends_by_backbone),
            guards=guards,
            stats=stats,
        )
        for chain in chains:
            p0 = str(chain["ordered_path_ids"][0])
            p1 = str(chain["ordered_path_ids"][-1])
            for so in starts_by_backbone.get(p0, []):
                for eo in ends_by_backbone.get(p1, []):
                    if guards.max_seconds is not None and time.monotonic() - t0 > guards.max_seconds:
                        raise ResourceExhaustion(
                            "MAPPING_EXPANSION_TIMEOUT",
                            {
                                "raw_mapping_candidates": stats.raw_mapping_candidate_count,
                                "explored_states": stats.explored_state_count,
                            },
                        )
                    mapping = mapping_from_chain_frozen(
                        axis_id,
                        chain,
                        so,
                        eo,
                        lookup,
                        boundary_hash,
                        path_node_counts,
                        supporting,
                    )
                    stats.raw_mapping_candidate_count += 1
                    if require_supporting_occurrence and not any(
                        mapping_contains_occurrence(mapping, g) for g in supporting
                    ):
                        stats.supporting_filter_rejection_count += 1
                        continue
                    writer.add(mapping)
        stats.mapping_expansion_naturally_exhausted = True
        merge = writer.finalize()
        final_path = Path(merge["final_canonical_set_path"])
        final_verification = verify_final_canonical_set(
            final_path,
            expected_sha256=str(merge["final_canonical_set_sha256"]),
            expected_unique_count=int(merge["unique_canonical_mapping_count"]),
        )
        stable_final_filename = final_path.name
        certificate = {
            "schema_version": R2A1_SCHEMA_VERSION,
            "certificate_type": "R2A1_C14B_EXACT_STREAMING_COMPLETENESS",
            "axis_id": axis_id,
            "rail": rail,
            "frozen_transition_domain_sha256": str(frozen_transition_domain_sha256),
            "frozen_occurrence_ledger_sha256": str(frozen_occurrence_ledger_sha256),
            "frozen_boundary_semantics_hash": str(boundary_hash),
            "accepted_transition_count": stats.accepted_transition_count,
            "start_anchor_inventory_count": len(starts),
            "end_anchor_inventory_count": len(ends),
            "start_anchor_inventory_sha256": sha256_bytes(canonical_json_bytes(sorted(starts, key=canonical_json_bytes))),
            "end_anchor_inventory_sha256": sha256_bytes(canonical_json_bytes(sorted(ends, key=canonical_json_bytes))),
            "explored_state_count": stats.explored_state_count,
            "simple_chain_count": stats.simple_chain_count,
            "raw_mapping_candidate_count": stats.raw_mapping_candidate_count,
            "supporting_filter_rejection_count": stats.supporting_filter_rejection_count,
            "canonical_records_emitted_count": merge["raw_canonical_records_received"],
            "exact_duplicate_collapse_count": merge["exact_duplicate_collapse_count"],
            "unique_canonical_mapping_count": merge["unique_canonical_mapping_count"],
            "final_canonical_set_sha256": merge["final_canonical_set_sha256"],
            "final_canonical_set_filename": stable_final_filename,
            "final_canonical_set_reread_verified": final_verification["verified"],
            "chain_iterator_naturally_exhausted": stats.chain_iterator_naturally_exhausted,
            "mapping_expansion_naturally_exhausted": stats.mapping_expansion_naturally_exhausted,
            "external_merge_complete": merge["external_merge_complete"],
            "hash_prefix_collision_count": merge["hash_prefix_collision_count"],
            "lossless_pruning_counts": {
                "REPEATED_FRAGMENT": stats.repeated_fragment_prunes,
                "IMPOSSIBLE_ENDPOINT_TYPE": stats.impossible_endpoint_type_prunes,
            },
            "heuristic_pruning": False,
            "rank_pruning": False,
            "residual_preference_pruning": False,
            "path_length_preference_pruning": False,
            "FX_preference_pruning": False,
            "target_aware_pruning": False,
            "resource_exhaustion": False,
            "status": "PASS",
        }
        certificate["certificate_sha256"] = _certificate_payload_sha256(certificate)
        certificate_path = Path(output_dir) / f"{axis_id}__{rail}.c14b_certificate.json"
        _write_verified_certificate(certificate_path, certificate)
        writer.cleanup_chunks()
        return {
            "axis_id": axis_id,
            "rail": rail,
            "C14b": "PASS",
            "canonical_set_path": str(final_path),
            "certificate_path": str(certificate_path),
            "certificate_persisted_and_verified": True,
            "certificate": certificate,
        }
    except ResourceExhaustion as exc:
        writer.cleanup_chunks()
        _cleanup_claim_outputs(Path(output_dir), f"{axis_id}__{rail}")
        return {
            "axis_id": axis_id,
            "rail": rail,
            "C14b": "NOT_REACHED_RESOURCE_EXHAUSTION",
            "resource_exhaustion_reason": exc.reason,
            "resource_detail": exc.detail,
            "partial_outputs_claim_grade": False,
            "unique_canonical_mapping_count": None,
        }
    except HashPrefixCollision as exc:
        writer.cleanup_chunks()
        _cleanup_claim_outputs(Path(output_dir), f"{axis_id}__{rail}")
        return {
            "axis_id": axis_id,
            "rail": rail,
            "C14b": "FAIL_IMPLEMENTATION",
            "error": f"HASH_PREFIX_COLLISION: {exc}",
            "partial_outputs_claim_grade": False,
        }
    except Exception as exc:
        writer.cleanup_chunks()
        _cleanup_claim_outputs(Path(output_dir), f"{axis_id}__{rail}")
        return {
            "axis_id": axis_id,
            "rail": rail,
            "C14b": "FAIL_IMPLEMENTATION",
            "error": f"{type(exc).__name__}: {exc}",
            "partial_outputs_claim_grade": False,
        }


def _iter_final_set_records(path: Path) -> Iterator[tuple[str, str, bytes]]:
    """Reconstruct the writer sort key from a final canonical JSONL stream."""
    with Path(path).open("rb") as f:
        previous: tuple[str, str, bytes] | None = None
        for raw in f:
            payload = canonical_json_bytes(json.loads(raw.decode("utf-8")))
            full = sha256_bytes(payload)
            record = ("M_" + full[:32], full, payload)
            if previous is not None and record < previous:
                raise ImplementationInvariantError("final canonical set is not deterministically sorted")
            previous = record
            yield record


def compare_completed_rails(
    *,
    axis_id: str,
    fx_result: Mapping[str, Any],
    i_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Streaming deterministic merge-join; never compares incomplete rail materializations."""
    fx_complete = fx_result.get("C14b") == "PASS"
    i_complete = i_result.get("C14b") == "PASS"
    if not fx_complete or not i_complete:
        return {
            "axis_id": axis_id,
            "fx_enumeration_complete": fx_complete,
            "i_enumeration_complete": i_complete,
            "exact_set_equality": None,
            "intersection_cardinality": None,
            "rail_sensitivity_classification": "NOT_TESTABLE_NO_COMPLETE_MAPPING",
            "scientific_invariance_established": False,
            "automatic_PASS_promotion_from_singleton_intersection": False,
        }

    fx_it = iter(_iter_final_set_records(Path(fx_result["canonical_set_path"])))
    i_it = iter(_iter_final_set_records(Path(i_result["canonical_set_path"])))
    fx_row = next(fx_it, None)
    i_row = next(i_it, None)
    fx_count = i_count = intersection_count = fx_only_count = i_only_count = 0
    while fx_row is not None or i_row is not None:
        if i_row is None or (fx_row is not None and fx_row < i_row):
            fx_count += 1
            fx_only_count += 1
            fx_row = next(fx_it, None)
        elif fx_row is None or i_row < fx_row:
            i_count += 1
            i_only_count += 1
            i_row = next(i_it, None)
        else:
            fx_count += 1
            i_count += 1
            intersection_count += 1
            fx_row = next(fx_it, None)
            i_row = next(i_it, None)

    exact_equal = fx_only_count == 0 and i_only_count == 0
    if exact_equal:
        cls = "INVARIANT_IDENTICAL"
    elif fx_count and i_count:
        cls = "RAIL_SENSITIVE_FINITE"
    else:
        cls = "RAIL_DISAGREEMENT"
    return {
        "axis_id": axis_id,
        "fx_enumeration_complete": True,
        "i_enumeration_complete": True,
        "exact_set_equality": exact_equal,
        "M_FX_count": fx_count,
        "M_I_count": i_count,
        "intersection_cardinality": intersection_count,
        "FX_only_count": fx_only_count,
        "I_only_count": i_only_count,
        "rail_sensitivity_classification": cls,
        "scientific_invariance_established": exact_equal,
        "automatic_PASS_promotion_from_singleton_intersection": False,
    }


def write_sha256_manifest(
    *, root: Path, relative_paths: Sequence[str], manifest_relative_path: str
) -> Path:
    root = Path(root)
    manifest_relative_path = str(manifest_relative_path)
    selected = sorted(set(str(x) for x in relative_paths if str(x) != manifest_relative_path))
    manifest = root / manifest_relative_path
    manifest.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for rel in selected:
        p = root / rel
        if not p.is_file():
            raise FileNotFoundError(rel)
        lines.append(f"{sha256_file(p)}  {rel}")
    manifest.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    # Hard invariant: never self-reference.
    if any(line.endswith("  " + manifest_relative_path) for line in lines):
        raise ImplementationInvariantError("manifest self-reference")
    return manifest
