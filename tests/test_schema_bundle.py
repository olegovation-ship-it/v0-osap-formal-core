from v0_osap_fc1.schema_validation import validate_schema_bundle


def test_schema_bundle_replays():
    assert validate_schema_bundle() == []
