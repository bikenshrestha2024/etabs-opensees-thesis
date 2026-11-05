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
    parser.add_argument("--responses",required=True,type=Path)
    parser.add_argument("--source",choices=["ETABS","OPENSEES"],required=True)
    parser.add_argument("--state",choices=["ULS","SLS"],required=True)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--end-tol-m",type=float,default=.05)
    parser.add_argument("--alignment-tol-m",type=float,default=.10)
    opts=parser.parse_args()
    pairs,governing,manifest=write_outputs(opts.output,opts.geometry,opts.responses,
        source=opts.source,limit_state=opts.state,
        end_tol_m=opts.end_tol_m,alignment_tol_m=opts.alignment_tol_m)
    print("Source:",opts.source,"Limit state:",opts.state)
    print("Opposite-end pairs:",len(pairs),"Floor/case checks:",len(governing))
    for row in governing:
        print(row["storey"],row["axis"],row["case"],row["status"],row.get("ratio"))
    print("Evidence hashes written:",opts.output/"Floor_End_Provenance.json")


if __name__=="__main__":main()
