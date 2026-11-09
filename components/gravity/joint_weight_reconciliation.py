"""Audit actual gravity quantity scenarios without changing loads or masses.

The original ETABS material quantity and self-weight conventions are independent
acceptance evidence. This module deliberately does NOT make a model correction.
Units kN, m. See docs/review/GRAVITY_JOINT_SELF_WEIGHT_20261109.md.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

CATEGORIES = ("COLUMN", "SHEAR WALL", "FLOOR", "BEAM")
ALLOWED_PAIR = {f"{a}_OVERLAPS_{b}" for a in CATEGORIES for b in CATEGORIES}


def _load(path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Source gravity quantity audit missing: {path}")
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict):
        raise ValueError(f"Invalid quantity source JSON: {path}")
    return result


def _number(value, label, nonnegative=False):
    try:
        result = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{label} is not numeric") from exc
    if not math.isfinite(result) or (nonnegative and result < -1e-7):
        raise ValueError(f"{label} not finite/nonnegative")
    return result


def _close(a, b, label):
    if abs(a-b) > max(0.01, abs(a)*1e-8, abs(b)*1e-8):
        raise ValueError(f"{label}: quantities do not conserve: {a}, {b}")


def reconcile_joint_weight_scenarios(source_folder, output_folder,
                                    applied_total_kN, etabs_total_kN=None,
                                    *, by_component=None):
    """Write independent, non-applied scenario and intersection reconciliation.

    Source RCC geometrical assumptions are NOT sufficient for activating a
    quantity correction. Reject contradictory ledgers, no fitted adjustments.
    """
    src = Path(source_folder).expanduser().resolve()
    out = Path(output_folder).expanduser().resolve()
    ledger_path = src / "OpenSees_Joint_Volume_Ownership_Audit.json"
    beam_path = src / "ETABS_OpenSees_Beam_Weight_Reconciliation.json"
    slab_path = src / "Gravity_Slab_Self_Weight_Audit.json"
    cfg_path = src / "OpenSees_Complete_Model_Config_V118.json"
    ledger, beam, slab, cfg = map(_load,
                                  (ledger_path, beam_path, slab_path, cfg_path))
    if ledger.get("schema") != "joint-volume-ownership-v1":
        raise ValueError("Unexpected joint ledger schema")
    if beam.get("schema") != "beam-self-weight-end-offset-v1":
        raise ValueError("Unexpected original beam offset audit schema")
    if cfg.get("joint_volume_weight_policy", "AUDIT_ONLY") != ledger.get("policy"):
        raise ValueError("Source config and geometric ownership policy differ")
    if cfg.get("etabs_beam_weight_policy", "GROSS_SECTION_LENGTH") != beam.get("policy"):
        raise ValueError("Source config and original beam self-weight policy differ")
    gross = _number(ledger["gross_RCC_weight_kN"], "gross RCC", True)
    net = _number(ledger["net_RCC_weight_kN"], "net RCC", True)
    overlap = _number(ledger["potentially_duplicated_RCC_weight_kN"],
                      "geometric potential overlap", True)
    _close(gross-net, overlap, "RCC weight conservation")
    rows = ledger.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("No source RCC solid records")
    category = {name: dict(gross=0., net=0., overlap=0., elements=0)
                for name in CATEGORIES}
    for r in rows:
        kind = r.get("category")
        if kind not in category:
            raise ValueError(f"Unexpected RCC solid: {kind}")
        gross_i = _number(r["gross_weight_kN"], "solid gross", True)
        net_i = _number(r["net_weight_kN"], "solid net", True)
        removed_i = _number(r["removed_weight_kN"], "solid overlap", True)
        _close(gross_i, net_i+removed_i, "solid volume ownership")
        t = category[kind]
        t["gross"] += gross_i
        t["net"] += net_i
        t["overlap"] += removed_i
        t["elements"] += 1
    _close(sum(x["gross"] for x in category.values()), gross, "RCC gross groups")
    _close(sum(x["net"] for x in category.values()), net, "RCC net groups")
    pairs = ledger.get("overlap_pair_weight_kN", {})
    if not isinstance(pairs, dict) or any(x not in ALLOWED_PAIR for x in pairs):
        raise ValueError("Unexpected overlapping physical solid category")
    pair_total = sum(_number(v, f"pair {k}", True) for k,v in pairs.items())
    _close(pair_total, overlap, "Nonoverlapping union attribution")
    _close(category["BEAM"]["gross"],
           _number(beam["gross_beam_weight_kN"], "beam gross", True),
           "Original beam count/meshing gross conservation")
    _close(category["FLOOR"]["gross"],
           _number(slab["gross_slab_self_weight_kN"], "slab gross", True),
           "Slab original area/mesh quantity conservation")
    original_beams = beam.get("rows", [])
    if len(original_beams) != int(beam.get("beam_count", -1)):
        raise ValueError("Original-object beam count inconsistent")
    clear_candidate = _number(beam["potential_offset_reduction_kN"],
                              "beam end-zone candidate", True)
    if clear_candidate > category["BEAM"]["gross"] + 0.01:
        raise ValueError("Candidate clear beam weight exceeds original beams")
    if beam.get("policy") == "GROSS_SECTION_LENGTH":
        _close(_number(beam["selected_beam_weight_kN"], "selected beam weight"),
               category["BEAM"]["gross"], "Current gross beam policy")
    applied = _number(applied_total_kN, "OpenSees applied gravity", True)
    etabs = None if etabs_total_kN is None else _number(
        etabs_total_kN, "ETABS base reaction", True)
    live = dict(by_component or {})
    for key,val in live.items():
        _number(val, f"applied component {key}")
    # Distinct, EXCLUSIVE interpretations: beam clear-span and geometric RCC
    # union cannot be subtracted together because their footprints intersect.
    # An applied correction under either route needs native ETABS quantities.
    scenarios = [
        dict(id="CURRENT_ASSEMBLED", total_kN=applied, correction_kN=0.,
             applied=True, interpretation="Current solved gravity; no proposed deductions"),
        dict(id="BEAM_CLEAR_LENGTH_ONLY", total_kN=applied-clear_candidate,
             correction_kN=clear_candidate, applied=False,
             interpretation="Only original source beam end offsets; ETABS weight rule unverified"),
        dict(id="GEOMETRIC_R​​CC_SINGLE_OWNER_ONLY".replace("\u200b", ""),
             total_kN=applied-overlap, correction_kN=overlap, applied=False,
             interpretation="Disjoint RCC box union; source insertion and ETABS rule unverified"),
    ]
    for item in scenarios:
        item["etabs_minus_scenario_kN"] = (
            etabs-item["total_kN"] if etabs is not None else None)
        item["scenario_minus_etabs_kN"] = (
            item["total_kN"]-etabs if etabs is not None else None)
        item["geometry_validated"] = bool(ledger.get("geometry_verified", False))
        item["etabs_material_quantity_validated"] = False
        item["accepted_weight_correction"] = False
    reasons = [
        "Full floor-to-floor columns and walls are represented in source gross volumes; their union with slabs and beams may overlap.",
        "Original floor polygons have their own actual openings: subtract only intersection volumes actually present, not a second global footprint deduction.",
        "Slab-column and slab-wall potential intersections are assigned to columns/walls in this audit; slab-beam intersections belong to the later beam in ownership priority.",
        "Beam clear spans depend on actual source geometry, offsets, insertion points and nearby walls; a column-only formula does not describe every connection.",
        "Brace automatic end offsets default to zero in ETABS, but brace gusset/connection physical cuts are not established in this RCC solid ledger.",
        "Do not use simultaneous clear-span and geometric-union deductions; they double count shared end-zone volumes.",
        "ETABS direct base reaction, even when identical to a candidate scenario, is not independent ETABS per-object material quantity proof.",
        "A verified 32-reaction-bearing joint subset is the primary diagnostic; 44 other ETABS zero-reaction points remain separate mesh/constraint evidence, not automatically deleted supports.",
    ]
    report = {
        "schema": "gravity-joint-weight-reconciliation-v1",
        "model_source": str(src),
        "source_hashes_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (ledger_path, beam_path, slab_path, cfg_path)
        },
        "current_joint_volume_policy": ledger["policy"],
        "current_beam_weight_policy": beam["policy"],
        "native_etabs_quantity_verified": False,
        "geometry_verified": bool(ledger.get("geometry_verified", False)),
        "current_gravity_kN": applied,
        "etabs_reference_kN": etabs,
        "rcc_gross_weight_kN": gross,
        "rcc_geometric_union_net_kN": net,
        "rcc_potential_overlap_kN": overlap,
        "beam_end_offset_candidate_kN": clear_candidate,
        "original_beam_objects": len(original_beams),
        "beam_finite_element_segments": category["BEAM"]["elements"],
        "by_R​​CC_type".replace("\u200b", ""): category,
        "overlap_relationships_kN": pairs,
        "source_omissions_outside_rectangular_RCC": ledger.get("unsupported_items", []),
        "applied_gravity_components_kN": live,
        "scenarios_EXCLUSIVE_NOT_APPLIED": scenarios,
        "automatic_gravity_correction_kN": 0.0,
        "mass_or_stiffness_modified": False,
        "status": "HYPOTHESIS_NUMERIC_SCREEN_ONLY_NOT_ETABS_WEIGHT_VALIDATED",
        "engineering_explanations": reasons,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "Gravity_Joint_Weight_Reconciliation.json").write_text(
        json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    with (out / "Gravity_Joint_Weight_Scenarios.csv").open(
            "w", newline="", encoding="utf-8-sig") as f:
        fields = ["id", "total_kN", "correction_kN", "applied",
                  "scenario_minus_etabs_kN", "geometry_validated",
                  "etabs_material_quantity_validated", "accepted_weight_correction",
                  "interpretation"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(scenarios)
    with (out / "Gravity_Joint_Weight_By_Solid.csv").open(
            "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["solid_type", "mesh_segments_or_cells",
                         "gross_kN", "potential_overlap_kN", "net_kN"])
        for name, entry in category.items():
            writer.writerow([name, entry["elements"], entry["gross"],
                             entry["overlap"], entry["net"]])
    return report
