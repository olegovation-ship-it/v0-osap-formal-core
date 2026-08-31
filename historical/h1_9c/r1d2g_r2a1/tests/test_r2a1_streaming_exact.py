from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from historical.h1_9c.r1d2g_r2a1.r2a1_streaming_exact import (
    ExternalCanonicalSetWriter,
    HashPrefixCollision,
    ResourceGuards,
    canonical_json_bytes,
    canonical_mapping_object,
    canonical_mapping_signature,
    compare_completed_rails,
    iter_simple_fragment_chains_exact_guarded,
    mapping_from_chain_frozen,
    EnumerationStats,
    solve_prepared_axis_streaming,
    write_sha256_manifest,
)


def tr(tid, core, a, at, b, bt, rail="FX"):
    return {
        "transition_id": tid,
        "transition_core_id": core,
        "registration_rail": rail,
        "decision": "ACCEPT",
        "source_path_id": a,
        "source_terminal": at,
        "destination_path_id": b,
        "destination_terminal": bt,
    }


def endpoint(path, ordinal, label):
    return {
        "backbone_id": path,
        "canonical_topology_ordinal": ordinal,
        "anchor_payload": {"label": label},
    }


def eager_reference(axis_id, rail, transitions, starts, ends, path_counts, boundary_hash):
    # Independent bounded reference reproducing frozen eager semantics for fixtures.
    adj = {}
    lookup = {}
    for r in transitions:
        if r["registration_rail"] != rail or r["decision"] != "ACCEPT":
            continue
        lookup[r["transition_id"]] = r
        adj.setdefault(r["source_path_id"], []).append(r)
        adj.setdefault(r["destination_path_id"], []).append(r)
    for k in adj:
        adj[k].sort(key=lambda x: x["transition_id"])
    start_ids = sorted({x["backbone_id"] for x in starts})
    end_ids = {x["backbone_id"] for x in ends}
    chains = []
    for start in start_ids:
        stack = [(start, (start,), (), None)]
        while stack:
            cur, paths, tids, arrival = stack.pop()
            if cur in end_ids:
                chains.append({
                    "registration_rail": rail,
                    "ordered_path_ids": list(paths),
                    "ordered_transition_ids": list(tids),
                })
                continue
            for r in reversed(adj.get(cur, [])):
                if r["source_path_id"] == cur:
                    out_t, nxt, next_arr = r["source_terminal"], r["destination_path_id"], r["destination_terminal"]
                else:
                    out_t, nxt, next_arr = r["destination_terminal"], r["source_path_id"], r["source_terminal"]
                if arrival is not None and out_t == arrival:
                    continue
                if nxt in paths:
                    continue
                stack.append((nxt, paths + (nxt,), tids + (r["transition_id"],), next_arr))
    mappings = []
    for ch in chains:
        p0, p1 = ch["ordered_path_ids"][0], ch["ordered_path_ids"][-1]
        for so in starts:
            if so["backbone_id"] != p0:
                continue
            for eo in ends:
                if eo["backbone_id"] != p1:
                    continue
                mappings.append(mapping_from_chain_frozen(axis_id, ch, so, eo, lookup, boundary_hash, path_counts, []))
    uniq = {canonical_mapping_signature(m): canonical_mapping_object(m) for m in mappings}
    return [uniq[k] for k in sorted(uniq)]


class R2A1Tests(unittest.TestCase):
    def fixture(self, rail="FX"):
        transitions = [
            tr("T_AB", "C_AB", "A", "T1", "B", "T0", rail),
            tr("T_BC", "C_BC", "B", "T1", "C", "T0", rail),
            tr("T_AD", "C_AD", "A", "T1", "D", "T0", rail),
            tr("T_DC", "C_DC", "D", "T1", "C", "T0", rail),
        ]
        starts = [endpoint("A", 2, "s1"), endpoint("A", 3, "s2"), endpoint("A", 2, "s1")]
        ends = [endpoint("C", 4, "e1"), endpoint("C", 5, "e2")]
        counts = {"A": 6, "B": 7, "C": 8, "D": 9}
        return transitions, starts, ends, counts

    def test_legacy_eager_exact_set_equivalence(self):
        transitions, starts, ends, counts = self.fixture("FX")
        expected = eager_reference("AX", "FX", transitions, starts, ends, counts, "BH")
        with tempfile.TemporaryDirectory() as td:
            result = solve_prepared_axis_streaming(
                axis_id="AX", rail="FX", prerequisite_ready=True, prerequisite_blockers=[],
                transition_rows=transitions, starts=starts, ends=ends, supporting_glyphs=[],
                require_supporting_occurrence=False, path_node_counts=counts, boundary_hash="BH", frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH",
                output_dir=Path(td), guards=ResourceGuards(max_explored_states=10000, max_seconds=30),
                chunk_record_limit=2,
            )
            self.assertEqual(result["C14b"], "PASS")
            actual = [json.loads(x) for x in Path(result["canonical_set_path"]).read_text().splitlines()]
            self.assertEqual(sorted(map(canonical_json_bytes, actual)), sorted(map(canonical_json_bytes, expected)))
            self.assertTrue(result["certificate"]["chain_iterator_naturally_exhausted"])
            self.assertTrue(result["certificate"]["mapping_expansion_naturally_exhausted"])

    def test_independent_bruteforce_chain_crosscheck(self):
        transitions, starts, ends, counts = self.fixture("FX")
        stats = EnumerationStats()
        streamed = list(iter_simple_fragment_chains_exact_guarded(
            transition_rows=transitions, rail="FX", start_path_ids=["A"], end_path_ids=["C"],
            guards=ResourceGuards(max_explored_states=100, max_seconds=10), stats=stats,
        ))
        self.assertEqual(
            {tuple(x["ordered_path_ids"]) for x in streamed},
            {("A", "B", "C"), ("A", "D", "C")},
        )
        self.assertTrue(stats.chain_iterator_naturally_exhausted)

    def test_duplicate_collapse_across_chunks(self):
        mapping = {
            "axis_id": "AX", "fragment_spans": [{"path_id":"A","ordinal_start":1,"ordinal_end":2}],
            "transitions": [], "source_start_anchor":{"x":1}, "source_end_anchor":{"y":2},
            "frozen_boundary_semantics_hash":"BH",
        }
        with tempfile.TemporaryDirectory() as td:
            w = ExternalCanonicalSetWriter(Path(td), "dup", chunk_record_limit=2)
            for _ in range(11):
                w.add(mapping)
            cert = w.finalize()
            self.assertEqual(cert["unique_canonical_mapping_count"], 1)
            self.assertEqual(cert["exact_duplicate_collapse_count"], 10)
            self.assertGreater(cert["chunk_count"], 1)

    def test_forced_prefix_collision_fails_closed(self):
        m1 = {"axis_id":"AX","fragment_spans":[{"path_id":"A","ordinal_start":1,"ordinal_end":1}],"transitions":[],"source_start_anchor":1,"source_end_anchor":1,"frozen_boundary_semantics_hash":"BH"}
        m2 = {"axis_id":"AX","fragment_spans":[{"path_id":"A","ordinal_start":2,"ordinal_end":2}],"transitions":[],"source_start_anchor":2,"source_end_anchor":2,"frozen_boundary_semantics_hash":"BH"}
        with tempfile.TemporaryDirectory() as td:
            w = ExternalCanonicalSetWriter(Path(td), "collision", chunk_record_limit=1, signature_from_full_digest=lambda _: "M_FORCED")
            w.add(m1); w.add(m2)
            with self.assertRaises(HashPrefixCollision):
                w.finalize()

    def test_interruption_is_not_empty_set_pass(self):
        transitions, starts, ends, counts = self.fixture("FX")
        with tempfile.TemporaryDirectory() as td:
            result = solve_prepared_axis_streaming(
                axis_id="AX", rail="FX", prerequisite_ready=True, prerequisite_blockers=[],
                transition_rows=transitions, starts=starts, ends=ends, supporting_glyphs=[],
                require_supporting_occurrence=False, path_node_counts=counts, boundary_hash="BH", frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH",
                output_dir=Path(td), guards=ResourceGuards(max_explored_states=1, max_seconds=30),
                chunk_record_limit=2,
            )
            self.assertEqual(result["C14b"], "NOT_REACHED_RESOURCE_EXHAUSTION")
            self.assertIsNone(result["unique_canonical_mapping_count"])
            self.assertFalse(any(Path(td).glob("*.canonical.jsonl")))

    def test_fx_i_comparison_delayed_until_both_pass(self):
        rec = compare_completed_rails(
            axis_id="AX",
            fx_result={"C14b":"NOT_REACHED_RESOURCE_EXHAUSTION"},
            i_result={"C14b":"NOT_REACHED_RESOURCE_EXHAUSTION"},
        )
        self.assertEqual(rec["rail_sensitivity_classification"], "NOT_TESTABLE_NO_COMPLETE_MAPPING")
        self.assertIsNone(rec["exact_set_equality"])
        self.assertFalse(rec["scientific_invariance_established"])

    def test_fx_i_complete_identical(self):
        transitions_fx, starts, ends, counts = self.fixture("FX")
        transitions_i = [dict(x, registration_rail="I") for x in transitions_fx]
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            fx = solve_prepared_axis_streaming(
                axis_id="AX", rail="FX", prerequisite_ready=True, prerequisite_blockers=[],
                transition_rows=transitions_fx, starts=starts, ends=ends, supporting_glyphs=[],
                require_supporting_occurrence=False, path_node_counts=counts, boundary_hash="BH", frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH",
                output_dir=td/"FX", guards=ResourceGuards(max_explored_states=10000, max_seconds=30), chunk_record_limit=2,
            )
            ii = solve_prepared_axis_streaming(
                axis_id="AX", rail="I", prerequisite_ready=True, prerequisite_blockers=[],
                transition_rows=transitions_i, starts=starts, ends=ends, supporting_glyphs=[],
                require_supporting_occurrence=False, path_node_counts=counts, boundary_hash="BH", frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH",
                output_dir=td/"I", guards=ResourceGuards(max_explored_states=10000, max_seconds=30), chunk_record_limit=3,
            )
            rec = compare_completed_rails(axis_id="AX", fx_result=fx, i_result=ii)
            self.assertEqual(rec["rail_sensitivity_classification"], "INVARIANT_IDENTICAL")
            self.assertTrue(rec["exact_set_equality"])

    def test_deterministic_final_set(self):
        transitions, starts, ends, counts = self.fixture("FX")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outputs = []
            for i, chunk in enumerate([2, 5]):
                r = solve_prepared_axis_streaming(
                    axis_id="AX", rail="FX", prerequisite_ready=True, prerequisite_blockers=[],
                    transition_rows=list(reversed(transitions)) if i else transitions,
                    starts=list(reversed(starts)) if i else starts,
                    ends=list(reversed(ends)) if i else ends,
                    supporting_glyphs=[], require_supporting_occurrence=False,
                    path_node_counts=counts, boundary_hash="BH", frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH", output_dir=root/f"r{i}",
                    guards=ResourceGuards(max_explored_states=10000, max_seconds=30), chunk_record_limit=chunk,
                )
                outputs.append(Path(r["canonical_set_path"]).read_bytes())
            self.assertEqual(outputs[0], outputs[1])

    def test_required_certificate_input_bindings_and_persistence(self):
        transitions, starts, ends, counts = self.fixture("FX")
        with tempfile.TemporaryDirectory() as td:
            result = solve_prepared_axis_streaming(
                axis_id="AX", rail="FX", prerequisite_ready=True, prerequisite_blockers=[],
                transition_rows=transitions, starts=starts, ends=ends, supporting_glyphs=[],
                require_supporting_occurrence=False, path_node_counts=counts, boundary_hash="BH",
                frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH",
                output_dir=Path(td), guards=ResourceGuards(max_explored_states=10000, max_seconds=30),
                chunk_record_limit=2,
            )
            self.assertEqual(result["C14b"], "PASS")
            cert = result["certificate"]
            self.assertEqual(cert["frozen_transition_domain_sha256"], "TDH")
            self.assertEqual(cert["frozen_occurrence_ledger_sha256"], "OLH")
            self.assertEqual(cert["frozen_boundary_semantics_hash"], "BH")
            self.assertTrue(cert["final_canonical_set_reread_verified"])
            self.assertTrue(result["certificate_persisted_and_verified"])
            certificate_path = Path(result["certificate_path"])
            self.assertTrue(certificate_path.is_file())
            self.assertEqual(json.loads(certificate_path.read_text()), cert)

    def test_path_independent_certificate_determinism(self):
        transitions, starts, ends, counts = self.fixture("FX")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cert_bytes = []
            cert_hashes = []
            final_bytes = []
            for i, chunk in enumerate([2, 5]):
                result = solve_prepared_axis_streaming(
                    axis_id="AX", rail="FX", prerequisite_ready=True, prerequisite_blockers=[],
                    transition_rows=list(reversed(transitions)) if i else transitions,
                    starts=list(reversed(starts)) if i else starts,
                    ends=list(reversed(ends)) if i else ends,
                    supporting_glyphs=[], require_supporting_occurrence=False,
                    path_node_counts=counts, boundary_hash="BH",
                    frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH",
                    output_dir=root/f"different-output-root-{i}",
                    guards=ResourceGuards(max_explored_states=10000, max_seconds=30),
                    chunk_record_limit=chunk,
                )
                self.assertEqual(result["C14b"], "PASS")
                cert_bytes.append(Path(result["certificate_path"]).read_bytes())
                cert_hashes.append(result["certificate"]["certificate_sha256"])
                final_bytes.append(Path(result["canonical_set_path"]).read_bytes())
            self.assertEqual(final_bytes[0], final_bytes[1])
            self.assertEqual(cert_bytes[0], cert_bytes[1])
            self.assertEqual(cert_hashes[0], cert_hashes[1])

    def test_certificate_and_final_set_are_verified_before_chunk_cleanup(self):
        transitions, starts, ends, counts = self.fixture("FX")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = solve_prepared_axis_streaming(
                axis_id="AX", rail="FX", prerequisite_ready=True, prerequisite_blockers=[],
                transition_rows=transitions, starts=starts, ends=ends, supporting_glyphs=[],
                require_supporting_occurrence=False, path_node_counts=counts, boundary_hash="BH",
                frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH",
                output_dir=root, guards=ResourceGuards(max_explored_states=10000, max_seconds=30),
                chunk_record_limit=2,
            )
            self.assertEqual(result["C14b"], "PASS")
            self.assertTrue(Path(result["canonical_set_path"]).is_file())
            self.assertTrue(Path(result["certificate_path"]).is_file())
            self.assertFalse(any(root.glob("*.chunk.*.tsv")))
            self.assertTrue(result["certificate"]["final_canonical_set_reread_verified"])
            self.assertTrue(result["certificate_persisted_and_verified"])

    def test_forced_certificate_persistence_failure_fails_closed(self):
        transitions, starts, ends, counts = self.fixture("FX")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch(
                "historical.h1_9c.r1d2g_r2a1.r2a1_streaming_exact._write_verified_certificate",
                side_effect=OSError("forced certificate persistence failure"),
            ):
                result = solve_prepared_axis_streaming(
                    axis_id="AX", rail="FX", prerequisite_ready=True, prerequisite_blockers=[],
                    transition_rows=transitions, starts=starts, ends=ends, supporting_glyphs=[],
                    require_supporting_occurrence=False, path_node_counts=counts, boundary_hash="BH",
                    frozen_transition_domain_sha256="TDH", frozen_occurrence_ledger_sha256="OLH",
                    output_dir=root, guards=ResourceGuards(max_explored_states=10000, max_seconds=30),
                    chunk_record_limit=2,
                )
            self.assertEqual(result["C14b"], "FAIL_IMPLEMENTATION")
            self.assertFalse(result["partial_outputs_claim_grade"])
            self.assertFalse(any(root.glob("*.canonical.jsonl")))
            self.assertFalse(any(root.glob("*.c14b_certificate.json")))
            self.assertFalse(any(root.glob("*.chunk.*.tsv")))

    def test_sha_manifest_excludes_itself(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root/"a.txt").write_text("A")
            (root/"b.txt").write_text("B")
            m = write_sha256_manifest(
                root=root,
                relative_paths=["a.txt","b.txt","report/SHA256.txt"],
                manifest_relative_path="report/SHA256.txt",
            )
            text = m.read_text()
            self.assertIn("a.txt", text)
            self.assertIn("b.txt", text)
            self.assertNotIn("report/SHA256.txt", text)

    def test_frozen_canonical_signature_compatibility(self):
        # Hard-coded reference generated from the frozen R1d2g-a1 implementation.
        transitions = [
            tr("T1", "C1", "A", "T1", "B", "T0", "FX"),
            tr("T2", "C2", "B", "T1", "C", "T0", "FX"),
        ]
        lookup = {x["transition_id"]: x for x in transitions}
        chain = {"registration_rail":"FX","ordered_path_ids":["A","B","C"],"ordered_transition_ids":["T1","T2"]}
        m = mapping_from_chain_frozen(
            "AX", chain, endpoint("A",2,"s"), endpoint("C",4,"e"), lookup, "BH",
            {"A":6,"B":7,"C":8}, [],
        )
        self.assertEqual(canonical_mapping_signature(m), "M_f98de138a8f5e90ee8fa490f505f2ef9")


if __name__ == "__main__":
    unittest.main()
