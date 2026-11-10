"""Versioned, ETABS-independent neutral elastic benchmark model.

Scope: one 3D linear elastic beam-column with nodal loading and fixed nodes.
NOT a substitute for RCC wall/shell, nonlinear, seismic or full-building model.
Exact units: kN, m, s; stress and Young's modulus: kN/m2.
"""
from __future__ import annotations
import hashlib
import json
import math

SCHEMA_VERSION="0.1.0"
REQUIRED_SECTION=("A","E","G","J","Iy","Iz")

def _positive_number(value, context):
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        raise ValueError(context+" must be a numeric scalar")
    number=float(value)
    if not math.isfinite(number) or number<=0:
        raise ValueError(context+" must be finite and positive")
    return number

def _numeric_vector(value,n,context):
    if not isinstance(value,(list,tuple)) or len(value)!=n:
        raise ValueError(context+" must contain exactly "+str(n)+" values")
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or
           not math.isfinite(float(v)) for v in value):
        raise ValueError(context+" must be a finite numerical vector")
    return [float(v) for v in value]

def validate_model(data):
    """Validate a minimal benchmark contract; unsupported capabilities fail closed."""
    if not isinstance(data,dict):raise ValueError("Neutral model must be a mapping")
    if data.get("schema_version")!=SCHEMA_VERSION:
        raise ValueError("Unsupported neutral schema version; explicit migration required")
    if data.get("units")!="kN-m-s":
        raise ValueError("Only explicitly declared kN-m-s is supported")
    if data.get("mode") not in ("standalone","benchmark"):
        raise ValueError("Only standalone or benchmark source mode allowed")
    nodes=data.get("nodes");elements=data.get("elements");loads=data.get("loads")
    if not isinstance(nodes,list) or len(nodes)<2:
        raise ValueError("At least two nodes required")
    if not isinstance(elements,list) or len(elements)!=1:
        raise ValueError("Only ONE 3D elastic beam-column element supported")
    if not isinstance(loads,list) or not loads:
        raise ValueError("Explicit nodal loads required")
    ids=set();coords={};fixed=0
    for i,node in enumerate(nodes):
        if not isinstance(node,dict):raise ValueError("Invalid node record")
        tag=node.get("tag")
        if not isinstance(tag,int) or isinstance(tag,bool) or tag<=0 or tag in ids:
            raise ValueError("Duplicate or invalid node tag")
        ids.add(tag);coords[tag]=_numeric_vector(node.get("xyz"),3,"node.xyz")
        f=node.get("fixity")
        if not isinstance(f,list) or len(f)!=6 or any(x not in (0,1) for x in f):
            raise ValueError("Every node needs six explicit binary fixity values")
        if all(f):fixed+=1
    if fixed<1:raise ValueError("At least one fully restrained 3D node required")
    element=elements[0]
    if element.get("type")!="elasticBeamColumn3D":
        raise ValueError("Unsupported element type; no shell/wall/device substitution")
    ends=element.get("nodes")
    if not isinstance(ends,list) or len(ends)!=2 or ends[0]==ends[1] or any(t not in ids for t in ends):
        raise ValueError("Element endpoints not mapped to two different nodes")
    tag=element.get("tag")
    if not isinstance(tag,int) or tag<=0:raise ValueError("Invalid element tag")
    if math.dist(coords[ends[0]],coords[ends[1]])<=1e-9:
        raise ValueError("Zero-length elastic beam")
    section=element.get("section")
    if not isinstance(section,dict) or set(section)!=set(REQUIRED_SECTION):
        raise ValueError("Exactly A/E/G/J/Iy/Iz section data required")
    for name in REQUIRED_SECTION:_positive_number(section[name],"section."+name)
    vxz=_numeric_vector(element.get("vecxz"),3,"local vecxz")
    direction=[coords[ends[1]][k]-coords[ends[0]][k] for k in range(3)]
    cross=[direction[1]*vxz[2]-direction[2]*vxz[1],
           direction[2]*vxz[0]-direction[0]*vxz[2],
           direction[0]*vxz[1]-direction[1]*vxz[0]]
    if math.sqrt(sum(a*a for a in cross)) <= 1e-9:
        raise ValueError("vecxz is parallel to member axis")
    if not any(not all(n["fixity"]) for n in nodes):
        raise ValueError("No unconstrained degrees of freedom")
    for load in loads:
        if load.get("node") not in ids:
            raise ValueError("Nodal load references unknown node")
        _numeric_vector(load.get("force"),6,"nodal load vector")
    if set(data)-{"schema_version","units","mode","nodes","elements","loads","source"}:
        raise ValueError("Unknown schema fields; no silent field discard")
    if not isinstance(data.get("source"),dict) or not data["source"].get("description"):
        raise ValueError("Model source description and provenance required")
    return data

def model_sha256(data):
    validate_model(data)
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()

def cantilever_example():
    """One axial-gravity elastic column: analytical Uz = -P*L/(A*E)."""
    return validate_model({
        "schema_version":SCHEMA_VERSION,"mode":"standalone","units":"kN-m-s",
        "source":{"description":"Synthetic axial cantilever; NOT the thesis building"},
        "nodes":[{"tag":1,"xyz":[0,0,0],"fixity":[1]*6},
                 {"tag":2,"xyz":[0,0,3],"fixity":[0]*6}],
        "elements":[{"tag":1,"nodes":[1,2],"type":"elasticBeamColumn3D",
                     "section":{"A":0.25,"E":3.0e7,"G":1.25e7,
                                "J":0.01,"Iy":0.01,"Iz":0.01},
                     "vecxz":[0,1,0]}],
        "loads":[{"node":2,"force":[0,0,-100,0,0,0]}],
    })
