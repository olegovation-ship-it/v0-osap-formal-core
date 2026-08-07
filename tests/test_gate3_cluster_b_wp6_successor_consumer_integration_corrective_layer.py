from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "release/v1.4.0/tools/verify_wp6_successor_consumer_integration_corrective_layer.py"
SPEC = importlib.util.spec_from_file_location(
    "wp6_successor_consumer_integration_corrective_layer",
    VERIFIER_PATH,
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_manifest_is_exact_canonical_and_closed() -> None:
    data = (ROOT / MODULE.MANIFEST).read_bytes()
    manifest = json.loads(data.decode("utf-8"))
    assert data == (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    assert manifest["version"] == "0.1"
    assert manifest["modified_path_count"] == 8
    assert manifest["additive_path_count"] == 5
    assert manifest["surface_path_count"] == 13
    assert manifest["ledger_entry_count"] == 4
    assert manifest["unresolved_dependency_count"] == 0


def test_exact_transform_inventory_and_source_blob_anchors() -> None:
    manifest = MODULE.load_manifest()
    assert sorted(item["path"] for item in manifest["transformations"]) == sorted(
        manifest["modified_paths"]
    )
    for item in manifest["transformations"]:
        assert len(item["predecessor_blob_sha1"]) == 40
        assert item["replacements"]
        source = MODULE.require_run(
            "git",
            "show",
            MODULE.PREDECESSOR + ":" + item["path"],
            text=False,
        ).stdout
        expected = MODULE.apply_transform(source, item)
        assert expected.endswith(b"\n")


def test_additive_ledger_is_exact_and_self_excluding() -> None:
    result = MODULE.verify_ledger()
    assert result["entry_count"] == 4
    assert result["self_excluded"] is True
    rows = MODULE.parse_ledger(
        (ROOT / MODULE.LEDGER).read_bytes(),
        MODULE.LEDGER,
    )
    assert [path for _, path in rows] == MODULE.ATTESTED_ADDITIVE_PATHS
    assert MODULE.LEDGER not in [path for _, path in rows]


def test_surface_verifier_accepts_exact_hypothetical_bytes() -> None:
    result = MODULE.verify_all(
        MODULE.load_manifest(),
        verify_predecessor_v02=False,
    )
    assert result["status"] == "PASS"
    assert result["modified_path_count"] == 8
    assert result["additive_path_count"] == 5
    assert result["surface_path_count"] == 13


def test_eight_workflow_replay_contract_is_complete() -> None:
    groups = MODULE.load_manifest()["replay_groups"]
    assert sorted(groups) == [
        "wp2",
        "wp2-post-merge",
        "wp3",
        "wp3-post-merge",
        "wp5",
        "wp5-post-merge",
        "wp5-sync-helper",
        "wp6-post-merge",
    ]
    assert groups["wp2"]["anchor"] == "c90041d3da5b680b574b910de50d8769d32fbfa9"
    assert groups["wp5"]["anchor"] == "14e761e7a34889eebc3c4ef7df17fc56c9267af9"
    assert groups["wp5-post-merge"]["anchor"] == "dba0425c0f98950534bf5c6d407246da58eacd2f"
    assert sorted(groups["wp6-post-merge"]["jobs"]) == [
        "closeout-verifier",
        "dedicated-tests",
        "hosted-ci-context-repair",
    ]
