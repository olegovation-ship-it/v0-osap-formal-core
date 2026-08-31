from __future__ import annotations
import argparse, gzip, hashlib, json
from pathlib import Path
from typing import Any, Iterator

IDS = ["GP-SH-KN-H","GP-SH-KN-MAIN-A","GP-SH-KN-MAIN-B","GP-SH-KS-B34","GP-SH-KS-H","GP-SH-KS-MAIN-A"]

def cjb(o: Any) -> bytes:
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def shab(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def shaf(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def iter_gz(path: Path, expected_sha: str, expected_count: int) -> Iterator[tuple[str,str,bytes]]:
    h=hashlib.sha256(); count=0; prev=None
    with gzip.open(path,'rb') as f:
        for raw in f:
            h.update(raw); count+=1
            obj=json.loads(raw.decode()); payload=cjb(obj); full=shab(payload); rec=("M_"+full[:32],full,payload)
            if prev is not None and rec <= prev: raise RuntimeError(f'NON_STRICT_CANONICAL_ORDER:{path}')
            prev=rec; yield rec
    if h.hexdigest()!=expected_sha: raise RuntimeError(f'DECOMPRESSED_SHA_MISMATCH:{path}')
    if count!=expected_count: raise RuntimeError(f'DECOMPRESSED_COUNT_MISMATCH:{path}:{count}:{expected_count}')

def compare(fx_path: Path, fx_cert: dict, i_path: Path, i_cert: dict) -> dict:
    a=iter(iter_gz(fx_path,fx_cert['final_canonical_set_sha256'],int(fx_cert['unique_canonical_mapping_count'])))
    b=iter(iter_gz(i_path,i_cert['final_canonical_set_sha256'],int(i_cert['unique_canonical_mapping_count'])))
    x=next(a,None); y=next(b,None); ac=bc=inter=ao=bo=0
    while x is not None or y is not None:
        if y is None or (x is not None and x<y): ac+=1; ao+=1; x=next(a,None)
        elif x is None or y<x: bc+=1; bo+=1; y=next(b,None)
        else: ac+=1;bc+=1;inter+=1;x=next(a,None);y=next(b,None)
    equal=(ao==0 and bo==0)
    return {'exact_set_equality':equal,'M_FX_count':ac,'M_I_count':bc,'intersection_cardinality':inter,'FX_only_count':ao,'I_only_count':bo,'rail_sensitivity_classification':'INVARIANT_IDENTICAL' if equal else ('RAIL_SENSITIVE_FINITE' if ac and bc else 'RAIL_DISAGREEMENT'),'scientific_invariance_established':equal,'automatic_PASS_promotion_from_singleton_intersection':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-root',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
    records={}
    for p in a.input_root.rglob('*.run_record.json'):
        r=json.loads(p.read_text()); records[(r['axis_id'],r['rail'])]=(r,p.parent)
    if len(records)!=12: raise SystemExit(f'expected 12 run records, found {len(records)}')
    fx_i=[]
    for axis in IDS:
        fx,fd=records[(axis,'FX')]; ii,idr=records[(axis,'I')]
        rec={'axis_id':axis,'C14b_FX':fx['C14b'],'C14b_I':ii['C14b']}
        if fx['C14b']=='PASS' and ii['C14b']=='PASS':
            fzp=fd/fx['compressed_canonical_set']['compressed_path']; izp=idr/ii['compressed_canonical_set']['compressed_path']
            rec.update(compare(fzp,fx['certificate'],izp,ii['certificate']))
        else:
            rec.update({'exact_set_equality':None,'intersection_cardinality':None,'rail_sensitivity_classification':'NOT_TESTABLE_NO_COMPLETE_MAPPING','scientific_invariance_established':False,'automatic_PASS_promotion_from_singleton_intersection':False})
        fx_i.append(rec)
    summary={'schema_version':'H1.9C-R1d2g-R2A2-summary-v1','stage':'H1.9C-R1d2g-R2A2','mode':'BOUNDED_REAL_DOMAIN_MAPPING_RESOURCE_EXHAUSTION_EXECUTION','run_records':[records[k][0] for k in sorted(records)],'C15_FX_I_records':fx_i,'scientific_firewall':{'geometry_promotion':False},'next_required_stage':'H1.9C-R1d2g-R2A2a READ_ONLY SIX_ID EXECUTION / COMPLETION-CERTIFICATE / FX-I VERDICT / CLAIM-CEILING AUDIT + META_STOP'}
    sp=a.output_dir/'R2A2_authoritative_execution_summary.json'; sp.write_bytes(cjb(summary)+b'\n')
    manifest=a.output_dir/'R2A2_SHA256.txt'; manifest.write_text(f'{shaf(sp)}  {sp.name}\n')
    print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__': main()
