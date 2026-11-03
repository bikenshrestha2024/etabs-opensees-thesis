"""Seven-variant, source-hashed outrigger comparison (M0 through M6).

Consumes existing, completed research case summaries and verified source
cross-model invariants. Does NOT run OpenSees or label preliminary metrics as
an experimentally validated optimum. Context: NBC 105:2025, three orthogonal
pairs for torsionally sensitive 3D models; Korkmaz & Kircil 2026 FVD studies.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

VARIANTS={
"M0":"No outrigger","M1":"Conventional outrigger",
"M2":"Damped conventional outrigger","M3":"Conventional + belt",
"M4":"Damped + belt","M5":"Conventional + belt + cap",
"M6":"Damped + belt + cap"}
METRICS=("peak_roof_UX_m","peak_roof_UY_m","max_story_drift_X",
         "max_story_drift_Y","peak_base_shear_X_kN","peak_base_shear_Y_kN",
         "peak_roof_torsion_rad")
INVARIANTS=("geometry_basis_sha256","mass_basis_sha256",
            "ground_motion_set_sha256","analysis_settings_sha256")


def validate_variant_manifest(payload):
    """Accept only explicit source provenance, not assumed equal models."""
    rows=payload.get("variants")
    if not isinstance(rows,list) or {r.get("variant") for r in rows}!=set(VARIANTS):
        raise ValueError("Exactly one entry is required for each M0–M6 variant")
    if len(rows)!=len(VARIANTS):
        raise ValueError("Duplicate or extra model variant")
    for key in INVARIANTS:
        values={str(r.get(key,"")).strip() for r in rows}
        if len(values)!=1 or not next(iter(values)):
            raise ValueError(f"Comparison cannot hold {key} invariant")
        val=next(iter(values))
        if len(val)!=64 or any(ch not in "0123456789abcdefABCDEF" for ch in val):
            raise ValueError(f"Invalid fingerprint for {key}")
    for r in rows:
        if not r.get("model_export_path") or not r.get("model_file_sha256"):
            raise ValueError(f"{r['variant']}: missing independent model export/hash")
        if not isinstance(r.get("outrigger_floors"),list):
            raise ValueError(f"{r['variant']}: outrigger floors must be listed")
        if r["variant"]=="M0" and r["outrigger_floors"]:
            raise ValueError("M0 must be the no-outrigger baseline")
    return rows


def compare_completed_cases(payload, summaries, *, require_pairs=3):
    """Compare matched full-duration, finite research outcomes, not code approval.

    summaries contains one list-of-dicts per variant, each with one row per
    limit-state / pair-id / XY-or-YX. Requires equivalent sets and complete
    numerical-screen evidence for every case; no omitted failures.
    """
    validate_variant_manifest(payload)
    if set(summaries)!=set(VARIANTS):
        raise ValueError("All M0–M6 case collections are required")
    grouped={}
    for variant,cases in summaries.items():
        if not isinstance(cases,list) or not cases:raise ValueError(variant+" has no completed cases")
        keyed={}
        for c in cases:
            key=(c.get("limit_state"),c.get("pair_id"),c.get("orientation"))
            if key in keyed:raise ValueError(f"{variant} duplicate case {key}")
            if key[0] not in ("ULS","SLS") or key[2] not in ("XY","YX") or not key[1]:
                raise ValueError(f"{variant} unsupported case key {key}")
            gate=c.get("completion_gate",{})
            if not gate.get("full_record_completed") or gate.get("status")!="FULL_DURATION_NUMERIC_SCREEN":
                raise ValueError(f"{variant} case {key} not a full-duration numerical screen")
            if gate.get("accepted_channels_finite") is not True:
                raise ValueError(f"{variant} case {key} has unverified finite channels")
            if c.get("record_sha256") is None:
                raise ValueError(f"{variant} case {key} has no ground motion hash")
            for name in METRICS:
                value=float(c[name])
                if not math.isfinite(value) or value<0:
                    raise ValueError(f"{variant} invalid metric {name}")
            keyed[key]=c
        grouped[variant]=keyed
    reference=grouped["M0"]
    keys=set(reference)
    for variant,cases in grouped.items():
        if set(cases)!=keys:
            raise ValueError(f"{variant}: missing/extra paired case relative to M0")
        for key,c in cases.items():
            if c["record_sha256"]!=reference[key]["record_sha256"]:
                raise ValueError(f"{variant}: motion source SHA differs in {key}")
    for limit in ("ULS","SLS"):
        pairs={key[1] for key in keys if key[0]==limit}
        if len(pairs)<require_pairs:
            raise ValueError(f"{limit}: fewer than {require_pairs} pairs")
        if any((limit,p,o) not in keys for p in pairs for o in ("XY","YX")):
            raise ValueError(f"{limit}: both XY and YX must exist for each pair")
    results={}
    for variant,by in grouped.items():
        results[variant]={}
        for metric in METRICS:
            worst=max(case[metric] for case in by.values())
            base=max(case[metric] for case in reference.values())
            results[variant][metric]={"maximum":worst,
                "M0_maximum":base,
                "reduction_percent":100*(base-worst)/base if base>0 else None}
    return dict(status="RESEARCH_SCREEN_ONLY_NOT_THESIS_VALIDATION",
                compared_variants=list(VARIANTS),
                paired_case_keys=len(keys),results=results,
                no_experimental_approval=True,
                warning="Numerical comparative screens only; all model/component acceptance gates still required.")


def load_case_manifest(path):
    manifest=Path(path)
    payload=json.loads(manifest.read_text(encoding="utf-8-sig"))
    variants=validate_variant_manifest(payload)
    collected={}
    for record in variants:
        files=record.get("case_summary_files",[])
        if not files:raise ValueError(record["variant"]+" missing case summary file list")
        items=[]
        for name in files:
            p=Path(name)
            if not p.is_absolute():p=manifest.parent/p
            data=json.loads(p.read_text(encoding="utf-8-sig"))
            items.append(data)
        collected[record["variant"]]=items
    return compare_completed_cases(payload,collected)
