"""Paper specimen reference-data validation; does not overwrite building RC design.

Source: Kolozvari, Orakcal & Wallace, PEER 2015/12 Sections 3.2.1–3.2.2.
RW2 = Thomsen and Wallace (1995), RW-A15-P10-S78 = Tran and Wallace (2012).
"""
import json
import math
from pathlib import Path

INCH_TO_M=0.0254
KSI_TO_MPA=6.894757293168361

def validate_specimen_register(path):
    payload=json.loads(Path(path).read_text(encoding="utf-8"))
    if not payload.get("source",{}).get("report","").startswith("Kolozvari"):
        raise ValueError("Wrong experiment-source register")
    specimens=payload.get("specimens")
    if not isinstance(specimens,list) or not specimens:
        raise ValueError("Missing specimens")
    names=set()
    for sp in specimens:
        name=str(sp.get("specimen_id",""))
        if name in names or not name:
            raise ValueError("Duplicate/empty specimen")
        names.add(name)
        if sp.get("project_transfer_approved") is not False:
            raise ValueError("Published specimen is not a project-approved section")
        for k in ("width_in","thickness_in","height_in"):
            v=float(sp[k])
            if not math.isfinite(v) or v<=0:
                raise ValueError(f"{name}: invalid {k}")
        sp["geometry_m"]={k.removesuffix("_in")+"_m":float(sp[k])*INCH_TO_M
                          for k in ("width_in","thickness_in","height_in")}
    return payload

def specimen_benchmark_only(specimen):
    """Generate benchmark labels without modifying any project fiber sections."""
    if specimen.get("project_transfer_approved") is not False:
        raise ValueError("Cannot silently approve specimen parameters for building")
    return {"specimen_id":specimen["specimen_id"],
            "source_locator":specimen["source_locator"],
            "reinforcement_note":specimen["boundary_reinforcement"],
            "project_section_overwrite_allowed":False,
            "numerical_validation":"NOT_RUN"}
