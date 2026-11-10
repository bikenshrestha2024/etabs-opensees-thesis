"""ETABS-independent OpenSeesPy static benchmark runner.

No import-time dependency on OpenSeesPy, CSI/ETABS, COM, or a GUI.
The currently working full-building analyses remain in components/.
"""
from __future__ import annotations
import math
from src.thesis_core.neutral_model import validate_model,model_sha256

def run_standalone(data,ops=None):
    validate_model(data)
    if ops is None:
        import openseespy.opensees as ops
    # An independent domain; no ETABS project, saved EDB, or source arrays.
    ops.wipe()
    ops.model("basic","-ndm",3,"-ndf",6)
    nodes=data["nodes"];element=data["elements"][0];section=element["section"]
    for n in nodes:
        ops.node(n["tag"],*n["xyz"])
        if any(n["fixity"]):ops.fix(n["tag"],*n["fixity"])
    ops.geomTransf("Linear",1,*element["vecxz"])
    i,j=element["nodes"]
    ops.element("elasticBeamColumn",element["tag"],i,j,
                *[section[k] for k in ("A","E","G","J","Iy","Iz")],1)
    ops.timeSeries("Linear",1)
    ops.pattern("Plain",1,1)
    for record in data["loads"]:
        ops.load(record["node"],*record["force"])
    ops.constraints("Plain");ops.numberer("RCM");ops.system("BandGeneral")
    ops.test("NormDispIncr",1e-10,25)
    ops.algorithm("Newton");ops.integrator("LoadControl",1.0)
    ops.analysis("Static")
    code=ops.analyze(1)
    if code!=0:raise RuntimeError("Standalone benchmark did not converge: "+str(code))
    ops.reactions()
    displacement={str(n["tag"]):[float(ops.nodeDisp(n["tag"],k))
                                  for k in range(1,7)] for n in nodes}
    reaction={str(n["tag"]):[float(ops.nodeReaction(n["tag"],k))
                              for k in range(1,7)] for n in nodes
                              if any(n["fixity"])}
    for values in list(displacement.values())+list(reaction.values()):
        if any(not math.isfinite(x) for x in values):
            raise RuntimeError("Non-finite OpenSees benchmark output")
    external=[sum(record["force"][i] for record in data["loads"]) for i in range(3)]
    restrained=[sum(value[i] for value in reaction.values()) for i in range(3)]
    residual=[external[i]+restrained[i] for i in range(3)]
    scale=max(1.0,max(abs(x) for x in external))
    if max(abs(x) for x in residual)>1e-6*scale:
        raise RuntimeError("Global axial/translational force equilibrium FAILED")
    return {"schema":"standalone-ops-benchmark-v1","model_sha256":model_sha256(data),
            "status":"NUMERICALLY_CONVERGED_ONLY",
            "etabs_equivalence":"NOT_APPLICABLE",
            "full_building_validation":"NOT_PERFORMED",
            "displacement_m_and_rad":displacement,
            "reaction_kN_and_kNm":reaction,"force_residual_kN":residual}

def axial_cantilever_check(data,results,relative_tolerance=0.002):
    """Independent analytical axial solution, only for synthetic cantilever."""
    if len(data["nodes"])!=2 or len(data["elements"])!=1 or len(data["loads"])!=1:
        raise ValueError("Only two-node axial cantilever benchmark supported")
    member=data["elements"][0];ends=member["nodes"]
    p=data["loads"][0]
    if p["node"]!=ends[1] or any(abs(p["force"][i])>1e-12 for i in (0,1,3,4,5)):
        raise ValueError("Expected pure axial gravity tip load")
    first,next_=data["nodes"]
    L=math.dist(first["xyz"],next_["xyz"])
    if abs(next_["xyz"][2]-first["xyz"][2])<L-1e-9:
        raise ValueError("Analytical comparison requires vertical member")
    expected=p["force"][2]*L/(member["section"]["A"]*member["section"]["E"])
    actual=results["displacement_m_and_rad"][str(next_["tag"])][2]
    error=abs(actual-expected)/max(abs(expected),1e-30)
    return {"expected_uz_m":expected,"actual_uz_m":actual,
            "relative_error":error,"pass":error<=relative_tolerance}
