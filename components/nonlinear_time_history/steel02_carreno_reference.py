"""Carreño et al. (2020) Steel02 reference cases, NOT Fe500 calibration.

[REF docs/source/components/nonlinear_time_history/steel02_carreno_reference.py.md]
Reference DOI 10.1061/(ASCE)ST.1943-541X.0002505, Table 12,
unmachined ASTM A615/A706 Grade 60 reinforcing steel. This module creates
research-only comparison plans and never calls OpenSees or alters model inputs.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from components.inputs.output_contract import atomic_json

ROOT = Path(__file__).resolve().parents[2]
DOI = "10.1061/(ASCE)ST.1943-541X.0002505"
COMMON = dict(E_MPa=202000.0, R0=20.0, cR1=.9, cR2=.08,
              a1=.039, a2=1.0, a3=.029, a4=1.0)


def _rebar_parameters(fy, b, common):
    row=dict(common, Fy_MPa=float(fy), b=float(b))
    row["Fy_kN_m2"]=row["Fy_MPa"]*1000.
    row["E_kN_m2"]=row["E_MPa"]*1000.
    return row


def build_carreno_study(*, nominal_fy_mpa=500.0):
    """[REF docs/source/components/nonlinear_time_history/steel02_carreno_reference.py.md]
    Return literature-only Steel02 scenarios, with nominal Fe500 preserved.
    Paper values are not model fits to local project reinforcement.
    """
    if isinstance(nominal_fy_mpa,bool):
        raise TypeError("Nominal yield strength must be a physical number")
    try:
        fy=float(nominal_fy_mpa)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("Nominal yield strength must be finite") from exc
    if not math.isfinite(fy) or not 100 <= fy <= 1500:
        raise ValueError("Nominal yield strength must be finite in [100,1500] MPa")
    baseline_source=ROOT/"Material_Catalog"/"M30_Fe500_Steel02.json"
    data=json.loads(baseline_source.read_text(encoding="utf-8"))
    baseline=dict(data["parameters"])
    required=("Fy_MPa","E_MPa","b","R0","cR1","cR2","a1","a2","a3","a4")
    if any(key not in baseline for key in required):
        raise ValueError("Original nominal Steel02 card lacks required parameters")
    if not math.isclose(float(baseline["Fy_MPa"]),500.,rel_tol=0,abs_tol=1e-12):
        raise ValueError("Stored nominal Fe500 source card changed; review source")
    baseline["Fy_MPa"]=fy
    baseline["E_kN_m2"]=float(baseline["E_MPa"])*1000.
    baseline["Fy_kN_m2"]=fy*1000.
    shape=dict(baseline,cR1=COMMON["cR1"],cR2=COMMON["cR2"],
               R0=COMMON["R0"])
    def case(case_id,description,parameters,source):
        return dict(case_id=case_id,description=description,
                    parameters=parameters,source=source,
                    auto_apply_to_building=False,
                    independent_cyclic_test_completed=False,
                    calibrated_for_project_fe500=False,
                    native_opensees_simulated=False)
    return {
        "status":"RESEARCH_PLANNING_ONLY_NOT_CALIBRATION",
        "reference":{"title":"Material Model Parameters for the Giuffre-Menegotto-Pinto Uniaxial Steel Stress-Strain Model",
                     "authors":["R. Carreño","K. H. Lotfizadeh","J. P. Conte","J. I. Restrepo"],
                     "year":2020,"doi":DOI,
                     "url":"https://doi.org/"+DOI,
                     "locator":"Table 12, journal page 04019205-16, PDF page 16 (unmachined bars)"},
        "original_baseline_card":"Material_Catalog/M30_Fe500_Steel02.json",
        "project_steel_calibrated":False,
        "native_opensees_executed":False,
        "engineering_design_acceptance":False,
        "cases":[
            case("NOMINAL_FE500_EXISTING_BASELINE",
                 "Existing nominal Fe500 research card; no project coupon calibration",
                 baseline,"Original source card; fy nominal"),
            case("FE500_SHAPE_ONLY_CARRENO_TRANSFER",
                 "Transfer R0/cR1/cR2 only while retaining nominal Fe500 E, fy, b and no isotropic hardening",
                 shape,"Carreño Table 12 transition-shape research hypothesis only"),
            case("CARRENO_ASTM_A615_G60_REFERENCE",
                 "Actual paper ASTM A615 Grade 60 unmachined reference (not Fe500)",
                 _rebar_parameters(480.0,.020,COMMON),
                 "Carreño et al. Table 12 ASTM A615 G60"),
            case("CARRENO_ASTM_A706_G60_REFERENCE",
                 "Actual paper ASTM A706 Grade 60 unmachined reference (not Fe500)",
                 _rebar_parameters(476.0,.012,COMMON),
                 "Carreño et al. Table 12 ASTM A706 G60"),
        ],
        "limitations":[
            "NOT experimentally calibrated Fe500: ASTM A615/A706 Grade 60 cannot be identified with the project's Fe500 reinforcement.",
            "Reference Steel02 isotope a1/a3 terms must be evaluated with a native coupon hysteresis protocol; existing frame material section uses only mandatory Steel02 arguments.",
            "A reference material plan does not change E-SFI-MVLEM-3D/SteelMPF, ConcreteCM/FSAM, reinforcement schedule, boundary confinement or FVD/BRB.",
            "OpenSees documentation defaults cR1=.925, cR2=.15 differ from Carreño calibrated cyclic parameters cR1=.9, cR2=.08.",
        ],
    }


def write_carreno_study(path, *, nominal_fy_mpa=500.):
    """[REF docs/source/components/nonlinear_time_history/steel02_carreno_reference.py.md]
    Persist structured, explicit research-only literature scenarios.
    """
    result=build_carreno_study(nominal_fy_mpa=nominal_fy_mpa)
    atomic_json(path,result)
    return result
