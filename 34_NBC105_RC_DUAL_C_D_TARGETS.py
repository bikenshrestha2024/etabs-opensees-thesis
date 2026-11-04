"""Export separate NBC105:2025 RC dual wall Soil C and D ULS target spectra.

Example *only*: python 34_NBC105_RC_DUAL_C_D_TARGETS.py --Z 0.35 --I 1.0
    --output D:/Thesis/TargetSpectra
Supply ACTUAL project Z and I before interpreting as design targets.
"""
import argparse
import json
from components.response_spectrum.nbc105_dual_target import write_target_spectra

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--Z",type=float,required=True,help="Project-specific zoning factor")
    p.add_argument("--I",type=float,required=True,help="Project-specific importance factor")
    p.add_argument("--output",required=True)
    p.add_argument("--step",type=float,default=.005)
    a=p.parse_args()
    print(json.dumps(write_target_spectra(a.output,zoning_Z=a.Z,importance_I=a.I,
                  step_s=a.step),indent=2))
if __name__=="__main__":main()
