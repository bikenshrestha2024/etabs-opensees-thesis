"""Accepted-step FVD/BRB recorder. All metrics are demands, NOT qualifications.

Device mapping comes from actual activated override tags; source: OpenSees
ViscousDamper and Steel02 manuals; Korkmaz & Kircil (2026),
doi:10.3390/buildings16040711. Verify force sign in a device benchmark.
"""
import json
import math
from pathlib import Path

def active_device_catalog(folder,frames):
    path=Path(folder)/"OpenSees_Element_Overrides_V125.json"
    if not path.is_file():return []
    config=json.loads(path.read_text(encoding="utf-8-sig"))
    if not config.get("active"):return []
    overrides=config.get("assignments",{})
    result=[]
    for i,frame in enumerate(frames):
        tag=100001+i
        obj=str(frame["object"])
        setting=overrides.get("SOLVER:"+str(tag),overrides.get("FRAME:"+obj,{}))
        kind={"FVD_MAXWELL":"FVD","BRB_STEEL02":"BRB"}.get(setting.get("target"))
        if kind:
            if len(frame.get("nodes",[]))!=2:raise ValueError("Device needs two nodes")
            result.append(dict(tag=tag,kind=kind,source_frame=obj,
                               node_i=int(frame["nodes"][0]),
                               node_j=int(frame["nodes"][1])))
    return result

def _vector(raw):
    if raw is None:return []
    try:return [float(x) for x in raw]
    except TypeError:return [float(raw)]

def _axis(nodes,d):
    a=[float(x) for x in nodes[str(d["node_i"])]]
    b=[float(x) for x in nodes[str(d["node_j"])]]
    v=[b[k]-a[k] for k in range(3)]
    l=math.sqrt(sum(x*x for x in v))
    if not math.isfinite(l) or l<=0:raise ValueError("Device has invalid initial length")
    return [x/l for x in v]

def _project(ops,d,axis,fn):
    a=_vector(fn(d["node_i"]))
    b=_vector(fn(d["node_j"]))
    if len(a)<3 or len(b)<3:raise ValueError("Device node fewer than 3 DOFs")
    return sum((b[k]-a[k])*axis[k] for k in range(3))

def baseline_axial_projection(ops,device,nodes):
    return _project(ops,device,_axis(nodes,device),ops.nodeDisp)

def device_sample(ops,device,nodes,baseline):
    axis=_axis(nodes,device)
    u=_project(ops,device,axis,ops.nodeDisp)-baseline
    v=_project(ops,device,axis,ops.nodeVel)
    response="basicForce" if device["kind"]=="FVD" else "axialForce"
    raw=_vector(ops.eleResponse(device["tag"],response))
    if len(raw)!=1:
        raise ValueError("Device %s: expected scalar %s, got %s" %
                         (device["tag"],response,len(raw)))
    t=float(ops.getTime());f=raw[0]
    if any(not math.isfinite(x) for x in (t,u,v,f)):
        raise ValueError("Nonfinite device recorder")
    return dict(time_s=t,element_tag=device["tag"],
        source_frame=device["source_frame"],device_kind=device["kind"],
        relative_displacement_m=u,relative_velocity_m_s=v,
        signed_force_kN=f,force_response_type=response,
        sign_convention="UNVERIFIED",qualification="DEMAND_ONLY")

def summarize_device_demands(rows):
    by={}
    for r in rows:by.setdefault(r["element_tag"],[]).append(r)
    result=[]
    for tag,s in sorted(by.items()):
        if any(s[i]["time_s"]<=s[i-1]["time_s"] for i in range(1,len(s))):
            raise ValueError("Nonincreasing device sample times")
        f=[r["signed_force_kN"] for r in s]
        v=[r["relative_velocity_m_s"] for r in s]
        u=[r["relative_displacement_m"] for r in s]
        t=[r["time_s"] for r in s]
        work=sum(.5*(f[i-1]*v[i-1]+f[i]*v[i])*(t[i]-t[i-1])
                 for i in range(1,len(s)))
        result.append(dict(element_tag=tag,source_frame=s[0]["source_frame"],
            device_kind=s[0]["device_kind"],samples=len(s),
            peak_force_kN=max(map(abs,f)),
            peak_velocity_m_s=max(map(abs,v)),
            peak_displacement_m=max(map(abs,u)),
            signed_force_velocity_work_kNm=work,
            energy_sign_approved=False,fatigue_validated=False))
    return result
