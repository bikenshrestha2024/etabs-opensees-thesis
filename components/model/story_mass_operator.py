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


def compare_etabs_object_lumped_mass(model, connectivity, mass_factors, reference_rows, *,
                                    reference_g_m_s2):
    """Reconstruct the exported ETABS mass ledger on original object joints.

    [REF docs/source/components/model/story_mass_operator.py.md]
    Equal endpoint/corner sharing is an explicit comparison hypothesis, not a
    force-transfer or native solver mass law. Keep all base mass separate and
    use the existing ETABS reference linear-split convention. Replay the
    archived refined nodal mass from its source ledger first. No masses,
    fixities or project gravity constants are changed.
    """
    from collections import defaultdict
    from components.modal.storey_mass_convention import (
        BASE, ETABS_BASE_ROW_LINEAR_SPLIT, storey_shares)
    from components.nbc105.constants import GRAVITY_M_S2

    def finite(value):
        if isinstance(value, bool) or not math.isfinite(float(value)):
            raise ValueError("Nonfinite or boolean reference quantity")
        return float(value)

    def xyz(values):
        if len(values) != 3:
            raise ValueError("Expected three coordinates")
        return tuple(finite(v) for v in values)

    g = finite(reference_g_m_s2)
    if g <= 0:
        raise ValueError("Positive explicit reference gravity required")
    nodes = {str(k): xyz(v) for k, v in model["nodes"].items()}
    original = {}
    tags = set()
    for row in connectivity["node_map"]:
        uid, tag = str(row["etabs_point_name"]), str(row["opensees_node_tag"])
        if (not uid or uid in original or tag in tags or tag not in nodes
                or math.dist(nodes[tag], xyz(row["coordinates_m"])) > 1e-7):
            raise ValueError("Original point identity/coordinate mismatch")
        original[uid] = tag
        tags.add(tag)
    owners = {}
    for row in connectivity["elements"]:
        dim = row["dimension"]
        if dim not in ("line_2_node", "area_polygon"):
            raise ValueError("Unsupported original source object geometry")
        kind, count = ("FRAME:", 2) if dim == "line_2_node" else ("AREA:", 4)
        key = kind + str(row["etabs_object"])
        ns = tuple(map(str, row["node_tags"]))
        if (key in owners or len(ns) != count or len(set(ns)) != count
                or tuple(original.get(str(n)) for n in row["node_names"]) != ns):
            raise ValueError("Original source object identity mismatch: " + key)
        owners[key] = ns
    object_weights, nodal_weights = defaultdict(float), defaultdict(float)
    for row in model["load_provenance"]:
        owner, node, pattern = row["source"], str(row["node"]), row["pattern"]
        if owner not in owners or node not in nodes or pattern not in mass_factors:
            raise ValueError("Source load ledger owner/node/pattern missing")
        factor, weight = finite(mass_factors[pattern]), finite(row["downward_kN"])
        if factor not in (0., .3, .6, 1.) or weight < 0:
            raise ValueError("Unsupported source load ledger weight/factor")
        object_weights[owner] += weight * factor
        nodal_weights[node] += weight * factor
    masses = {str(k): finite(v) for k, v in model["nodal_mass"].items()}
    if (not masses or not object_weights or set(masses) != set(nodes)
            or set(nodal_weights) - set(masses)
            or any(m < 0 or not math.isclose(nodal_weights[n] / GRAVITY_M_S2, m,
                       rel_tol=1e-9, abs_tol=1e-8) for n, m in masses.items())):
        raise ValueError("Refined nodal mass differs from source load ledger")
    coarse = defaultdict(float)
    for owner, weight in object_weights.items():
        for n in owners[owner]:
            coarse[n] += weight / (g * len(owners[owner]))
    groups = sorted(model["diaphragms"], key=lambda row: xyz(row["master_xyz"])[2])
    heights = [xyz(row["master_xyz"])[2] for row in groups]
    base = finite(model["base_z_m"])
    if (not groups or heights[0] <= base or any(a >= b for a,b in zip(heights, heights[1:]))
            or len({row["storey_number"] for row in groups}) != len(groups)):
        raise ValueError("Invalid original floor geometry")
    expected = {f"Story{row['storey_number']}": i for i, row in enumerate(groups)}
    reference = {}
    base_ref = [0., 0.]
    base_rows = 0
    for row in reference_rows:
        story = row["Story"]
        mx, my, jz = (finite(row[k]) for k in ("UX", "UY", "RZ"))
        p = xyz([row[k] for k in "XYZ"])
        if min(mx, my, jz) < 0:
            raise ValueError("Negative reference mass or inertia")
        if story == "Base":
            if abs(p[2] - base) > 1e-7:
                raise ValueError("Base mass coordinate differs from source base")
            base_rows += 1
            base_ref[0] += mx / 1000
            base_ref[1] += my / 1000
        elif story not in expected:
            raise ValueError("Unmatched reference story: " + story)
        elif mx or my or jz:
            if (story in reference or min(mx, my) <= 0 or
                    math.dist(p, xyz(groups[expected[story]]["master_xyz"])) > 1e-6):
                raise ValueError("Reference mass concentration/coordinate mismatch: " + story)
            reference[story] = (mx/1000, my/1000, jz)
    if not base_rows or set(reference) != set(expected):
        raise ValueError("Missing base or floor mass reference")
    # Generalized in-plane rigid-diaphragm kinetic energy matrix, about the
    # reported master: [[M,0,-sum(m dy)],[0,M,sum(m dx)],[...,Jz]].
    terms = defaultdict(lambda: [0., 0., 0., 0.])
    for n, mass in coarse.items():
        x,y,z = nodes[n]
        if z < base - 1e-7 or z > heights[-1] + 1e-7:
            raise ValueError("Source mass lies outside floor elevations")
        for i, fraction in storey_shares(z, heights, base, ETABS_BASE_ROW_LINEAR_SPLIT):
            value = mass * fraction
            terms[i][0] += value
            if i != BASE:
                cx,cy,_ = xyz(groups[i]["master_xyz"])
                dx,dy = x-cx,y-cy
                terms[i][1] -= value * dy
                terms[i][2] += value * dx
                terms[i][3] += value * (dx*dx + dy*dy)
    rows = []
    for story, i in expected.items():
        mass, xr, yr, jz = terms[i]
        mx,my,jref = reference[story]
        rows.append({"story":story,"reference_UX_t":mx,"reference_UY_t":my,
                     "reference_RZ_t_m2":jref,"mass_t":mass,"Jz_t_m2":jz,
                     "mass_residual_X_t":mass-mx,"mass_residual_Y_t":mass-my,
                     "RZ_residual_t_m2":jz-jref,
                     "horizontal_reference_matrix":[[mass,0.,xr],[0.,mass,yr],[xr,yr,jz]]})
    base_mass = terms[BASE][0]
    total = math.fsum(object_weights.values()) / g
    if not math.isclose(base_mass + math.fsum(row["mass_t"] for row in rows), total,
                        rel_tol=1e-10, abs_tol=1e-8):
        raise ValueError("Original-object reference mass is not conserved")
    return {"status":"OBJECT_LUMPED_REFERENCE_DIAGNOSTIC_ONLY",
            "native_mass_matrix_equivalence":"NOT_VERIFIED", "source_model_identity":"UNVERIFIED",
            "reference_g_m_s2":g,"project_g_m_s2":GRAVITY_M_S2,
            "original_weighted_objects":len(object_weights),"base_mass_t":base_mass,
            "reference_base_UX_t":base_ref[0],"reference_base_UY_t":base_ref[1],
            "base_residual_X_t":base_mass-base_ref[0],"base_residual_Y_t":base_mass-base_ref[1],
            "total_reference_basis_mass_t":total,"floors":rows,
            "limitations":["Equal object sharing can change first moments of individual loads; diagnostic only.",
                           "Generalized reference matrix is reconstructed, not a native OpenSees matrix.",
                           "No solver masses, restraints or NBC load factors are replaced."]}
