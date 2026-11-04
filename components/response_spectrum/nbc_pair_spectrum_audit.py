"""NBC105:2025 §9.3.2.2 pair-spectrum audit using EXISTING spectrum engine.

The existing source module computes 5%-damped pseudo acceleration from actual
recorded accelerograms; this module checks X/Y candidates and selects the
smaller factor for BOTH components. Its mean-ordinate fitting method is a
screening convention, not a codified spectral fitting algorithm or design PASS.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from components.nonlinear_time_history.nbc105_2025_audit import paired_ground_motion_scale,scaling_period_range

def pair_spectrum_audit(x_path,y_path,*,soil_type,Z,I,omega_u,R_mu,
                        t1_x_s,t1_y_s,tn90_x_s,tn90_y_s,evaluator=None):
    """Generate a reproducible research-only paired component spectrum report.

    evaluator is an injected test hook; production evaluates actual accelerogram
    spectra using site_spectrum_and_scaling.candidate_scale_factor.
    """
    x,y=(Path(p).expanduser().resolve() for p in (x_path,y_path))
    for path in (x,y):
        if not path.is_file() or path.stat().st_size==0:
            raise FileNotFoundError("Missing/empty original record: "+str(path))
    if x==y:raise ValueError("Paired orthogonal components must be different source files")
    scaling_period_range(tn90_x_s,t1_x_s,R_mu)
    scaling_period_range(tn90_y_s,t1_y_s,R_mu)
    if evaluator is None:
        from components.response_spectrum.site_spectrum_and_scaling import candidate_scale_factor
        evaluator=candidate_scale_factor
    inputs=((x,t1_x_s,tn90_x_s),(y,t1_y_s,tn90_y_s))
    items=[]
    for path,t1,tn in inputs:
        r=evaluator(str(path),soil_type=soil_type,Z=Z,I=I,omega_u=omega_u,
                   R_mu=R_mu,T1_s=t1,Tn_s=tn)
        factor=float(r["candidate_factor"])
        if not math.isfinite(factor) or factor<=0:
            raise ValueError("Nonfinite/nonpositive derived component factor")
        items.append({"source_file":str(path),
          "source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
          "independent_candidate_scale":factor,
          "spectral_diagnostic":r})
    factors=[r["independent_candidate_scale"] for r in items]
    allowed=all(.33<=v<=3 for v in factors)
    lower=min(factors)
    if allowed:
        # Also enforce the source range with the canonical pure helper.
        lower=paired_ground_motion_scale(*factors)
    return {
        "status":"REJECT_PAIR_OUTSIDE_0.33_TO_3" if not allowed
                 else "PAIR_FACTOR_COMPUTED_SPECTRAL_SCREEN_ONLY",
        "nbc_clause":"NBC 105:2025 §§9.3.2.2(a–d), 9.3.2.3",
        "components":items,"shared_scale_both_components":lower if allowed else None,
        "both_component_factors_in_code_range":allowed,
        "scaling_method":"Existing 5pct Newmark candidate_scale_factor: ratio of mean target to mean recorded spectral ordinates",
        "target_basis":"ULS elastic C(T) / Omega_u; not the ESM Cd spectrum",
        "original_record_files_modified":False,
        "spectral_match_independently_approved":False,
        "seismic_hazard_record_selection_approved":False,
        "final_nbc_design_approval":False,
        "limitations":[
           "Candidate mean-spectrum matching is a research diagnostic; no acceptance deviation was invented.",
           "Review site-specific magnitude, fault distance, mechanism and record frequency content.",
           "Apply the same lower factor to both orthogonal accelerations and run XY and YX.",
           "Do not automatically rescale out-of-range pairs; replace the record pair.",
           "Check T1 and Tn90 from modal effective participation and sample data units."
        ]
    }

def write_pair_audit(destination,*args,**kwargs):
    report=pair_spectrum_audit(*args,**kwargs)
    path=Path(destination);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    return report
