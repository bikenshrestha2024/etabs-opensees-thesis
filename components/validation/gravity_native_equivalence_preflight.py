"""Read-only forensic preflight for native ETABS vs OpenSees gravity equivalence.

No ETABS COM, solver commands, or source modifications. ETABS zero reaction
does NOT prove a free support DOF; rigid-end-zone stiffness is independent of
clear-length self-weight. This module intentionally never declares equivalence.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "gravity-native-equivalence-preflight-v1"
REQUIRED = ("OpenSees_Complete_Model_Data_V118.json",
            "OpenSees_Source_Model_Metadata_V118.json",
            "OpenSees_Element_Connectivity.json")


def _load_json(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _offset(raw):
    """CSI GetEndLengthOffset: auto, i, j, rigid zone factor, ret."""
    if not isinstance(raw, (list, tuple)) or len(raw) != 5 or raw[-1] != 0:
        return dict(status="MISSING_OR_FAILED_NATIVE_OFFSET")
    try:
        auto, i, j, rigid = raw[:4]
        if not isinstance(auto, (bool, int)) or auto not in (0, 1, False, True):
            raise ValueError("invalid AutoOffset")
        i, j, rigid = float(i), float(j), float(rigid)
        if not all(math.isfinite(x) for x in (i, j, rigid)):
            raise ValueError("nonfinite offset")
        if i < 0 or j < 0 or not 0 <= rigid <= 1:
            raise ValueError("offset/rz outside physical bounds")
    except (ValueError, TypeError):
        return dict(status="INVALID_NATIVE_OFFSET")
    return dict(status="NATIVE_OFFSET_CAPTURED",
                auto_offset=bool(auto), end_i_m=i, end_j_m=j,
                rigid_zone_factor=rigid,
                native_rigid_end_zone_requires_review=bool(rigid > 0 and (auto or i > 0 or j > 0)))


def assess(source_folder, *, primary_audit=None):
    """Assess evidence without changing supports, stiffness, or load cases.

    Input exported model data must be the ORIGINAL assembled source-support
    configuration, not a model mutated in memory by the 32-node scenario.
    """
    root = Path(source_folder).expanduser().resolve()
    for name in REQUIRED:
        if not (root / name).is_file():
            raise FileNotFoundError("Required project export evidence missing: " + name)
    model = _load_json(root / REQUIRED[0])
    meta = _load_json(root / REQUIRED[1])
    topology = _load_json(root / REQUIRED[2])
    original = model.get("supports")
    if not isinstance(original, dict) or not original:
        raise ValueError("Original assembled support DOFs missing")
    from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32
    primary = set(map(str, PROJECT_PRIMARY_32))
    original_vertical = {}
    for tag, flags in original.items():
        if not isinstance(flags, (list, tuple)) or len(flags) != 6:
            raise ValueError("Source restraint must contain six DOF flags at node " + str(tag))
        if any(v not in (0, 1, False, True) for v in flags):
            raise ValueError("Source restraint flags invalid at node " + str(tag))
        if bool(flags[2]):
            original_vertical[str(tag)] = list(map(int, flags))
    source_tags = set(original_vertical)
    missing_primary = sorted(primary - source_tags, key=int)
    released = sorted(source_tags - primary, key=int)
    native_points = {str(x["opensees_node_tag"]):str(x["etabs_point_name"])
                     for x in topology.get("node_map",[])
                     if x.get("opensees_node_tag") is not None
                     and x.get("etabs_point_name") is not None}
    support_rows = []
    for tag in sorted(source_tags | primary, key=int):
        flags = original.get(tag, [0] * 6)
        support_rows.append(dict(opensees_node=int(tag),
            etabs_point=native_points.get(tag),
            source_dof="".join(str(int(x)) for x in flags),
            primary32_selected=(tag in primary),
            native_source_uz_restrained=bool(original_vertical.get(tag)),
            released_in_primary32=(tag in source_tags - primary),
            provenance="SOURCE_EXPORT_RESTRAINT_NOT_NATIVE_INTERNAL_AUTOMESH"))
    offsets = []
    native_frames = meta.get("frames") or {}
    for obj, records in sorted(native_frames.items()):
        offset = _offset(records.get("GetEndLengthOffset") if isinstance(records, dict) else None)
        offsets.append(dict(etabs_object=str(obj), **offset))
    missing_offsets = sum(x["status"] != "NATIVE_OFFSET_CAPTURED" for x in offsets)
    nonzero_rigid = sum(x.get("native_rigid_end_zone_requires_review",False) for x in offsets)
    mismatch = None
    audit_hash = None
    if primary_audit is not None:
        audit_path = Path(primary_audit)
        if not audit_path.is_file():
            raise FileNotFoundError(audit_path)
        audit_hash = _sha(audit_path)
        audit = _load_json(audit_path)
        if audit.get("mode") != "ETABS_NONZERO_REACTION_DIAGNOSTIC":
            raise ValueError("Primary reaction audit has different scenario identity")
        listed = {str(row["opensees_node"]) for row in audit.get("mapping",[])
                  if row.get("selected")}
        if listed != primary:
            raise ValueError("Primary audit mapped support set does not match selected 32")
        mismatch = dict(
            selected32_verified_in_source=(not missing_primary),
            primary_audit_sha256=audit_hash,
            etabs_table_sha256=audit.get("source_sha256"),
            original_etabs_case=audit.get("case"))
    reasons = []
    if missing_primary:
        reasons.append("Project primary node tags missing from original source restraints")
    if released:
        reasons.append("Primary 32-node run releases originally restrained base points; native ETABS DOF equivalence NOT demonstrated")
    if not native_frames:
        reasons.append("Native frame assignment metadata missing")
    if missing_offsets:
        reasons.append("Some native ETABS end-length offset metadata missing/invalid")
    if nonzero_rigid:
        reasons.append("ETABS rigid end zones require an independently verified OpenSees stiffness transformation")
    if meta.get("errors"):
        reasons.append("ETABS OAPI source metadata extraction has unresolved errors")
    if not native_points:
        reasons.append("ETABS point-to-OpenSees mapping missing")
    if primary_audit is None:
        reasons.append("Original ETABS reaction-based primary support mapping audit not supplied")
    reasons.append("Individual ETABS joint force/stiffness and native response equivalence still require native comparisons")
    return dict(schema=SCHEMA,
        engineering_acceptance="NOT_VALIDATED",
        recommended_action="RECONCILE_NATIVE_RESTRAINTS_AND_RIGID_END_STIFFNESS_BEFORE_NEW_MODEL_CORRECTION",
        input_sha256={name:_sha(root / name) for name in REQUIRED},
        source_vertical_restrained_count=len(source_tags),
        selected_primary_count=len(primary),
        selected_primary_not_in_source=missing_primary,
        originally_restrained_released_by_primary32=released,
        released_by_primary32_count=len(released),
        native_frame_metadata_count=len(native_frames),
        native_offset_missing_or_invalid_count=missing_offsets,
        native_frame_rigid_end_zone_review_count=nonzero_rigid,
        comparison=mismatch, blockers=reasons,
        support_rows=support_rows, offset_rows=offsets)


def export(source_folder, output_folder, *, primary_audit=None):
    """Write new audit outputs atomically; never overwrite an existing audit."""
    report = assess(source_folder, primary_audit=primary_audit)
    target = Path(output_folder).expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        raise FileExistsError("Audit folder must be new or empty: " + str(target))
    target.mkdir(parents=True,exist_ok=True)
    summary = {k:v for k,v in report.items() if k not in ("support_rows","offset_rows")}
    (target / "GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json").write_text(
        json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    for name,rows in (("SOURCE_SUPPORT_DOF_VS_PRIMARY32.csv",report["support_rows"]),
                      ("ETABS_END_ZONE_STIFFNESS_REVIEW.csv",report["offset_rows"])):
        keys = sorted({k for row in rows for k in row})
        with (target / name).open("w",newline="",encoding="utf-8-sig") as stream:
            writer=csv.DictWriter(stream,fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
    (target / "READ_FIRST.txt").write_text(
        "ETABS/OpenSees gravity stiffness and foundation preflight — NOT validated.\n"
        "Read the source/support DOF and end-zone CSV, reconcile native ETABS restraints\n"
        "and auto offsets, then rerun 32/76/97 cases in isolated directories.\n"
        "Never change native source EDB, gravity loads or stiffness to fit reactions.\n"
        "Blockers: "+json.dumps(summary["blockers"],indent=2)+"\n",encoding="utf-8")
    # Include just the small forensic evidence, not private source datasets.
    # The new run directory makes this ZIP non-overwriting by construction.
    from zipfile import ZipFile, ZIP_DEFLATED
    with ZipFile(target / "GRAVITY_NATIVE_EQUIVALENCE_UPLOAD.zip",
                 "x",compression=ZIP_DEFLATED) as archive:
        for name in ("GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json",
                     "SOURCE_SUPPORT_DOF_VS_PRIMARY32.csv",
                     "ETABS_END_ZONE_STIFFNESS_REVIEW.csv","READ_FIRST.txt"):
            archive.write(target / name,arcname=name)
    return report


def main(argv=None):
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("export_folder",help="Saved ETABS-to-OpenSees export folder")
    p.add_argument("output_folder",help="NEW output folder (existing files never overwritten)")
    p.add_argument("--primary-audit",help="Original nonzero ETABS-reaction mapping JSON")
    args=p.parse_args(argv)
    r=export(args.export_folder,args.output_folder,primary_audit=args.primary_audit)
    print(json.dumps({k:v for k,v in r.items() if k not in ("support_rows","offset_rows")},indent=2))


if __name__=="__main__":
    main()
