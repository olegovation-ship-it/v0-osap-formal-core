from v0_osap_fc1.fixtures import replay_all


def test_all_fixtures_match_oracle():
    results = replay_all()
    assert len(results) >= 6
    assert all(item["passed"] for item in results), results
