"""Independent mass-elevation diagnostic for NBC 105:2025 Rayleigh floors.

[REF components/model/assembly.py prepare_complete_export]
[REF components/modal/rayleigh.py run]

This is a diagnostic, not a substitution for the NBC storey lumping rule
or proof of native ETABS/OpenSees equivalence. No OpenSees imports.
"""
from __future__ import annotations

import math

from components.nbc105.constants import GRAVITY_M_S2
from components.nbc105.clause_05_dynamic_characteristics import storey_index_for_elevation


def audit_rayleigh_mass_elevations(model, story_rows, *, g_mass=GRAVITY_M_S2,
                                   tolerance_kN=0.01, z_tolerance_m=1e-7):
    """Reconcile source nodal seismic weight and quantify floor lumping.

    [REF docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md]

    The converter assigns horizontal-active nodes by consecutive floor
    midpoints. This preserves total weight but
    does not preserve mass moments or eigenvector-weighted kinetic energy.
    """
    if not isinstance(model, dict) or not story_rows:
        raise ValueError("Assembled model and Rayleigh story ledger required")
    for name, raw in (("g_mass", g_mass), ("tolerance_kN", tolerance_kN),
                      ("z_tolerance_m", z_tolerance_m)):
        if isinstance(raw, bool) or not isinstance(raw, (float, int)) or not math.isfinite(raw):
            raise ValueError("Invalid Rayleigh mass audit parameter: " + name)
    if g_mass <= 0 or tolerance_kN < 0 or z_tolerance_m < 0:
        raise ValueError("Invalid Rayleigh mass audit tolerance or gravity")
    groups = sorted(model["diaphragms"], key=lambda d: float(d["master_xyz"][2]))
    if len(groups) != len(story_rows):
        raise ValueError("Number of Rayleigh floors differs from source model")
    heights = [float(g["master_xyz"][2]) for g in groups]
    if any(not math.isfinite(z) for z in heights) or any(
            a >= b for a, b in zip(heights, heights[1:])):
        raise ValueError("Invalid diaphragm elevations for mass audit")
    base = float(model["base_z_m"])
    if not math.isfinite(base) or heights[0] <= base:
        raise ValueError("Invalid seismic base for mass audit")
    nodal_mass = model["nodal_mass"]
    points = model["nodes"]
    supports = model["supports"]
    mass_by_floor = [0.0] * len(groups)
    moved_weight = 0.0
    first_moment_shift = 0.0
    max_lift = 0.0
    max_drop = 0.0
    intermediate_nodes = 0
    active_nodes = 0
    mixed_xy_restraint_nodes = 0
    above_roof_nodes = 0
    for key, mass_raw in nodal_mass.items():
        mass = float(mass_raw)
        if not math.isfinite(mass) or mass < 0:
            raise ValueError("Nonfinite or negative source nodal mass")
        if mass == 0:
            continue
        flags = supports.get(str(key), [0] * 6)
        if len(flags) != 6:
            raise ValueError("Unsupported source restraint vector")
        if bool(flags[0]) != bool(flags[1]):
            mixed_xy_restraint_nodes += 1
        if bool(flags[0]) and bool(flags[1]):
            continue
        if str(key) in points:
            xyz = points[str(key)]
        elif isinstance(key, str) and key.isdecimal() and int(key) in points:
            xyz = points[int(key)]
        elif str(key).isdecimal() and int(key) in points:
            xyz = points[int(key)]
        else:
            raise ValueError("Nodal mass point missing from model coordinates")
        z = float(xyz[2])
        if not math.isfinite(z):
            raise ValueError("Nonfinite nodal mass elevation")
        if z < base-z_tolerance_m:
            raise ValueError("Seismic mass below assembled seismic base")
        if z > heights[-1]+z_tolerance_m:
            raise ValueError("Mass node located above uppermost diaphragm")
        floor_index = storey_index_for_elevation(z, heights)
        lift = heights[floor_index]-z
        w = mass*g_mass
        mass_by_floor[floor_index] += w
        active_nodes += 1
        if abs(lift) > z_tolerance_m:
            intermediate_nodes += 1
            moved_weight += w
            first_moment_shift += w*lift
            max_lift = max(max_lift, lift)
            max_drop = max(max_drop, -lift)
    expected_by_floor = []
    for row, group in zip(story_rows, groups):
        if int(row["master_node_tag"]) != int(group["master_tag"]):
            raise ValueError("Mass audit master tags differ from story ledger")
        w = (float(row["dead_load_kN"]) + .6*float(row["storage_live_load_kN"])
             + .3*float(row["other_live_load_kN"]))
        if not math.isfinite(w) or w < 0:
            raise ValueError("Invalid seismic story weight")
        expected_by_floor.append(w)
    differences = [actual-expected for actual,expected in zip(mass_by_floor,expected_by_floor)]
    if any(abs(x) > tolerance_kN for x in differences):
        raise ValueError("Mass audit floor weights fail source seismic ledger reconciliation")
    total = math.fsum(mass_by_floor)
    return {
        "status": "SOURCE_MASS_TOTAL_RECONCILED_VERTICAL_LUMPING_NOT_EIGEN_EQUIVALENCE",
        "source_active_horizontal_weight_kN": total,
        "floor_count": len(groups),
        "active_mass_node_count": active_nodes,
        "intermediate_mass_node_count": intermediate_nodes,
        "intermediate_mass_weight_kN": moved_weight,
        "intermediate_mass_weight_fraction": moved_weight/total if total else 0,
        "vertical_first_moment_shift_kN_m": first_moment_shift,
        "vertical_shift_weighted_mean_m": first_moment_shift/total if total else 0,
        "maximum_upward_lump_m": max_lift,
        "maximum_downward_lump_m": max_drop,
        "mixed_XY_support_node_count": mixed_xy_restraint_nodes,
        "mass_nodes_above_roof": above_roof_nodes,
        "maximum_floor_weight_discrepancy_kN": max(map(abs, differences), default=0),
        "floor_weights_from_nodal_mass_kN": mass_by_floor,
        "floor_weights_from_source_ledger_kN": expected_by_floor,
        "open_engineering_checks": [
            "This is an exact source bookkeeping check only, not a full eigen mass operator comparison",
            "Check intermediate-node eigenvector shape and consistent mass work versus floor lumping",
            "Check axis-specific restraint and diaphragm constraints against ETABS",
            "Check P-Delta tangent, stiffness modifiers, gravity state and source model identity",
        ],
    }
