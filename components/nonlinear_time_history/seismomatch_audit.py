"""SeismoMatch export provenance and NBC fitting-window screening.

Independent of native OpenSees. A wave-form export's 'matched' header is
not evidence of original independent scaling factors (NBC 105:2025 §9.3.2.2).
All records remain read-only; acceleration units require explicit reporting.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path


def assess_preprocessed_sources(x_path,y_path,*,open_sees_scale=1.0,
                                declared_already_matched=None):
    if declared_already_matched not in (None,True,False):
        raise ValueError("source_records_already_scaled must be true, false, or null")
    files=[Path(x_path).expanduser().resolve(),Path(y_path).expanduser().resolve()]
    if files[0]==files[1]:raise ValueError("XY and YX require different orthogonal source files")
    rows=[]
    for path in files:
        if not path.is_file() or path.stat().st_size==0:
            raise FileNotFoundError(path)
        with path.open("rb") as fh:header=fh.read(8192)
        text=header.decode("utf-8-sig",errors="replace").lower()
        is_match="time series matched accelerogram" in text
        rows.append(dict(source_path=str(path),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         export_header_identifies_seismomatch=is_match,
                         contains_independent_original_pair_factors=False,
                         source_unit_label="g" if "acc(g)" in text else "UNVERIFIED"))
    both=all(r["export_header_identifies_seismomatch"] for r in rows)
    anymatch=any(r["export_header_identifies_seismomatch"] for r in rows)
    if anymatch and not both:
        raise ValueError("Mixed original/matched components: source processing basis must match for both axes")
    if declared_already_matched is False and anymatch:
        raise ValueError("Source header identifies SeismoMatch output but configuration declares unscaled originals")
    if declared_already_matched is True and not both:
        raise ValueError("Matched source claim is not confirmed by either export header; inspect source files")
    scale=float(open_sees_scale)
    if not math.isfinite(scale) or scale<=0:
        raise ValueError("OpenSees scale must be finite positive")
    if both and not math.isclose(scale,1.0,rel_tol=0,abs_tol=1e-12):
        raise ValueError("SeismoMatch accelerations already matched: OpenSees 'scale' MUST be 1.0")
    return dict(status="MATCHED_EXPORTS_ONLY_UNIT_CONVERSION_AT_IMPORT" if both
                     else "ORIGINAL_OR_UNKNOWN_SOURCE_REVIEW_REQUIRED",
       both_headers_identify_matched_outputs=both,
       source_files=rows,additional_opensees_spectral_scale=scale,
       source_unit_conversion_required=True,
       independent_seismomatch_scale_factors_verified=False,
       nbc105_lower_of_pair_rule_verified=False,
       matching_target_formula_verified=False,
       target_period_window_coverage_verified=False,
       warning=("SeismoMatch output waveform does not contain its original scale-factor log. "
                "Do not treat a PGA before/after ratio as the SeismoMatch amplitude-scale factor "
                "when time-domain wavelets modify the spectral shape."))


def screen_fitting_window(matched_min_s,matched_max_s,*,tn90_x_s,tn90_y_s,
                          t1_x_s,t1_y_s,r_mu):
    """NBC 105:2025 §9.3.2.2(b), both plan axes. No guessed modal periods."""
    from components.nonlinear_time_history.nbc105_2025_audit import scaling_period_range
    start=float(matched_min_s);end=float(matched_max_s)
    if not all(math.isfinite(v) for v in (start,end)) or start<0 or end<=start:
        raise ValueError("Invalid SeismoMatch fitted period window")
    ranges={}
    for axis in ("x","y"):
        tn=float({"x":tn90_x_s,"y":tn90_y_s}[axis])
        t1=float({"x":t1_x_s,"y":t1_y_s}[axis])
        lower,upper=scaling_period_range(tn,t1,r_mu)
        ranges[axis]=dict(code_lower_s=lower,code_upper_s=upper,
                          fitted_min_s=start,fitted_max_s=end,
                          covered=(start<=lower+1e-10 and end+1e-10>=upper),
                          short_period_gap_s=max(0.,start-lower),
                          long_period_gap_s=max(0.,upper-end))
    return dict(status="PERIOD_WINDOW_COVERED" if all(x["covered"] for x in ranges.values())
                else "FITTING_WINDOW_DOES_NOT_COVER_NBC_INTERVAL",
                axes=ranges,selected_r_mu=float(r_mu),
                modal_t1_and_tn90_independently_verified=False)
