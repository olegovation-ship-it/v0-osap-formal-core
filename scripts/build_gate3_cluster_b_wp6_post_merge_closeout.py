#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SHA256SUMS.txt'
MANIFEST=ROOT/'release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SCHEMA_BUNDLE_MANIFEST.json'
FIXTURE_SCHEMA=ROOT/'schemas/v1.4.0/gate3_cluster_b_wp6_post_merge_sync_fixture.schema.json'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def canonical(path):
    obj=json.loads(path.read_text(encoding='utf-8')); return path.read_text(encoding='utf-8')==json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n'
def check():
    m=json.loads(MANIFEST.read_text(encoding='utf-8'))
    for item in m['pairs']:
        doc=ROOT/item['document']; sch=ROOT/item['schema']
        Draft202012Validator(json.loads(sch.read_text())).validate(json.loads(doc.read_text()))
        if digest(doc)!=item['document_sha256'] or digest(sch)!=item['schema_sha256']: raise SystemExit('schema bundle digest mismatch: '+item['document'])
        if not canonical(doc) or not canonical(sch): raise SystemExit('non-canonical JSON')
    fs=json.loads(FIXTURE_SCHEMA.read_text()); fm=load('release/v1.4.0/GATE3_CLUSTER_B_WP6_POST_MERGE_SYNC_FIXTURE_MANIFEST.json')
    for row in fm['fixtures']:
        p=ROOT/row['path']; Draft202012Validator(fs).validate(json.loads(p.read_text()))
        if digest(p)!=row['sha256']: raise SystemExit('fixture digest mismatch: '+row['path'])
    entries={}
    for line in LEDGER.read_text(encoding='utf-8').splitlines():
        if line.strip():
            h,rel=line.split('  ',1); entries[rel]=h
    for rel,h in entries.items():
        p=ROOT/rel
        if not p.is_file() or digest(p)!=h: raise SystemExit('post-merge ledger mismatch: '+rel)
    print(f'WP6 POST-MERGE BUILD CHECK: PASS ({len(entries)} ledger entries, {len(m["pairs"])} schema pairs)')
def main():
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); a=p.parse_args()
    if not a.check: raise SystemExit('frozen package: use --check')
    check(); return 0
if __name__=='__main__': raise SystemExit(main())
