"""Opt-in ETABS frame rigid end zones for the elastic ETABS comparison model.

Config key (``OpenSees_Complete_Model_Config_V118.json``)::

    "rigid_end_zones": {"enabled": true,
                        "source": "ASSIGNMENT_WORKBOOK" | "SOURCE_METADATA",
                        "factor": "SOURCE" | <float 0..1>,
                        "workbook_path": "<optional; default etabs_native_assignment_workbook_path>"}

Absent key or ``enabled: false``: nothing changes (the export is byte-identical).

Method. The resolved ETABS end length offsets (``Frame Assignments - End Length
Offsets``: Offset I / Offset J / Rigid Factor per frame UniqueName, or the EDB
``FrameObj.GetEndLengthOffset`` record in the source metadata) are written as
``end_offsets_m`` into every state of ``elastic_etabs_comparison``.
``elastic_conversion_settings.compile_settings`` then places the rigid length
(offset x rigid factor) on the outer frame segments as OpenSees
``geomTransf ... -jntOffset`` rigid joint offsets, and scales A and J of those
segments by the retained length ratio so that axial and torsional flexibility
stay over the full member length. This follows the CSI rule that rigid zones
affect bending and shear only ("The rigid zones of the end offsets never affect
axial and torsional deformations", ETABS help, Assign > Frame > End Length
Offsets). Nodes, nodal loads, nodal masses and self-weight are not touched, so
total gravity load and seismic weight are unchanged.

[REF docs/source/components/model/rigid_end_zones.py.md]
"""
from __future__ import annotations

import math
from pathlib import Path

SHEET = "Frame Assigns - End Len Offsets"
SOURCES = ("ASSIGNMENT_WORKBOOK", "SOURCE_METADATA")
CONFIG_KEYS = {"enabled", "source", "factor", "workbook_path"}
_UNIT = {"mm": 1.0e-3, "m": 1.0}


def _finite_nonnegative(value, label):
    if isinstance(value, bool):
        raise ValueError(label + " must be a number")
    x = float(value)
    if not math.isfinite(x) or x < 0.0:
        raise ValueError(label + " must be finite and >= 0")
    return x


def read_end_offsets_workbook(path):
    """Read ETABS ``Frame Assignments - End Length Offsets`` from an assignment workbook.

    [REF CSI ETABS database table "Frame Assignments - End Length Offsets"]
    Row 1 title, row 2 column names, row 3 units (mm or m), data from row 4.
    Returns {UniqueName: dict(option, i_m, j_m, rigid_factor)}; lengths in metres.
    """
    from openpyxl import load_workbook
    book = load_workbook(Path(path), read_only=True, data_only=True)
    try:
        matches = [n for n in book.sheetnames if n.strip() == SHEET]
        if len(matches) != 1:
            raise ValueError("Assignment workbook needs exactly one sheet " + repr(SHEET))
        rows = list(book[matches[0]].iter_rows(values_only=True))
    finally:
        book.close()
    if len(rows) < 3:
        raise ValueError(SHEET + ": missing header or unit rows")
    header = [str(c or "").strip() for c in rows[1]]
    units = [str(c or "").strip().lower() for c in rows[2]]
    needed = ("UniqueName", "Offset Option", "Offset I", "Offset J", "Rigid Factor")
    missing = [k for k in needed if k not in header]
    if missing:
        raise ValueError(SHEET + ": missing columns " + ", ".join(missing))
    col = {k: header.index(k) for k in needed}
    scale = {}
    for k in ("Offset I", "Offset J"):
        unit = units[col[k]]
        if unit not in _UNIT:
            raise ValueError(SHEET + f": unsupported unit {unit!r} for {k}")
        scale[k] = _UNIT[unit]
    result = {}
    for number, row in enumerate(rows[3:], start=4):
        if row is None or all(c in (None, "") for c in row):
            continue
        name = str(row[col["UniqueName"]] or "").strip()
        if not name:
            raise ValueError(SHEET + f" row {number}: empty UniqueName")
        if name in result:
            raise ValueError(SHEET + f": duplicate UniqueName {name}")
        rigid = _finite_nonnegative(row[col["Rigid Factor"]], f"{SHEET} row {number} Rigid Factor")
        if rigid > 1.0:
            raise ValueError(f"{SHEET} row {number}: Rigid Factor > 1")
        result[name] = dict(
            option=str(row[col["Offset Option"]] or "").strip(),
            i_m=_finite_nonnegative(row[col["Offset I"]], f"{SHEET} row {number} Offset I") * scale["Offset I"],
            j_m=_finite_nonnegative(row[col["Offset J"]], f"{SHEET} row {number} Offset J") * scale["Offset J"],
            rigid_factor=rigid)
    if not result:
        raise ValueError(SHEET + ": no data rows")
    return result


def read_end_offsets_metadata(metadata):
    """Read ``FrameObj.GetEndLengthOffset`` records (auto, i, j, rigid, ret) from source metadata.

    [REF CSI OAPI FrameObj.GetEndLengthOffset] lengths already in model units (m).
    """
    result = {}
    for name, frame in (metadata.get("frames") or {}).items():
        record = frame.get("GetEndLengthOffset")
        if not (isinstance(record, (list, tuple)) and len(record) == 5 and record[-1] in (0, None)):
            continue
        auto, li, lj, rigid = record[:4]
        rigid = _finite_nonnegative(rigid, f"frame {name} rigid factor")
        if rigid > 1.0:
            raise ValueError(f"frame {name}: rigid factor > 1")
        result[str(name)] = dict(option="Auto" if auto else "User",
                                 i_m=_finite_nonnegative(li, f"frame {name} offset i"),
                                 j_m=_finite_nonnegative(lj, f"frame {name} offset j"),
                                 rigid_factor=rigid)
    return result


def validate_rigid_end_zone_config(block):
    """Return a normalised copy of the ``rigid_end_zones`` block, or None when absent/disabled.

    [REF engineering/rules/CORE_RULES.md rule 5] stiffness changes must be explicit and key-checked.
    """
    if block is None:
        return None
    if not isinstance(block, dict):
        raise ValueError("rigid_end_zones must be a JSON object")
    extra = set(block) - CONFIG_KEYS
    if extra:
        raise ValueError("rigid_end_zones has unknown keys: " + ", ".join(sorted(extra)))
    enabled = block.get("enabled", False)
    if type(enabled) is not bool:
        raise ValueError("rigid_end_zones.enabled must be boolean")
    if not enabled:
        return None
    source = block.get("source", "ASSIGNMENT_WORKBOOK")
    if source not in SOURCES:
        raise ValueError("rigid_end_zones.source must be one of " + ", ".join(SOURCES))
    factor = block.get("factor", "SOURCE")
    if factor != "SOURCE":
        factor = _finite_nonnegative(factor, "rigid_end_zones.factor")
        if factor > 1.0:
            raise ValueError("rigid_end_zones.factor must be <= 1")
    path = block.get("workbook_path")
    if path is not None and not isinstance(path, str):
        raise ValueError("rigid_end_zones.workbook_path must be a string")
    return dict(enabled=True, source=source, factor=factor, workbook_path=path)


def resolve_end_offsets(block, frames, *, metadata, default_workbook=None, base_dir=None):
    """Map the ETABS end offsets onto assembled frame objects as ``end_offsets_m`` entries.

    [REF ETABS help: Assign > Frame > End Length Offsets (rigid-zone factor, bending/shear only)]
    ``frames`` are the assembled frame segments (dicts with ``object``, ``hinged_brace``).
    Returns (end_offsets_m, audit). Frames with zero rigid length are omitted.
    Hinged braces with a nonzero rigid length are rejected (releases + offsets unqualified).
    """
    cfg = validate_rigid_end_zone_config(block)
    if cfg is None:
        return {}, None
    meta_records = read_end_offsets_metadata(metadata)
    workbook = None
    if cfg["source"] == "ASSIGNMENT_WORKBOOK":
        workbook = cfg["workbook_path"] or default_workbook
        if not workbook:
            raise ValueError("rigid_end_zones source ASSIGNMENT_WORKBOOK needs workbook_path "
                             "or etabs_native_assignment_workbook_path")
        workbook = Path(workbook)
        if not workbook.is_absolute() and base_dir is not None:
            workbook = Path(base_dir) / workbook
        records = read_end_offsets_workbook(workbook)
    else:
        records = meta_records
    objects = {}
    for frame in frames:
        objects.setdefault(str(frame["object"]), bool(frame.get("hinged_brace")))
    missing = sorted(o for o in objects if o not in records)
    if missing:
        raise ValueError(f"rigid_end_zones: {len(missing)} assembled frames lack an end-offset "
                         f"record, e.g. {missing[:5]}")
    offsets, cross_mismatch, factor_changed = {}, [], 0
    rigid_total = 0.0
    for obj in sorted(objects, key=lambda s: (len(s), s)):
        rec = records[obj]
        rigid = rec["rigid_factor"] if cfg["factor"] == "SOURCE" else cfg["factor"]
        factor_changed += not math.isclose(rigid, rec["rigid_factor"], abs_tol=1e-12)
        other = meta_records.get(obj) if cfg["source"] == "ASSIGNMENT_WORKBOOK" else None
        if other is not None and any(not math.isclose(rec[k], other[k], abs_tol=1e-6)
                                     for k in ("i_m", "j_m", "rigid_factor")):
            cross_mismatch.append(obj)
        if rigid * (rec["i_m"] + rec["j_m"]) <= 0.0:
            continue
        if objects[obj]:
            raise ValueError(f"rigid_end_zones: hinged brace {obj} has a rigid end zone; "
                             "releases with joint offsets are not qualified")
        offsets[obj] = {"i": rec["i_m"], "j": rec["j_m"], "rigid_fraction": rigid}
        rigid_total += rigid * (rec["i_m"] + rec["j_m"])
    audit = dict(
        schema="RIGID_END_ZONES_V1", source=cfg["source"],
        workbook=(workbook.name if workbook is not None else None),
        factor=cfg["factor"], assembled_frame_objects=len(objects),
        frames_with_rigid_zone=len(offsets), frames_rigid_factor_overridden=factor_changed,
        total_rigid_length_m=rigid_total,
        workbook_vs_metadata_mismatch_count=(len(cross_mismatch) if cfg["source"] == "ASSIGNMENT_WORKBOOK"
                                             and meta_records else None),
        workbook_vs_metadata_mismatch_examples=cross_mismatch[:10],
        method="geomTransf -jntOffset on outer segments; A and J scaled by retained length "
               "(axial/torsion over full length); loads, masses and self-weight unchanged",
        status="STIFFNESS_INPUT_ONLY_NOT_ENGINEERING_ACCEPTANCE")
    return offsets, audit


def inject_end_offsets(elastic_config, offsets):
    """Return a copy of ``elastic_etabs_comparison`` with ``end_offsets_m`` set in every state.

    [REF docs/source/components/model/rigid_end_zones.py.md] refuses to merge with
    hand-written ``end_offsets_m`` so a single source of offsets is used.
    """
    if not isinstance(elastic_config, dict) or not elastic_config:
        raise ValueError("rigid_end_zones needs a non-empty elastic_etabs_comparison "
                         "(rigid zones act through the elastic comparison stiffness path)")
    result = {}
    for state, options in elastic_config.items():
        if not isinstance(options, dict):
            raise ValueError(f"elastic_etabs_comparison {state} must be a JSON object")
        if options.get("end_offsets_m"):
            raise ValueError(f"elastic_etabs_comparison {state} already has end_offsets_m; "
                             "use either rigid_end_zones or end_offsets_m")
        result[state] = {**options, "end_offsets_m": {k: dict(v) for k, v in offsets.items()}}
    return result
