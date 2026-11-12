"""Reviewed first-storey wall grouping for NBC 105:2025 §5.1.2.

[REF docs/source/components/inputs/grouped_wall_aw.py.md]
Historical precedent: UBC 1997 §§1628, 1630.2.2 Eq. (30-9);
SEAOC Seismic Design Manual Vol. I, Example 19 (masonry wall openings).
Net MINIMUM first-storey horizontal concrete area is distinguished from
OVERALL lateral-load resisting wall length. This is an engineering
interpretation/audit, not an official Nepalese opening commentary.
No EDB edits, no silent use as an approved design parameter.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

STATUS = "SOURCE_MATCHED_GROUPED_WALL_AREA_REVIEW_REQUIRED"
INPUT_NAME = "NBC105_Wall_Grouping_Review.json"


def _number(value, label, *, positive=False):
    v = float(value)
    if not math.isfinite(v) or (positive and v <= 0):
        raise ValueError(label + " must be finite" + (" and positive" if positive else ""))
    return v


def wall_aw_example(*, height_m=95.0, thickness_m=0.6,
                    width_m=6.0, opening_width_m=2.0,
                    x_walls=4, y_walls=3):
    """[REF docs/source/components/inputs/grouped_wall_aw.py.md]
    Standalone example reproducing user's original Excel METHOD, not source
    geometry or a permitted substitute for validated ETABS results.
    """
    h = _number(height_m, "H", positive=True)
    t = _number(thickness_m, "t", positive=True)
    width = _number(width_m, "L", positive=True)
    op = _number(opening_width_m, "opening_width")
    if op < 0 or op >= width:
        raise ValueError("Opening width must be >=0 and smaller than wall length")
    if not isinstance(x_walls, int) or not isinstance(y_walls, int) or x_walls < 0 or y_walls < 0:
        raise ValueError("Wall counts must be nonnegative integers")
    factor = 0.2 + min(width / h, 0.9) ** 2
    return {
        "status": "ILLUSTRATIVE_GEOMETRY_NOT_EDB_VERIFIED",
        "X": x_walls * t * (width - op) * factor,
        "Y": y_walls * t * width * factor,
        "net_area_per_X_wall_m2": t * (width - op),
        "net_area_per_Y_wall_m2": t * width,
        "wall_gross_length_m": width,
        "coefficient": factor,
        "opening_height_m": None,
        "method": "MINIMUM_FIRST_STOREY_HORIZONTAL_AREA_WITH_OVERALL_WALL_LENGTH",
        "code_accepted": False,
    }


def _union(intervals):
    result = []
    for a, b in sorted(intervals):
        if b <= a:
            raise ValueError("Invalid or zero-length wall interval")
        if result and a <= result[-1][1] + 1e-7:
            result[-1] = (result[-1][0], max(result[-1][1], b))
        else:
            result.append((a, b))
    return result


def _coverage(intervals, low, high):
    total = 0.0
    for a, b in intervals:
        total += max(0.0, min(b, high) - max(a, low))
    return total


def grouped_wall_aw(profile, height_m, groups):
    """[REF docs/source/components/inputs/grouped_wall_aw.py.md]
    Each group is an explicitly mapped whole structural wall:
      {id,axis,plane_m,thickness_m,start_m,end_m}.
    Its per-slice solid horizontal widths are read from SOURCE shell slices.
    Use the minimum NET area over first-storey horizontal slices, multiplied
    by the GROSS group span's empirical length factor, capped at L/H=.9.
    Adjacent/overlapping groups or unassigned shell material are rejected.
    """
    h = _number(height_m, "H", positive=True)
    slices = profile.get("rows") or []
    if not slices or not groups:
        raise ValueError("Need all first-storey slices and explicit wall groups")
    ids = set()
    parsed = []
    for g in groups:
        ident = str(g["id"]).strip()
        if not ident or ident in ids:
            raise ValueError("Wall group IDs must be unique and nonblank")
        ids.add(ident)
        axis = str(g["axis"]).upper()
        if axis not in ("X", "Y"):
            raise ValueError("Wall axis must be X/Y")
        plane = _number(g["plane_m"], ident + " plane")
        thick = _number(g["thickness_m"], ident + " thickness", positive=True)
        left = _number(g["start_m"], ident + " start")
        right = _number(g["end_m"], ident + " end")
        if right <= left:
            raise ValueError("Group length must be positive")
        parsed.append(dict(id=ident, axis=axis, plane=plane,
                           thickness=thick, left=left, right=right))
    for i, first in enumerate(parsed):
        for second in parsed[i + 1:]:
            if (first["axis"], first["plane"], first["thickness"]) != (
                    second["axis"], second["plane"], second["thickness"]):
                continue
            if min(first["right"], second["right"]) - max(first["left"], second["left"]) > 1e-7:
                raise ValueError("Overlapping wall groups would double-count material")
    areas_by_group = {g["id"]: [] for g in parsed}
    # Require that no source wall segment is unassigned or doubly assigned.
    for row in slices:
        segments = row.get("segments") or []
        for segment in segments:
            matching = [g for g in parsed
                        if g["axis"] == segment["axis"] and
                        abs(g["plane"] - float(segment["plane_m"])) < 1e-5 and
                        abs(g["thickness"] - float(segment["thickness_m"])) < 1e-5]
            a, b = float(segment["start_m"]), float(segment["end_m"])
            assigned = sum(_coverage([(a, b)], g["left"], g["right"]) for g in matching)
            if abs(assigned - (b - a)) > 1e-5:
                raise ValueError("Unmapped or duplicated source wall material at z="
                                 + str(row["z_mid_m"]) + "; cannot assume wall groups")
        for g in parsed:
            spans = []
            for seg in segments:
                if (seg["axis"] == g["axis"] and
                    abs(float(seg["plane_m"]) - g["plane"]) < 1e-5 and
                    abs(float(seg["thickness_m"]) - g["thickness"]) < 1e-5):
                    a = max(g["left"], float(seg["start_m"]))
                    b = min(g["right"], float(seg["end_m"]))
                    if b - a > 1e-8:
                        spans.append((a, b))
            width = sum(b - a for a, b in _union(spans))
            areas_by_group[g["id"]].append(g["thickness"] * width)
    totals = {"X": 0.0, "Y": 0.0}
    detail = []
    for g in parsed:
        minimum = min(areas_by_group[g["id"]])
        if minimum <= 0:
            raise ValueError("Group " + g["id"] + " has no concrete in a first-storey slice")
        gross_len = g["right"] - g["left"]
        weighted = minimum * (0.2 + min(gross_len / h, 0.9) ** 2)
        totals[g["axis"]] += weighted
        detail.append(dict(id=g["id"], axis=g["axis"],
                           gross_length_m=gross_len,
                           net_min_first_storey_area_m2=minimum,
                           slice_areas_m2=areas_by_group[g["id"]],
                           aw_contribution_m2=weighted))
    return {"status": STATUS, "code_accepted": False,
            "method": "MIN_FIRST_STOREY_AREA_GROSS_CONNECTED_WALL_LENGTH",
            "aw_candidate_m2": totals, "wall_contributions": detail,
            "notes": ["Explicit structural wall grouping remains engineer-reviewed",
                      "Not equivalent to physical pier/coupling stiffness verification",
                      "UBC 1997 and SEAOC are explanatory precedent, not Nepalese adoption"]}



THESIS_WALL_POLICY = "THESIS_20261112_TWO_CONNECTED_12M_X_WALLS"


def verify_thesis_two_12m_wall_geometry(profile, height_m):
    """[REF docs/source/components/inputs/grouped_wall_aw.py.md]
    Verify THIS thesis's two 12m perforated X-wall lines and three solid
    6m Y-wall lines from generated OpenSees first-storey shell/node geometry.

    No wall groups are inferred from a drawing or grid labels. Every actual
    horizontal material slice is checked; failure is an explicit engineering
    block rather than a fallback to 6m bays or a hard-coded 2.073m².
    This validates EXPORT geometry, not original ETABS EDB coupling/rebar.
    """
    h = _number(height_m, "NBC building height H", positive=True)
    rows = profile.get("rows") or []
    if not rows:
        raise ValueError("No exported first-storey wall material slices")
    def near(a, b, tol=0.001):
        return abs(a - b) <= tol
    if not near(h, 95.):
        raise ValueError("Thesis 12m-wall policy expected H=95m; source has " + str(h))
    base = min(float(r["z_bottom_m"]) for r in rows)
    top = max(float(r["z_top_m"]) for r in rows)
    if not near(top - base, 3.8):
        raise ValueError("First-storey extent differs from expected 3.8m")
    axes = {}
    for row in rows:
        for seg in row.get("segments") or []:
            key = (str(seg["axis"]).upper(), round(float(seg["plane_m"]), 6),
                   round(float(seg["thickness_m"]), 6))
            axes.setdefault(key, []).append((float(seg["start_m"]), float(seg["end_m"])))
    xlines = sorted(k for k in axes if k[0] == "X")
    ylines = sorted(k for k in axes if k[0] == "Y")
    if len(xlines) != 2 or len(ylines) != 3:
        raise ValueError("Expected 2 X wall planes and 3 Y wall planes, found "
                         + str((len(xlines), len(ylines))))
    if any(not near(k[2], .6) for k in axes):
        raise ValueError("Source wall thickness differs from reviewed 0.6m")
    groups = []
    evidence = {"policy": THESIS_WALL_POLICY,
                "source": "EXPORTED_OPENSEES_FIRST_STOREY_NODES_AND_SHELLS",
                "first_storey_base_m": base,
                "first_storey_top_m": top,
                "x_wall_lines": [], "y_wall_lines": [],
                "classification": "EXPORTED_GEOMETRY_VERIFIED_NOT_NATIVE_ETABS_CERTIFIED"}
    for axis, lines in (("X", xlines), ("Y", ylines)):
        expected_length = 12.0 if axis == "X" else 6.0
        for k in lines:
            spans = _union(axes[k])
            left = min(a for a, b in spans)
            right = max(b for a, b in spans)
            if not near(right - left, expected_length):
                raise ValueError(f"{axis} wall plane {k[1]} span is "
                                 f"{right-left}m, expected {expected_length}m")
            groups.append({"id": f"{axis}_{len(evidence[axis.lower()+'_wall_lines'])+1}",
                           "axis": axis, "plane_m": k[1], "thickness_m": .6,
                           "start_m": left, "end_m": right})
            sections = []
            for row in rows:
                zlo, zhi = float(row["z_bottom_m"]), float(row["z_top_m"])
                intervals = _union([
                    (float(seg["start_m"]), float(seg["end_m"]))
                    for seg in row.get("segments") or []
                    if (str(seg["axis"]).upper(), round(float(seg["plane_m"]), 6),
                        round(float(seg["thickness_m"]), 6)) == k])
                intervals = [(max(left,a), min(right,b)) for a,b in intervals
                             if min(right,b)-max(left,a) > 1e-7]
                gaps = []
                edge = left
                for a,b in intervals:
                    if a-edge > 1e-6:
                        gaps.append((edge,a))
                    edge = b
                if right-edge > 1e-6:
                    gaps.append((edge,right))
                sections.append(dict(z_bottom_m=zlo,z_top_m=zhi,
                                     solid_intervals_m=intervals,
                                     gaps_m=gaps,
                                     net_area_m2=.6*sum(b-a for a,b in intervals)))
            if axis == "X":
                low = [r for r in sections if r["z_bottom_m"] < base+2.3-1e-5]
                high = [r for r in sections if r["z_top_m"] > base+2.3+1e-5]
                if not low or not high:
                    raise ValueError("Door head at 2.3m is not represented by source slices")
                for row in low:
                    if (not near(row["net_area_m2"], 4.8) or
                        len(row["gaps_m"]) != 2 or
                        any(not near(b-a,2.) for a,b in row["gaps_m"])):
                        raise ValueError(f"X wall {k[1]} lacks two 2m floor-level doors "
                                         "in a common horizontal section")
                if any(not near(r["net_area_m2"], 7.2) or r["gaps_m"] for r in high):
                    raise ValueError(f"X wall {k[1]} does not reconnect above 2.3m")
                if any(not near(r["z_top_m"],base+2.3) for r in low):
                    raise ValueError("Door-head elevation differs from expected 2.3m")
                evidence["x_wall_lines"].append(dict(plane_m=k[1],
                                                   gross_span_m=[left,right],
                                                   first_storey_sections=sections))
            else:
                if any(not near(r["net_area_m2"],3.6) or r["gaps_m"] for r in sections):
                    raise ValueError(f"Y wall {k[1]} contains an opening or missing segment")
                evidence["y_wall_lines"].append(dict(plane_m=k[1],
                                                   gross_span_m=[left,right],
                                                   first_storey_sections=sections))
    result = grouped_wall_aw(profile, h, groups)
    result["status"] = "EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY"
    result["policy"] = THESIS_WALL_POLICY
    result["wall_geometry_verification"] = evidence
    result["code_accepted"] = False
    result["structural_grouping_decision"] = "USER_SELECTED_TWO_CONNECTED_12M_X_WALLS"
    result["warnings"] = [
        "Generated source-matched shell/node geometry confirmed; original ETABS "
        "EDB and reinforcement connectivity are separate native checks.",
        "Do not change the original Excel source file. Previous 6m grouping is a "
        "historical comparison, not the selected 12m calculation.",
    ]
    return result


def source_matched_grouping(export_dir, state, profile, height_m,
                            source_edb, assembled_model_sha256):
    """[REF docs/source/components/inputs/grouped_wall_aw.py.md]
    Use ONLY a deliberate local manifest matching current EDB bytes, the
    assembled model hash and analysis state. Nothing auto-generates approval.
    """
    manifest = Path(export_dir) / INPUT_NAME
    if not manifest.is_file():
        return None
    edb = Path(source_edb) if source_edb else None
    if not edb or not edb.is_file():
        raise ValueError("Missing original EDB for grouped wall source verification")
    hasher = hashlib.sha256()
    with edb.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if (data.get("source_edb_sha256") != digest or
        data.get("assembled_model_sha256") != assembled_model_sha256 or
        data.get("limit_state") != str(state).upper()):
        raise ValueError("Wall grouping input EDB/model/limit-state fingerprint mismatch")
    if abs(_number(data.get("height_m"), "Manifest height", positive=True) - float(height_m)) > 1e-6:
        raise ValueError("Grouping and source seismic heights differ")
    result = grouped_wall_aw(profile, height_m, data["wall_groups"])
    result["source_manifest"] = str(manifest)
    result["source_edb_sha256"] = digest
    result["assembled_model_sha256"] = assembled_model_sha256
    return result
