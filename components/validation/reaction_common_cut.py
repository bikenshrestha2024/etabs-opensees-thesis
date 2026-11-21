"""Offline six-component ETABS/OpenSees common-origin reaction comparison.

Requires *mapped and solved* native results for the same source and case.
ETABS object JointReact is not assumed equivalent to an internal analysis joint.
This module never changes supports, shell formulation or frame end offsets.

Input JSON: {"source": {"edb_sha256": "...", "model_sha256": "...",
"case": "1. DL + LL", "force_unit": "kN", "length_unit": "m",
"coordinate_system": "GLOBAL", "reaction_level": "ANALYSIS_JOINT",
"native_restraints_verified": true},
"origin_m": [0,0,0],
"etabs": [{"id": "...", "xyz_m": [x,y,z], "reaction": [Fx,Fy,Fz,Mx,My,Mz]}],
"opensees": [{"id": "...", "xyz_m": [...], "reaction": [...]}],
"map": [{"etabs": "...", "opensees": "...", "group": "PRIMARY_32"}]}

Other groups are WALL_TRANSFER_44 and EXTRA_21. A missing mapped solver
reaction is NOT replaced with zero. Moments are kN*m about the same origin.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

DOF = ("FX_kN", "FY_kN", "FZ_kN", "MX_kNm", "MY_kNm", "MZ_kNm")
GROUPS = ("PRIMARY_32", "WALL_TRANSFER_44", "EXTRA_21")


def _vector(v, length, name):
    if not isinstance(v, (list, tuple)) or len(v) != length:
        raise ValueError(name + " must have " + str(length) + " entries")
    if any(isinstance(x, bool) for x in v):
        raise ValueError(name + " contains boolean")
    try:
        result = [float(x) for x in v]
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + " contains nonnumeric values") from exc
    if not all(math.isfinite(x) for x in result):
        raise ValueError(name + " contains nonfinite values")
    return result


def _index(rows, name):
    if not isinstance(rows, list) or not rows:
        raise ValueError(name + " requires nonempty records")
    found = {}
    for row in rows:
        tag = str(row.get("id", "")).strip()
        if not tag or tag in found:
            raise ValueError(name + " has empty or duplicate node IDs")
        found[tag] = {
            "xyz": _vector(row.get("xyz_m"), 3, name + " coordinates"),
            "reaction": _vector(row.get("reaction"), 6, name + " reactions"),
        }
    return found


def _resultant(row, origin):
    xyz = row["xyz"]
    f = row["reaction"][:3]
    m = row["reaction"][3:]
    x, y, z = (xyz[i] - origin[i] for i in range(3))
    return [*f, m[0] + y*f[2] - z*f[1],
            m[1] + z*f[0] - x*f[2],
            m[2] + x*f[1] - y*f[0]]


def _sum(vectors):
    vectors = list(vectors)
    return [math.fsum(v[i] for v in vectors) for i in range(6)]


def compare_common_cut(payload, *, expected_primary_count=32,
                       expected_transfer_count=44):
    """Compare mapped six-DOF support reactions, not force-only equilibrium.

    Do not issue a structural-equivalence PASS even with exact numerical
    agreement: analysis-mesh topology and stiffness require external review.
    """
    source = payload.get("source", {})
    required = ("edb_sha256", "model_sha256", "case", "force_unit",
                "length_unit", "coordinate_system", "reaction_level",
                "native_restraints_verified")
    if not isinstance(source, dict) or any(k not in source for k in required):
        raise ValueError("Missing native source provenance fields")
    for key in ("edb_sha256", "model_sha256"):
        value = source[key]
        if not isinstance(value, str) or len(value) != 64 or any(
                c not in "0123456789abcdefABCDEF" for c in value):
            raise ValueError("Missing exact SHA256 for " + key)
    if source["case"] != "1. DL + LL":
        raise ValueError("Comparison case must be 1. DL + LL")
    if any(source[k] != v for k, v in
           (("force_unit", "kN"), ("length_unit", "m"),
            ("coordinate_system", "GLOBAL"))):
        raise ValueError("Unit or coordinate mismatch")
    if source["reaction_level"] not in ("ANALYSIS_JOINT", "OBJECT_JOINT"):
        raise ValueError("Explicit ETABS reaction level required")
    if type(source["native_restraints_verified"]) is not bool:
        raise ValueError("Native restraint verification must be boolean")
    origin = _vector(payload.get("origin_m"), 3, "origin")
    etabs, opensees = _index(payload.get("etabs"), "ETABS"), _index(
        payload.get("opensees"), "OpenSees")
    mappings = payload.get("map")
    if not isinstance(mappings, list) or not mappings:
        raise ValueError("Mappings are mandatory")
    paired_etabs, paired_os, records = set(), set(), []
    for m in mappings:
        a, b = str(m.get("etabs", "")).strip(), str(m.get("opensees", "")).strip()
        group = m.get("group")
        if group not in GROUPS or not a or not b:
            raise ValueError("Invalid group or node mapping")
        if a in paired_etabs or b in paired_os:
            raise ValueError("Duplicate or many-to-one node mapping")
        if a not in etabs or b not in opensees:
            raise ValueError("Unmapped/absent solved reaction cannot become zero")
        paired_etabs.add(a)
        paired_os.add(b)
        ra, rb = etabs[a], opensees[b]
        if max(abs(x-y) for x,y in zip(ra["xyz"], rb["xyz"])) > 1e-6:
            raise ValueError("Mapped node coordinates differ; do not pair by label")
        a6 = _resultant(ra, origin)
        b6 = _resultant(rb, origin)
        records.append({"group": group, "etabs_id": a, "opensees_id": b,
                        "etabs_resultant": a6, "opensees_resultant": b6,
                        "delta": [y-x for x,y in zip(a6,b6)],
                        "reaction_delta": [y-x for x,y in zip(
                            ra["reaction"], rb["reaction"])]})
    if len(paired_etabs) != len(etabs) or len(paired_os) != len(opensees):
        raise ValueError("Input contains reactions without unique mappings")
    counts = {g: sum(x["group"] == g for x in records) for g in GROUPS}
    if counts["PRIMARY_32"] != expected_primary_count or counts[
            "WALL_TRANSFER_44"] != expected_transfer_count:
        raise ValueError("Expected primary/transfer mapping counts do not match")
    metrics = {}
    for group in (*GROUPS, "ALL_MAPPED"):
        items = records if group == "ALL_MAPPED" else [
            x for x in records if x["group"] == group]
        a = _sum(x["etabs_resultant"] for x in items)
        b = _sum(x["opensees_resultant"] for x in items)
        delta = [y-x for x,y in zip(a,b)]
        metrics[group] = {"count": len(items), "etabs": a,
                          "opensees": b, "difference": delta,
                          "sum_abs_local_delta": [math.fsum(abs(x["reaction_delta"][j])
                              for x in items) for j in range(6)]}
    result = {
        "status": "NUMERICAL_DIAGNOSTIC_ONLY_NOT_STRUCTURAL_ACCEPTANCE",
        "source": source, "origin_m": origin, "groups": metrics,
        "records": records,
        "unresolved": [
            "Verify ETABS analysis-joint versus object-joint reaction recovery",
            "Verify native ETABS internal auto-mesh edge and MPC force transfers",
            "Verify six-DOF common physical wall-base cut and frame end sections",
            "Verify stiffness, diaphragm connectivity and gravity load paths",
        ],
    }
    if source["reaction_level"] != "ANALYSIS_JOINT":
        result["unresolved"].append(
            "ETABS OBJECT_JOINT reactions cannot prove analysis-level support force attribution")
    if not source["native_restraints_verified"]:
        result["unresolved"].append("Native six-DOF restraints not independently verified")
    return result


def export_report(payload_path, output_dir):
    """Save JSON + CSV under requested output directory with source hash."""
    inp = Path(payload_path)
    payload = json.loads(inp.read_text(encoding="utf-8-sig"))
    result = compare_common_cut(payload)
    result["input_sha256"] = hashlib.sha256(inp.read_bytes()).hexdigest()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "Reaction_Six_DOF_Common_Cut.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    fields = ["group", "etabs_id", "opensees_id", *(
        prefix + dof for prefix in ("ETABS_", "OpenSees_", "Difference_")
        for dof in DOF)]
    with (out / "Reaction_Six_DOF_Common_Cut.csv").open(
            "w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for record in result["records"]:
            row = {k: record[k] for k in fields[:3]}
            for prefix, values in (("ETABS_",record["etabs_resultant"]),
                                   ("OpenSees_",record["opensees_resultant"]),
                                   ("Difference_",record["delta"])):
                row.update({prefix+dof:v for dof,v in zip(DOF,values)})
            writer.writerow(row)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_json")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    print(json.dumps(export_report(args.source_json, args.output_dir)["groups"],
                     indent=2))
