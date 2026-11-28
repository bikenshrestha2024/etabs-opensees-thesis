"""Optional NBC story-centre seismic mass aggregation, without altering geometry.

[REF NBC105-2025 §5.2 Table 5-1; printed p.30]
[REF components/modal/rayleigh_mass_audit.py audit_rayleigh_mass_elevations]
[REF engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md]

The default mass operator stays SOURCE_DISTRIBUTED pending ETABS mode/MPC
equivalence. A user may explicitly request STORY_LUMPED_NBC; the master
receives horizontal translational mass and polar Jz, while original node
vertical mass remains. This changes dynamic physics and is not acceptance.
"""
from __future__ import annotations

import math
from components.nbc105.clause_05_dynamic_characteristics import storey_index_for_elevation


def story_lumped_mass_plan(model, *, center_tolerance_m=0.001):
    """Compute source-conservative horizontal floor mass and polar inertias.

    [REF NBC105-2025 §5.2, printed p.30]
    [REF components/model/assembly.py build_complete_model]
    """
    if not isinstance(model,dict):
        raise ValueError("Assembled model dictionary is required")
    groups=sorted(model["diaphragms"],key=lambda x:float(x["master_xyz"][2]))
    if not groups:
        raise ValueError("At least one source rigid diaphragm is required")
    heights=[float(d["master_xyz"][2]) for d in groups]
    base=float(model["base_z_m"])
    if not math.isfinite(base) or heights[0]<=base or any(
        not math.isfinite(v) or v<=u for u,v in zip(heights,heights[1:])):
        raise ValueError("Invalid floor heights or seismic base")
    tol=float(center_tolerance_m)
    if not math.isfinite(tol) or tol<0:
        raise ValueError("Invalid mass center tolerance")
    stats=[dict(mass=0.,mass_x=0.,mass_y=0.,Jz=0.,source_nodes=0,
                intermediate_nodes=0) for _ in groups]
    active=0.;intermediate=0.;active_nodes=0
    nodes=model["nodes"]
    for tag,mass_raw in model["nodal_mass"].items():
        mass=float(mass_raw)
        if not math.isfinite(mass) or mass<0:
            raise ValueError("Nonfinite or negative model nodal mass")
        if not mass: continue
        flags=model["supports"].get(str(tag),[0]*6)
        if len(flags)!=6:
            raise ValueError("Source node support vector must have six DOFs")
        if bool(flags[0])!=bool(flags[1]):
            raise ValueError("Horizontal source restraint is anisotropic; a single scalar story mass cannot preserve it")
        if bool(flags[0]) and bool(flags[1]):
            continue
        xyz=nodes.get(str(tag),nodes.get(int(tag)) if str(tag).isdecimal() else None)
        if xyz is None:
            raise ValueError("Source seismic mass node coordinates missing: "+str(tag))
        x,y,z=map(float,xyz)
        if not all(map(math.isfinite,(x,y,z))) or z<base-1e-7 or z>heights[-1]+1e-7:
            raise ValueError("Source seismic mass outside the seismic diaphragm elevations")
        i=storey_index_for_elevation(z,heights)
        center=groups[i]["master_xyz"]
        dx=x-float(center[0]);dy=y-float(center[1])
        rec=stats[i]
        rec["mass"]+=mass
        rec["mass_x"]+=mass*x
        rec["mass_y"]+=mass*y
        rec["Jz"]+=mass*(dx*dx+dy*dy)
        rec["source_nodes"]+=1
        active+=mass
        active_nodes+=1
        if abs(z-heights[i])>1e-7:
            intermediate+=mass
            rec["intermediate_nodes"]+=1
    plan={}
    for g,s in zip(groups,stats):
        mass=s["mass"]
        if mass<=0:raise ValueError("Floor "+str(g["storey_number"])+" has no active seismic mass")
        x=s["mass_x"]/mass;y=s["mass_y"]/mass
        mx,my=map(float,g["master_xyz"][:2])
        if math.hypot(x-mx,y-my)>tol:
            raise ValueError("Floor mass center/centroid differs from diaphragm master: "+str(g["storey_number"]))
        plan[int(g["master_tag"])]=dict(
            mass=mass,Jz=s["Jz"],mass_center_x_m=x,mass_center_y_m=y,
            original_master_x_m=mx,original_master_y_m=my,
            source_nodes=s["source_nodes"],intermediate_nodes=s["intermediate_nodes"],
            storey_number=int(g["storey_number"]))
    return dict(plan_status="STORY_LUMPING_NUMERICALLY_RECONCILED_NOT_NATIVE_ACCEPTED",
                horizontal_mass_by_master=plan,active_source_horizontal_mass=active,
                intermediate_mass=intermediate,active_source_node_count=active_nodes,
                unassigned_horizontal_mass=active-sum(rec["mass"] for rec in plan.values()),
                native_etabs_dynamic_mass_equivalence="NOT_VERIFIED")


def compare_etabs_story_mass(model, reference_rows, *, coordinate_tolerance_m=1e-6):
    """Compare assembled INPUT floor mass and polar inertia, never a solved matrix.

    [REF docs/source/components/model/story_mass_operator.py.md]
    Expects verified Assembled Joint Masses rows (kg, ton-m², m), with one
    concentrated horizontal mass/inertia record per StoryN and base excluded.
    Source-distributed mass and geometry remain unchanged.
    """
    plan=story_lumped_mass_plan(model)
    tol=float(coordinate_tolerance_m)
    if not math.isfinite(tol) or tol<0:
        raise ValueError("Invalid coordinate tolerance")
    groups={int(g['storey_number']):g for g in model['diaphragms']}
    if len(groups)!=len(model['diaphragms']):
        raise ValueError("Duplicate diaphragm storey numbers")
    expected={f'Story{i}':i for i in groups}
    by_story={}
    for row in reference_rows:
        if row['Story']=='Base':
            continue
        story=row['Story']
        if story not in expected:
            raise ValueError("Unmatched reference story: "+str(story))
        mx,my,jz,x,y,z=(float(row[k]) for k in ('UX','UY','RZ','X','Y','Z'))
        if not all(math.isfinite(v) for v in (mx,my,jz,x,y,z)) or min(mx,my,jz)<0:
            raise ValueError("Invalid ETABS mass or coordinate")
        if mx==my==jz==0:
            continue
        if min(mx,my)<=0 or story in by_story:
            raise ValueError("Expected one concentrated horizontal mass row per story: "+story)
        i=expected[story]
        distance=math.dist((x,y,z),groups[i]['master_xyz'])
        if distance>tol:
            raise ValueError("ETABS mass location differs from diaphragm master: "+story)
        by_story[story]=(mx/1000,my/1000,jz,distance)
    if set(by_story)!=set(expected):
        raise ValueError("Missing reference horizontal floor masses")
    floors=[]
    for rec in sorted(plan['horizontal_mass_by_master'].values(),key=lambda r:r['storey_number']):
        story=f"Story{rec['storey_number']}"
        mx,my,jz,distance=by_story[story]
        m=rec['mass'];j=rec['Jz']
        floors.append(dict(story=story,etabs_UX_t=mx,etabs_UY_t=my,etabs_RZ_t_m2=jz,
            assembled_mass_t=m,assembled_polar_inertia_t_m2=j,
            UX_difference_t=m-mx,UY_difference_t=m-my,RZ_difference_t_m2=j-jz,
            UX_difference_percent=100*(m-mx)/mx,UY_difference_percent=100*(m-my)/my,
            RZ_difference_percent=(100*(j-jz)/jz if jz else None),master_coordinate_distance_m=distance))
    return dict(status='ASSEMBLED_INPUT_COMPARISON_NOT_NATIVE_MASS_MATRIX',
                native_mass_matrix_equivalence='NOT_VERIFIED',source_model_identity='UNVERIFIED',
                floors=floors,active_assembled_mass_t=plan['active_source_horizontal_mass'],
                etabs_UX_t=math.fsum(r['etabs_UX_t'] for r in floors),
                etabs_UY_t=math.fsum(r['etabs_UY_t'] for r in floors),
                intermediate_mass_t=plan['intermediate_mass'])
