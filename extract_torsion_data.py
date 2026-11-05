"""Map signed floor-end responses for NBC 105:2025 torsion review.

Use separate ETABS and OpenSees geometry/results files, not shared node IDs.
Only centered-CM static reference cases are accepted as NBC §5.4.2 input.

python extract_torsion_data.py --geometry etabs_nodes.csv --responses etabs_uxuy.csv --source ETABS --state ULS --output path/to/report
python extract_torsion_data.py --geometry opensees_nodes.csv --responses opensees_uxuy.csv --source OPENSEES --state ULS --output path/to/report

Output includes each valid across-floor pair and the worst case by floor,
and a SHA256 manifest. No ETABS/solver application is modified.
"""
import argparse
from pathlib import Path
from components.validation.floor_end_extraction import write_outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry",required=True,type=Path)
    parser.add_argument("--responses",type=Path)
    parser.add_argument("--etabs-api",action="store_true",help="Attach to already-open ETABS EDB and read signed static results")
    parser.add_argument("--edb",type=Path)
    parser.add_argument("--case",dest="etabs_case")
    parser.add_argument("--axis",choices=["X","Y"])
    parser.add_argument("--step-type")
    parser.add_argument("--step-number",type=float)
    parser.add_argument("--reviewed-centered-cm",action="store_true")
    parser.add_argument("--source",choices=["ETABS","OPENSEES"],required=True)
    parser.add_argument("--state",choices=["ULS","SLS"],required=True)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--end-tol-m",type=float,default=.05)
    parser.add_argument("--alignment-tol-m",type=float,default=.10)
    opts=parser.parse_args()
    responses=opts.responses
    if opts.etabs_api:
        if opts.source!="ETABS":
            parser.error("--etabs-api is only for ETABS")
        if not all((opts.edb,opts.etabs_case,opts.axis,opts.step_type,
                    opts.step_number is not None,opts.reviewed_centered_cm)):
            parser.error("ETABS API needs --edb, --case, --axis, --step-type, --step-number and --reviewed-centered-cm")
        import csv
        from components.validation.floor_end_extraction import read_csv,GEOMETRY_COLUMNS
        from components.validation.etabs_floor_end_api import connect_and_extract
        geometry=read_csv(opts.geometry,GEOMETRY_COLUMNS)
        rows=connect_and_extract(geometry,source_edb=opts.edb,
            limit_state=opts.state,case=opts.etabs_case,axis=opts.axis,
            step_type=opts.step_type,step_number=opts.step_number,
            reviewed_centered_cm=opts.reviewed_centered_cm)
        opts.output.mkdir(parents=True,exist_ok=True)
        responses=opts.output/"ETABS_Signed_Source_Results.csv"
        with responses.open("w",newline="",encoding="utf-8-sig") as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
    elif responses is None:
        parser.error("Either --responses CSV or --etabs-api is required")
    pairs,governing,manifest=write_outputs(opts.output,opts.geometry,responses,
        source=opts.source,limit_state=opts.state,
        end_tol_m=opts.end_tol_m,alignment_tol_m=opts.alignment_tol_m)
    print("Source:",opts.source,"Limit state:",opts.state)
    print("Opposite-end pairs:",len(pairs),"Floor/case checks:",len(governing))
    for row in governing:
        print(row["storey"],row["axis"],row["case"],row["status"],row.get("ratio"))
    print("Evidence hashes written:",opts.output/"Floor_End_Provenance.json")


if __name__=="__main__":main()
