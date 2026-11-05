"""Standalone review of floor-end torsional irregularity CSV.

Usage:
  python torsion_check.py input_floor_end_displacements.csv output_torsion_review.csv

Source CSV column names:
limit_state,case,axis,storey,end_a_m,end_b_m,centered_cm_load,same_end_basis

An explicit true/false evidence field is required. THIS DOES NOT CALL ETABS
OR OPENSEES; input displacement data must already have been independently
source/case/node-mapped. The result is a diagnostic and design acceptance gate,
not an automatic physical reconfiguration or destructive solver halt.
"""
from __future__ import annotations
import csv
from pathlib import Path
from components.validation.torsion_check import check_torsional_irregularity


def run(input_csv, output_csv):
    source=Path(input_csv);target=Path(output_csv)
    with source.open(newline="",encoding="utf-8-sig") as stream:
        rows=list(csv.DictReader(stream))
    for row in rows:
        for name in ("centered_cm_load","same_end_basis"):
            raw=str(row.get(name,"")).strip().lower()
            if raw not in ("true","false"):
                raise ValueError(name+" must be explicitly true or false, not a guessed default.")
            row[name]=(raw=="true")
        for name in ("end_a_m","end_b_m"):
            if not str(row.get(name,"")).strip():
                row[name]=None
    reviewed=check_torsional_irregularity(rows)
    target.parent.mkdir(parents=True,exist_ok=True)
    columns=list(dict.fromkeys(k for row in reviewed for k in row))
    with target.open("w",newline="",encoding="utf-8-sig") as stream:
        writer=csv.DictWriter(stream,fieldnames=columns)
        writer.writeheader()
        writer.writerows(reviewed)
    return reviewed


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv",type=Path)
    parser.add_argument("output_csv",type=Path)
    arguments=parser.parse_args()
    result=run(arguments.input_csv,arguments.output_csv)
    print("Reviews:",len(result))
    for status in ("EXTREME TORSION","UNBOUNDED","TORSIONAL IRREGULARITY","NOT EVALUATED"):
        number=sum(row["status"]==status for row in result)
        print(status,number)
    print("Design acceptance gate:", "BLOCKED" if any(x["design_acceptance_blocked"] for x in result) else "NO TRIGGER FOUND (provided data only)")
