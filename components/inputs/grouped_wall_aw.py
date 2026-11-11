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
