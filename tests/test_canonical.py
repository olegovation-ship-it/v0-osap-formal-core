from v0_osap_fc1.canonical import canonical_sha256, canonical_text


def test_canonicalization_is_order_stable():
    left = {"b": 2, "a": [3, 1]}
    right = {"a": [3, 1], "b": 2}
    assert canonical_text(left) == '{"a":[3,1],"b":2}\n'
    assert canonical_sha256(left) == canonical_sha256(right)
