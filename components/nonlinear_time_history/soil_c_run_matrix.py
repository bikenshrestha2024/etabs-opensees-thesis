"""Generate (never execute) 112 independent Soil C model/event/state run configs.

7 variants M0–M6 x 8 matched pairs x 2 limit states = 112 configurations.
Each contains BOTH simultaneous orientations XY and YX in a fresh domain,
for 224 intended nonlinear analyses; no solver is launched.

Mandatory source: docs/ground_motions/seismomatch_20261104/
The source files are private and must NOT be copied into GitHub.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

from components.nonlinear_time_history.soil_c_nltha_suite import (
    EVENT_ORDER, register_rows, verify_runner_pair,
)

VARIANTS=tuple("M"+str(i) for i in range(7))
STATES=("ULS","SLS")


def resolve_sources(folder, *, register=None):
    """Locate 16 registered sources by SHA; independent of browser suffixes."""
    src=Path(folder).expanduser().resolve()
    if not src.is_dir():
        raise NotADirectoryError(src)
    rows=register_rows(register) if register else register_rows()
    # Only expected text exports; never scan/commit proprietary building files.
    discovered={}
    for path in src.rglob("*.txt"):
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in discovered:
            raise ValueError("Duplicate source bytes / ambiguous waveform matching: "+digest)
        discovered[digest]=str(path.resolve())
    missing=[]
    mapped={}
    for event in EVENT_ORDER:
        for comp in ("A","B"):
            digest=rows[event,comp]["matched_sha256"]
            if digest not in discovered:
                missing.append(event+" "+comp)
            else:
                mapped[event,comp]=discovered[digest]
    if missing:
        raise ValueError("Missing original registered Soil C matched exports: "+", ".join(missing))
    return mapped


def create_configs(*,models_json,matched_dir,output_dir,dt_s=.005,
                   allow_existing=False,source_map=None):
    """Do not approve user rebar, wall materials or source scale from this tool."""
    dt=float(dt_s)
    if not 0<dt<=.005:
        raise ValueError("Use a positive preliminary dt<=0.005s; current modal bound may require less")
    model_map=json.loads(Path(models_json).read_text(encoding="utf-8-sig"))
    if not isinstance(model_map,dict) or set(model_map)!=set(VARIANTS):
        raise ValueError("models JSON requires exact M0..M6 keys")
    models={}
    for key,val in model_map.items():
        path=Path(val).expanduser().resolve()
        if not path.is_dir():
            raise NotADirectoryError("No model export folder for "+key+": "+str(path))
        models[key]=str(path)
    sources=source_map or resolve_sources(matched_dir)
    root=Path(output_dir).expanduser().resolve()
    configurations=[]
    for variant in VARIANTS:
        for state in STATES:
            for event in EVENT_ORDER:
                case_root=root/"results"/variant/state/event.replace(" ","_")
                config_path=root/"configs"/variant/state/(event.replace(" ","_")+".json")
                cfg={
                    "analysis_intent":"RESEARCH_DIAGNOSTIC",
                    "model_folder":models[variant],
                    "output_dir":str(case_root),
                    "soil_type":"C",
                    "soil_c_primary_nltha":True,
                    "earthquake_event":event,
                    "source_records_already_scaled":True,
                    "x_path":str(sources[event,"A"]),
                    "y_path":str(sources[event,"B"]),
                    "scale":1.0,
                    "limit_state":state,
                    "orientations":["XY","YX"],
                    "diagnostic_excitation":"XY",
                    "dt_s":dt,
                    "nonlinear_walls":True,
                    "duration_s":None,
                    "nbc105_2025_design_evidence":None,
                    # Deliberately omitted until the documented source
                    # modal output and actual scale logs are examined.
                    # No placeholder mode IDs may be promoted as thesis evidence.
                    "damping_reference_modes":None,
                    "seismomatch_original_pair_scale_evidence":None,
                    "rayleigh_device_exclusion_reviewed":False,
                    "sls_seismic_input_basis_reviewed":False,
                    "target_workbook_sha256":
                        "fe513b2dc8ad33dda870a2eeefba07f3c6ae8dc8ff92f332b20a323a9d9c63a8",
                    "target_spectrum_kind":"SOIL_C_ULS_C_OVER_OMEGA_U",
                    "input_record_class":"MATCHED_SEISMOMATCH_SOIL_C",
                    "gorkha_processing_reviewed":False,
                    "loma_end_policy":"reject",
                    "engineering_reviewer":None,
                    "source_evidence_not_yet_complete":True,
                }
                configurations.append((config_path,cfg,variant,state,event))
    manifest=root/"00_SOIL_C_M0_M6_RUN_MATRIX.csv"
    summary_path=root/"00_SOIL_C_RESEARCH_RUN_MATRIX.json"
    if not allow_existing:
        collisions=[str(p) for p,*_ in configurations if p.exists()]
        collisions += [str(p) for p in (manifest,summary_path) if p.exists()]
        if collisions:
            raise FileExistsError("Refusing to overwrite existing analysis configs: "+collisions[0])
    root.mkdir(parents=True,exist_ok=True)
    for path,cfg,*_ in configurations:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(cfg,indent=2,allow_nan=False),encoding="utf-8")
    with manifest.open("w",newline="",encoding="utf-8") as fh:
        writer=csv.writer(fh)
        writer.writerow(["order","variant","limit_state","earthquake","orientations",
                         "expected_analysis_count","study_field_group","config_file",
                         "output_directory","status","blocking_review"])
        from components.nonlinear_time_history.soil_c_nltha_suite import FIELD_TYPE
        for i,(path,cfg,variant,state,event) in enumerate(configurations,1):
            blocking=("GORKHA_ORIGINAL_120S_VS_MATCHED_322_94S" if event=="Gorkha"
                  else "LOMA_ONE_SAMPLE_DIFFERENCE" if event=="Loma Prieta" else
                    "MATERIAL_AND_MODAL_VERIFICATION_NOT_COMPLETE")
            writer.writerow([i,variant,state,event,"XY + YX",2,FIELD_TYPE[event],
                             str(path),cfg["output_dir"],"NOT_EXECUTED",blocking])
    summary={
        "status":"CONFIGURATION_ONLY_NOT_EXECUTED",
        "soil_type":"C", "models":list(VARIANTS), "states":list(STATES),
        "earthquakes":list(EVENT_ORDER), "configs_generated":len(configurations),
        "orientations_per_config":["XY","YX"],"intended_total_analyses":len(configurations)*2,
        "matched_input_additional_scale":1.,
        "path_factor_for_g_input_m_s2":9.80665,
        "record_original_scale_factor_logs_verified":False,
        "target_workbook_sha256":"fe513b2dc8ad33dda870a2eeefba07f3c6ae8dc8ff92f332b20a323a9d9c63a8",
        "target":"NBC_105_2025_SOIL_C_ULS_RC_DUAL",
        "sls_seismic_input_review_required":True,
        "damping_mode_selection_required":True,
        "all_materials_and_wall_geometry_approved":False,
        "gorkha_processing_approved":False,"loma_endpoint_policy_approved":False,
        "review_before_execution":True,
        "manifest":str(manifest),
    }
    (root/"00_SOIL_C_RESEARCH_RUN_MATRIX.json").write_text(
        json.dumps(summary,indent=2,allow_nan=False),encoding="utf-8")
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--models-json",required=True)
    p.add_argument("--matched-dir",required=True)
    p.add_argument("--output-dir",required=True)
    p.add_argument("--dt",type=float,default=.005)
    a=p.parse_args()
    print(json.dumps(create_configs(models_json=a.models_json,
           matched_dir=a.matched_dir,output_dir=a.output_dir,dt_s=a.dt),indent=2))

if __name__=="__main__":
    main()
