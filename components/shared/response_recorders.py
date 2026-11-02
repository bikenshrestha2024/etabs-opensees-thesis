"""Shared response recorder exports for gravity and seismic analysis cases."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path


REACTION_COMPONENTS = (
    "support_reaction_Fx_kN",
    "support_reaction_Fy_kN",
    "support_reaction_Fz_kN",
    "support_reaction_Mx_kNm",
    "support_reaction_My_kNm",
    "support_reaction_Mz_kNm",
)
FRAME_SOLVER_TAG_BASE = 100001


def frame_solver_tag_catalog(frames):
    """Map the stable assembled frame solver tags back to ETABS frame objects."""
    return [
        {
            "solver_tag": FRAME_SOLVER_TAG_BASE + index,
            "source_object": str(element.get("object", "")),
            "category": str(element.get("category", "")),
            "section_property": str(element.get("properties", {}).get("section", "")),
            "node_i": int(element["nodes"][0]),
            "node_j": int(element["nodes"][1]),
            "release_i": bool(element.get("release_i", False)),
            "release_j": bool(element.get("release_j", False)),
        }
        for index, element in enumerate(frames)
    ]


def active_device_catalog(frames, scenario):
    """Return all active FVD/BRB frame assignments with their stable solver tags."""
    if not scenario.get("active"):
        return []
    assignments = scenario.get("assignments", {})
    devices = []
    for index, element in enumerate(frames):
        tag = FRAME_SOLVER_TAG_BASE + index
        selection = assignments.get(
            "SOLVER:" + str(tag),
            assignments.get("FRAME:" + str(element.get("object", "")), {}),
        )
        if selection.get("target") not in ("FVD_MAXWELL", "BRB_STEEL02"):
            continue
        devices.append({
            "element_tag": tag,
            "source_object": str(element.get("object", "")),
            "device_type": selection["target"],
            "parameters": selection.get("parameters", {}),
            "citation": str(selection.get("citation", "")),
            "node_tags": element["nodes"],
        })
    return devices


def support_resultants(ops, support_nodes):
    """Return signed summed support reactions; call after each converged state."""
    supports = [int(node) for node in support_nodes]
    if not supports:
        raise ValueError("At least one support node is required for reaction recording.")
    ops.reactions()
    values = [sum(float(ops.nodeReaction(node, dof)) for node in supports)
              for dof in range(1, 7)]
    return dict(zip(REACTION_COMPONENTS, values))


def write_rows(path, rows):
    rows = list(rows)
    if not rows:
        raise ValueError(f"Cannot write an empty response recorder: {path}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(
            key for row in rows for key in row)))
        writer.writeheader()
        writer.writerows(rows)
    return target


def write_recorder_index(output_dir, analysis, files, notes=(),
                         filename="Response_Recorder_Index.json"):
    target = Path(output_dir) / str(filename)
    payload = {
        "analysis": str(analysis),
        "files": [dict(name=str(name), channels=list(channels))
                  for name, channels in files],
        "notes": list(notes),
        "units": {"displacement": "m", "velocity": "m/s", "rotation": "rad",
                  "force": "kN", "moment": "kN m", "energy": "kN m",
                  "power": "kN m/s", "time": "s", "drift": "dimensionless"},
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def append_base_shear(row, ops, support_nodes, baseline=None):
    """Add signed incremental base shears and six support resultants to a sample."""
    current = support_resultants(ops, support_nodes)
    reference = baseline or {}
    for key, value in current.items():
        row[key] = value - float(reference.get(key, 0.0))
    row["base_shear_X_kN"] = -row["support_reaction_Fx_kN"]
    row["base_shear_Y_kN"] = -row["support_reaction_Fy_kN"]
    return row


def write_base_shear_roof_curve(path, rows, roof_story_name):
    """Write synchronized base-shear/roof-displacement samples, not envelopes."""
    roof = str(roof_story_name)
    selected = [
        {
            "time_s": row["time_s"],
            "roof_UX_m": row[roof + "_UX_m"],
            "roof_UY_m": row[roof + "_UY_m"],
            "base_shear_X_kN": row["base_shear_X_kN"],
            "base_shear_Y_kN": row["base_shear_Y_kN"],
        }
        for row in rows
        if "base_shear_X_kN" in row and "base_shear_Y_kN" in row
    ]
    if not selected:
        raise ValueError("No synchronized base-shear and roof-displacement samples.")
    return write_rows(path, selected)


def selected_member_response(ops, element_tag, node_tags, node_coordinates,
                            baseline_displacements):
    """Capture a selected member's local end forces and gravity-relative axial extension."""
    i_node, j_node = (int(node) for node in node_tags)
    start = [float(value) for value in node_coordinates.get(str(i_node), node_coordinates.get(i_node))]
    end = [float(value) for value in node_coordinates.get(str(j_node), node_coordinates.get(j_node))]
    axis = [b - a for a, b in zip(start, end)]
    length = sum(value * value for value in axis) ** .5
    if not length > 0:
        raise ValueError(f"Element {element_tag} has zero initial length.")
    axis = [value / length for value in axis]

    def translation(node):
        values = list(ops.nodeDisp(node))
        if len(values) < 3:
            raise ValueError(f"Node {node} displacement has fewer than three translational DOFs.")
        return [float(value) for value in values[:3]]

    current_i, current_j = translation(i_node), translation(j_node)
    initial_i = baseline_displacements[i_node][:3]
    initial_j = baseline_displacements[j_node][:3]
    extension = sum(
        ((current_j[k] - current_i[k]) - (initial_j[k] - initial_i[k])) * axis[k]
        for k in range(3)
    )
    def response_vector(response):
        if response is None:
            return []
        try:
            return [float(value) for value in response]
        except TypeError:
            return [float(response)]

    forces = response_vector(ops.eleResponse(int(element_tag), "localForce"))
    if not forces:
        axial = response_vector(ops.eleResponse(int(element_tag), "axialForce"))
        if axial:
            forces = [float(axial[0]), -float(axial[0])]
    if not forces:
        raise ValueError(f"Element {element_tag} returned neither localForce nor axialForce.")
    return {
        "element_tag": int(element_tag),
        "axial_extension_m": extension,
        "local_end_forces_kN_kNm": forces,
    }


def selected_device_response(ops, element_tag, node_tags, node_coordinates,
                             baseline_displacements, device_type, parameters):
    """Capture axial device force and gravity-relative kinematics at one accepted state."""
    i_node, j_node = (int(node) for node in node_tags)

    def position(node, displacement):
        xyz = node_coordinates.get(str(node), node_coordinates.get(node))
        if xyz is None or len(displacement) < 3:
            raise ValueError(f"Device {element_tag} node {node} lacks 3D coordinates/displacements.")
        return [float(xyz[index]) + float(displacement[index]) for index in range(3)]

    initial_i = position(i_node, baseline_displacements[i_node])
    initial_j = position(j_node, baseline_displacements[j_node])
    current_i = position(i_node, ops.nodeDisp(i_node))
    current_j = position(j_node, ops.nodeDisp(j_node))
    initial_axis = [b - a for a, b in zip(initial_i, initial_j)]
    initial_length = sum(value * value for value in initial_axis) ** .5
    current_axis = [b - a for a, b in zip(current_i, current_j)]
    current_length = sum(value * value for value in current_axis) ** .5
    if initial_length <= 0 or current_length <= 0:
        raise ValueError(f"Device {element_tag} has zero current or gravity-state length.")
    extension = current_length - initial_length
    current_axis = [value / current_length for value in current_axis]
    velocity_i = [float(value) for value in ops.nodeVel(i_node)[:3]]
    velocity_j = [float(value) for value in ops.nodeVel(j_node)[:3]]
    if len(velocity_i) < 3 or len(velocity_j) < 3:
        raise ValueError(f"Device {element_tag} node velocity has fewer than three translational DOFs.")
    axial_velocity = sum(
        (velocity_j[index] - velocity_i[index]) * current_axis[index]
        for index in range(3)
    )

    kind = str(device_type).upper()
    if kind == "FVD_MAXWELL":
        queries = (("basicForce",), ("material", 1, "stress"), ("axialForce",))
    elif kind == "BRB_STEEL02":
        queries = (("axialForce",), ("basicForce",), ("material", 1, "stress"))
    else:
        raise ValueError(f"Unsupported device type {device_type!r}.")

    force = None
    errors = []
    for query in queries:
        try:
            response = ops.eleResponse(int(element_tag), *query)
        except Exception as exc:
            errors.append(f"{query!r}: {exc}")
            continue
        if response is None:
            continue
        try:
            values = [float(response)] if isinstance(response, (int, float)) else [
                float(value) for value in response
            ]
        except (TypeError, ValueError):
            continue
        if not values:
            continue
        force = values[0]
        if query == ("material", 1, "stress") and kind == "BRB_STEEL02":
            area = float(parameters["core_area"])
            if not area > 0:
                raise ValueError(f"Device {element_tag} BRB core_area must be positive.")
            force *= area
        break
    if force is None:
        detail = "; ".join(errors) if errors else "all supported force responses were empty"
        raise RuntimeError(f"Device {element_tag} force response unavailable: {detail}")
    if not math.isfinite(force) or not math.isfinite(extension) or not math.isfinite(axial_velocity):
        raise ValueError(f"Device {element_tag} returned a non-finite force or kinematic response.")

    dashpot_velocity = None
    if kind == "FVD_MAXWELL":
        coefficient = float(parameters["Cd"])
        exponent = float(parameters["alpha"])
        if not coefficient > 0 or not 0 < exponent <= 1:
            raise ValueError(f"Device {element_tag} requires Cd > 0 and 0 < alpha <= 1.")
        dashpot_velocity = (
            0.0 if force == 0
            else math.copysign((abs(force) / coefficient) ** (1.0 / exponent), force)
        )
    return {
        "element_tag": int(element_tag),
        "axial_force_kN": force,
        "relative_displacement_m": extension,
        "assembly_axial_velocity_m_s": axial_velocity,
        "dashpot_velocity_m_s": dashpot_velocity,
    }


def device_energy_step(previous, time_s, force_kN, displacement_m,
                       dashpot_velocity_m_s=None):
    """Integrate signed device work and, for an FVD, its Maxwell dashpot work."""
    time_s, force_kN, displacement_m = (
        float(time_s), float(force_kN), float(displacement_m)
    )
    if not all(math.isfinite(value) for value in (time_s, force_kN, displacement_m)):
        raise ValueError("Device energy integration inputs must be finite.")
    if previous is None:
        return {
            "cumulative_device_work_kNm": 0.0,
            "dashpot_power_kW": (
                None if dashpot_velocity_m_s is None
                else force_kN * float(dashpot_velocity_m_s)
            ),
            "cumulative_dashpot_dissipation_kNm": (
                None if dashpot_velocity_m_s is None else 0.0
            ),
            "time_s": time_s,
            "force_kN": force_kN,
            "displacement_m": displacement_m,
            "dashpot_velocity_m_s": (
                None if dashpot_velocity_m_s is None
                else float(dashpot_velocity_m_s)
            ),
        }

    dt = time_s - float(previous["time_s"])
    if dt < -1e-12:
        raise ValueError("Device recorder time must be nondecreasing.")
    work = 0.5 * (float(previous["force_kN"]) + force_kN) * (
        displacement_m - float(previous["displacement_m"])
    )
    cumulative_work = float(previous["cumulative_device_work_kNm"]) + work
    power = None
    cumulative_dissipation = None
    dashpot_velocity = None
    if dashpot_velocity_m_s is not None:
        dashpot_velocity = float(dashpot_velocity_m_s)
        if not math.isfinite(dashpot_velocity):
            raise ValueError("FVD dashpot velocity must be finite.")
        power = force_kN * dashpot_velocity
        prior_power = previous["dashpot_power_kW"]
        cumulative_dissipation = (
            float(previous["cumulative_dashpot_dissipation_kNm"])
            + 0.5 * (float(prior_power) + power) * dt
        )
    return {
        "cumulative_device_work_kNm": cumulative_work,
        "dashpot_power_kW": power,
        "cumulative_dashpot_dissipation_kNm": cumulative_dissipation,
        "time_s": time_s,
        "force_kN": force_kN,
        "displacement_m": displacement_m,
        "dashpot_velocity_m_s": dashpot_velocity,
    }
