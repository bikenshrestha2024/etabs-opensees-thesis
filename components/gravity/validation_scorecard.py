"""Non-acceptance-aware ETABS/OpenSees gravity diagnostic scoreboard.

Reads only recorded native evidence. Numeric tolerances are diagnostic
screening parameters, not structural code acceptance criteria.
[REF docs/source/components/gravity/validation_scorecard.py.md]
"""
from __future__ import annotations
import json
import math
from pathlib import Path


def _read(path):
    if not path.is_file():
        return None
    data=json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data,dict) else None


def _num(value):
    try:
        n=float(value)
    except (ValueError,TypeError):
        return None
    return n if math.isfinite(n) else None


def create_gravity_scorecard(export_dir,gravity_dir,comparison_root,missing,oversize,
                             *,global_tolerance_percent=0.5,
                             node_relative_tolerance_percent=5.,
                             node_absolute_tolerance_kN=100.):
    """Produce conservative evidence gates with source file provenance.

    No numerical comparison is relabeled as physical acceptance. A
    'within diagnostic tolerance' value is merely one prerequisite.
    [REF components/validation/gravity_node_comparison.py compare_support_nodes]
    """
    export_dir=Path(export_dir)
    gravity_dir=Path(gravity_dir)
    comparison_root=Path(comparison_root)
    cfg=_read(export_dir/"OpenSees_Complete_Model_Config_V118.json")
    beam=_read(export_dir/"ETABS_OpenSees_Beam_Weight_Reconciliation.json")
    native_beam=_read(export_dir/"ETABS_Native_Assignment_Gravity_Quantity_Audit.json")
    union=_read(export_dir/"OpenSees_Joint_Volume_Ownership_Audit.json")
    run=_read(gravity_dir/"Gravity_Result_V110.json")
    direct_path=comparison_root/"Gravity_ETABS_OpenSees_Direct"/"Direct_Gravity_Comparison.json"
    direct=_read(direct_path)

    rows=[]
    def add(key,label,value,status,reason,evidence):
        rows.append(dict(key=key,label=label,value=value,status=status,
                         reason=reason,evidence=str(evidence)))
    beam_policy=(beam or {}).get("policy")
    mode=(cfg or {}).get("etabs_beam_weight_policy")
    verified=(cfg or {}).get("etabs_clear_beam_weight_confirmed")
    beam_evidence=export_dir/"ETABS_OpenSees_Beam_Weight_Reconciliation.json"
    if beam is None or cfg is None:
        add("beam_weight","Structural self-weight / frame end offsets",None,
            "MISSING_EVIDENCE","Source configuration or beam audit unavailable",beam_evidence)
    else:
        gross=_num(beam.get("gross_beam_weight_kN"))
        selected=_num(beam.get("selected_beam_weight_kN"))
        potential=_num(beam.get("potential_offset_reduction_kN"))
        detail=dict(configuration_policy=mode,exported_policy=beam_policy,
            verified_source_option=verified,gross_beam_weight_kN=gross,
            selected_beam_weight_kN=selected,potential_offset_weight_kN=potential,
            unresolved_offset_count=beam.get("unresolved_offset_count"))
        if mode!=beam_policy:
            status="INCONSISTENT_INPUTS"
            reason="Config and audit beam weight modes differ: rebuild source model"
        elif mode=="GROSS_SECTION_LENGTH":
            status="GROSS_BEAM_WEIGHT_ACTIVE"
            reason="No beam clear-length reduction applied; compare source self weight and physical overlap independently"
        elif mode=="ETABS_BEAM_CLEAR_LENGTH" and verified is True and beam.get("unresolved_offset_count")==0:
            if (native_beam and
                native_beam.get("opensees_beam_crosswalk_status")
                    =="SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH" and
                native_beam.get("clear_candidate_matches_native_quantity") is True):
                status="NATIVE_ETABS_BEAM_QUANTITY_CONFIRMED"
                reason=("Original ETABS beam material list, all original beam IDs, "
                        "lengths and offsets agree with selected clear-length quantity. "
                        "Local reactions, stiffness and seismic preload remain unverified")
            else:
                status="MISSING_NATIVE_BEAM_QUANTITY_PROOF"
                reason=("Source config selected beam clear-length but matching "
                        "independent native ETABS assignment workbook evidence was not found")
        else:
            status="UNVERIFIED_BEAM_WEIGHT_CORRECTION"
            reason="Clear-span mode lacks reviewed source option or complete offset data"
        add("beam_weight","Structural self-weight / frame end offsets",detail,status,reason,beam_evidence)

    owner_policy=(union or {}).get("policy")
    add("joint_volume","Beam-column-slab-wall overlap ownership",
        dict(policy=owner_policy,
             potential_overlapping_weight_kN=_num((union or {}).get("potentially_duplicated_RCC_weight_kN")),
             physical_geometry_verified=(union or {}).get("geometry_verified")),
        "GEOMETRY_NOT_VERIFIED" if not (union or {}).get("geometry_verified") else
        "GEOMETRY_REVIEW_RECORDED",
        "Rectangular union is a sensitivity diagnostic, not a deduction to add to ETABS beam offsets",
        export_dir/"OpenSees_Joint_Volume_Ownership_Audit.json")

    run_ok=bool(run and run.get("ok"))
    add("solver","OpenSees full gravity numerical solver",
        (run or {}).get("report"),"SOLVER_CONVERGED" if run_ok else "MISSING_OR_FAILED",
        "A converged force balance is not ETABS equivalence",
        gravity_dir/"Gravity_Result_V110.json")

    etabs=_num((direct or {}).get("etabs_base_FZ_kN"))
    opensees=_num((direct or {}).get("opensees_support_FZ_kN"))
    # A direct comparison may have been generated against an older
    # single gravity run. Reject it as evidence for a newly rebuilt model.
    current_reaction=_num((run or {}).get("report",{}).get("support_vertical_reaction_kN"))
    stale=(opensees is not None and current_reaction is not None and
           abs(opensees-current_reaction)>max(0.1,abs(current_reaction)*1e-6))
    delta=(opensees-etabs) if etabs is not None and opensees is not None else None
    pct=100.*abs(delta)/abs(etabs) if delta is not None and etabs!=0 else None
    global_details=dict(etabs_kN=etabs,opensees_kN=opensees,
                        current_run_reaction_kN=current_reaction,
                        direct_comparison_stale=stale,
                        opensees_minus_etabs_kN=delta,difference_percent_of_etabs=pct,
                        screening_tolerance_percent=global_tolerance_percent)
    if stale:
        status="STALE_COMPARISON_REBUILD_AND_RECOMPARE"
        reason="ETABS direct comparison uses a different OpenSees reaction total from the current selected run"
    elif pct is None:
        status="MISSING_ETABS_DIRECT_EVIDENCE"
        reason="Real ETABS/OpenSees global reaction comparison required"
    elif pct>global_tolerance_percent:
        status="NOT_VALIDATED"
        reason="Total gravity difference exceeds diagnostic tolerance; do not mark ETABS equivalence"
    else:
        status="WITHIN_SCREENING_TOLERANCE_NOT_ACCEPTED"
        reason="Global agreement alone cannot validate support load path or physical weight"
    add("global","Global gravity load agreement",global_details,status,reason,direct_path)

    nodes=(direct or {}).get("node_comparison") or {}
    top=(direct or {}).get("top_node_discrepancies") or []
    valid=int(nodes.get("valid_one_to_one_global_z_count",0) or 0)
    missing_pairs=sum(int(nodes.get(k,0) or 0) for k in (
        "axis_unverified_count","ambiguous_count","etabs_unmatched_count",
        "opensees_unmatched_count"))
    worst=max((_num(x.get("abs_delta_kN")) or 0. for x in top),default=None)
    # Both abs and relative screening are diagnostic only: avoid false
    # PASS for small ETABS zero-reaction supports with large OpenSees Rz.
    large=[]
    for x in top:
        error=_num(x.get("abs_delta_kN"))
        ref=_num(x.get("etabs_global_rz_kN"))
        if error is None or ref is None:
            continue
        if error>node_absolute_tolerance_kN and (
                ref==0 or error/abs(ref)*100>node_relative_tolerance_percent):
            large.append(dict(etabs_point=x.get("etabs_point"),
                opensees_node=x.get("opensees_node"),
                discrepancy_kN=error,etabs_reaction_kN=ref))
    if stale:
        node_status="STALE_COMPARISON_REBUILD_AND_RECOMPARE"
        node_reason="Individual support reactions are from an older OpenSees result; rerun ETABS comparison for current source-support run"
    elif not valid or missing_pairs:
        node_status="MISSING_OR_AMBIGUOUS_EVIDENCE"
        node_reason="Incomplete verified source-to-response support mapping"
    elif large:
        node_status="NOT_VALIDATED"
        node_reason="Large individual foundation reaction differences remain"
    elif not top:
        node_status="MISSING_REACTION_DETAIL"
        node_reason="No individual discrepancy records for per-support check"
    else:
        node_status="WITHIN_SCREENING_TOLERANCE_NOT_ACCEPTED"
        node_reason="Only mapped numeric reaction screening passed; support connectivity still needs verification"
    add("foundation","Individual foundation reactions",
        dict(verified_matches=valid,unverified_or_unmatched=missing_pairs,
             largest_reported_difference_kN=worst,large_difference_examples=large[:10],
             screening_absolute_kN=node_absolute_tolerance_kN,
             screening_relative_percent=node_relative_tolerance_percent),
        node_status,node_reason,direct_path)

    required=[x for x in missing if x.get("required")]
    optional=[x for x in missing if not x.get("required")]
    add("evidence","Evidence collection",
        dict(zip_status="CREATED_BY_EXPORTER",optional_missing_count=len(optional),
             required_missing_count=len(required),oversized_omitted_count=len(oversize),
             missing_files=missing,oversized_files=oversize),
        "INCOMPLETE" if (required or optional or oversize) else "NO_REPORTED_GAPS",
        "Review the exact missing file list, not only the count; missing diagnostic files are not invented",
        "EVIDENCE_MANIFEST.json")

    blocker_keys=("global","foundation","joint_volume","beam_weight")
    blockers=[r for r in rows if r["key"] in blocker_keys and
              r["status"] not in ("WITHIN_SCREENING_TOLERANCE_NOT_ACCEPTED",
                                  "NATIVE_ETABS_BEAM_QUANTITY_CONFIRMED",
                                  "GEOMETRY_REVIEW_RECORDED")]
    return dict(schema="gravity-validation-scorecard-v1",
        conclusion="NOT_STRUCTURALLY_VALIDATED",
        explanation="Even if every numerical screen passes, ETABS/OpenSees equivalence requires geometry, section stiffness, connectivity, applied source loads and original support model review",
        thresholds_kind="DIAGNOSTIC_ONLY_NOT_NBC_CODE_ACCEPTANCE",
        rows=rows,unresolved_gates=[r["key"] for r in blockers],
        corrected_gravity_model_certified=False)


def save_gravity_scorecard(folder,scorecard):
    """Persist the same scoreboard in JSON, CSV and readable text.

    [REF docs/source/components/gravity/validation_scorecard.py.md]
    """
    import csv
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/"GRAVITY_VALIDATION_SCORECARD.json"
    path.write_text(json.dumps(scorecard,indent=2,allow_nan=False),encoding="utf-8")
    with (folder/"GRAVITY_VALIDATION_SCORECARD.csv").open(
        "w",newline="",encoding="utf-8-sig") as stream:
        w=csv.DictWriter(stream,fieldnames=["check","status","result","reason","evidence"])
        w.writeheader()
        for item in scorecard["rows"]:
            w.writerow(dict(check=item["label"],status=item["status"],
                result=json.dumps(item["value"],ensure_ascii=False),
                reason=item["reason"],evidence=item["evidence"]))
    lines=["GRAVITY / ETABS VALIDATION SCORECARD",
           "CONCLUSION: "+scorecard["conclusion"],
           "Only numeric diagnostics; NOT code acceptance.",""]
    for item in scorecard["rows"]:
        lines.append(item["label"]+" | "+item["status"])
        lines.append("  "+item["reason"])
        lines.append("  "+json.dumps(item["value"],ensure_ascii=False))
    (folder/"GRAVITY_VALIDATION_SCORECARD.txt").write_text(
        "\n".join(lines)+"\n",encoding="utf-8")
    return path
