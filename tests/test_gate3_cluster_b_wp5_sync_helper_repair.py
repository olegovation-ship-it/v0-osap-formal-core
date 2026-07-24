from __future__ import annotations
import importlib.util
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CLASSIFIER = ROOT / "scripts/classify_v1_4_0_development_sync_relation_wp5.py"

def load_classifier():
    spec = importlib.util.spec_from_file_location("wp5_sync_classifier_test", CLASSIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_relation_classifier_generalizes_safe_n_zero():
    module = load_classifier()
    assert module.classify(0,0).decision == "ALREADY_SYNCHRONIZED"
    for n in (1,2,3,10,100):
        r = module.classify(n,0)
        assert r.allowed is True and r.decision == "FAST_FORWARD_ALLOWED" and r.action == "FAST_FORWARD"

def test_relation_classifier_rejects_unsafe_relations():
    module = load_classifier()
    assert module.classify(0,1).decision == "REJECT_DEVELOPMENT_AHEAD"
    assert module.classify(1,1).decision == "REJECT_DIVERGED"
    assert module.classify(7,2).decision == "REJECT_DIVERGED"

def test_declared_replay_fixtures_pass():
    cp = subprocess.run(["python","scripts/replay_gate3_cluster_b_wp5_sync_helper_repair.py"],cwd=ROOT,capture_output=True,text=True)
    assert cp.returncode == 0, cp.stdout + cp.stderr
    result = json.loads(cp.stdout)
    assert result["status"] == "PASS" and result["fixture_count"] == 5

def test_helper_is_ff_only_and_force_free():
    helper = (ROOT / "scripts/synchronize_v1_4_0_development_wp5.sh").read_text()
    assert "git merge-base --is-ancestor" in helper
    assert "git merge --ff-only origin/main" in helper
    assert "git push origin v1.4.0-development" in helper
    assert "--force" not in helper
    assert "force-with-lease" not in helper
    assert "reset --hard" not in helper
    assert "git rebase" not in helper
