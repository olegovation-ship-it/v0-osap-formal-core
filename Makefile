.PHONY: install test schema fixtures canonical manifest verify-manifest verify-closure lean coq no-holes all

install:
	python -m pip install -e '.[dev]'

test:
	pytest -q

schema:
	v0-osap-fc1 schema-bundle

fixtures:
	v0-osap-fc1 fixtures

canonical:
	v0-osap-fc1 canonicalize schemas/v1.1/canonical_example_registry.json > /tmp/v0-osap-canonical.json

manifest:
	python scripts/build_manifest.py

verify-manifest:
	python scripts/verify_manifest.py

verify-closure:
	python scripts/verify_closure.py

lean:
	cd lean && lake build

coq:
	$(MAKE) -C coq

no-holes:
	python scripts/check_no_proof_holes.py

all: test schema fixtures no-holes verify-manifest verify-closure
