"""Optional read-only original vs matched waveform lineage audit.

Uses the existing 16-component matched register and a separate original .AT2
register. Never mistakes PGA ratio for SeismoMatch source amplitude scale.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

from tools.verify_matched_waveforms import audit as audit_matched, parse_matched, ROOT

ORIGINAL_REGISTER = (ROOT/"docs"/"ground_motions"/"seismomatch_20261104"
                     /"original_component_register.csv")
MATCHED_REGISTER = (ROOT/"docs"/"ground_motions"/"seismomatch_20261104"
                    /"matched_component_register.csv")


def parse_original_at2(path):
    """Parse a PEER AT2 acceleration history in g with declared NPTS and dt."""
    file=Path(path)
    payload=file.read_bytes()
    lines=payload.decode("utf-8-sig", errors="replace").splitlines()
    if not any("IN UNITS OF G" in line.upper() for line in lines[:5]):
        raise ValueError("Unknown PEER acceleration source units")
    index=next((i for i,line in enumerate(lines[:12])
                if "NPTS" in line.upper() and "DT" in line.upper()),None)
    if index is None:
        raise ValueError("PEER AT2 missing NPTS and DT")
    descriptor=lines[index]
    npts=re.search(r"NPTS\\s*=\\s*(\\d+)",descriptor,re.I)
    dt=re.search(r"DT\\s*=\\s*([.\\dEe+-]+)",descriptor,re.I)
    if not npts or not dt:
        raise ValueError("Invalid NPTS / DT descriptor")
    npts=int(npts.group(1))
    timestep=float(dt.group(1))
    if npts<3 or not math.isfinite(timestep) or timestep<=0:
        raise ValueError("Invalid original time-series dimensions")
    values=[]
    for line in lines[index+1:]:
        for token in line.split():
            try:v=float(token.replace("D","E").replace("d","E"))
            except ValueError as exc:
                raise ValueError("Invalid original acceleration ordinate") from exc
            if not math.isfinite(v):raise ValueError("Nonfinite original acceleration")
            values.append(v)
    if npts!=len(values):
        raise ValueError(f"Declared NPTS={npts} but observed {len(values)}")
    return dict(source=str(file),sha256=hashlib.sha256(payload).hexdigest(),
                npts=npts,dt_s=timestep,duration_s=(npts-1)*timestep,
                peak_acceleration_g=max(abs(v) for v in values),unit="g")


def verify_original_matched(original_dir,matched_dir,orig_register=ORIGINAL_REGISTER,
                            match_register=MATCHED_REGISTER):
    originals_dir=Path(original_dir).resolve()
    matches_dir=Path(matched_dir).resolve()
    with Path(orig_register).open(newline="",encoding="utf-8-sig") as f:
        originals=list(csv.DictReader(f))
    with Path(match_register).open(newline="",encoding="utf-8-sig") as f:
        matches=list(csv.DictReader(f))
    if len(originals)!=16 or len(matches)!=16:
        raise ValueError("Expected exactly sixteen original and matched components")
    original_map={(r["event"],r["component"]):r for r in originals}
    match_map={(r["event"],r["component"]):r for r in matches}
    if len(original_map)!=16 or set(original_map)!=set(match_map):
        raise ValueError("Original and matched event-component keys do not match")
    verified_matched=audit_matched(matches_dir,match_register)
    rows=[]
    for key in sorted(original_map):
        r=original_map[key];m=match_map[key]
        filename=Path(r["original_filename"])
        if filename.name!=r["original_filename"]:
            raise ValueError("Unsafe original filename in register")
        path=originals_dir/filename
        if not path.is_file():
            rows.append(dict(event=key[0],component=key[1],
                             status="MISSING_ORIGINAL",filename=str(path)))
            continue
        try:
            actual=parse_original_at2(path)
            issues=[]
            if actual["sha256"]!=r["original_sha256"]:issues.append("HASH")
            if actual["npts"]!=int(r["original_declared_npts"]):issues.append("NPTS")
            if not math.isclose(actual["dt_s"],float(r["original_dt_s"]),abs_tol=1e-10):
                issues.append("DT")
            if not math.isclose(actual["peak_acceleration_g"],float(r["original_pga_g"]),
                                abs_tol=1e-5):issues.append("PGA")
            expected_duration=float(m["matched_end_time_s"])
            rows.append(dict(event=key[0],component=key[1],
               original_filename=str(path),matched_filename=m["source_filename"],
               original_sha256=actual["sha256"],original_npts=actual["npts"],
               original_duration_s=actual["duration_s"],
               matched_duration_s=expected_duration,
               duration_change_s=expected_duration-actual["duration_s"],
               original_pga_g=actual["peak_acceleration_g"],
               matched_pga_g=float(m["matched_pga_g"]),
               status="ORIGINAL_REGISTER_MATCH" if not issues else "ORIGINAL_MISMATCH",
               issues=issues))
        except (ValueError,OSError) as exc:
            rows.append(dict(event=key[0],component=key[1],
                             status="ORIGINAL_PARSE_FAILURE",error=str(exc)))
    failed=sum(r["status"]!="ORIGINAL_REGISTER_MATCH" for r in rows)
    return dict(status=("ORIGINAL_AND_MATCHED_SOURCE_INTEGRITY_REVIEW_REQUIRED"
           if failed or verified_matched["source_discrepancies"] or
                      verified_matched["pair_synchronization_review_count"]
           else "ORIGINAL_AND_MATCHED_SOURCES_MATCH"),
           original_failures=failed,
           matched_source_failures=verified_matched["source_discrepancies"],
           pair_synchronization_review_count=verified_matched["pair_synchronization_review_count"],
           waveforms=rows,paired_source_report=verified_matched["pairs"],
           applied_SeismoMatch_scale_factor_verified=False,
           matched_PGA_divided_by_original_PGA_is_scaling_factor=False,
           original_waveforms_modified=False,
           notes=["No acceleration samples are uploaded or rewritten.",
                  "SeismoMatch matching session logs needed to verify NBC 105 0.33..3.0 and lower-factor rule.",
                  "Gorkha has a large change in duration; Loma Prieta pair ends differ."])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-dir",type=Path,required=True)
    p.add_argument("--matched-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    opts=p.parse_args()
    result=verify_original_matched(opts.original_dir,opts.matched_dir)
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(result,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps(dict(status=result["status"],report=str(opts.output),
                          original_failures=result["original_failures"],
                          matched_source_failures=result["matched_source_failures"],
                          pairs_needing_review=result["pair_synchronization_review_count"]),indent=2))
    return 0 if result["status"]=="ORIGINAL_AND_MATCHED_SOURCES_MATCH" else 3


if __name__=="__main__":
    raise SystemExit(main())
