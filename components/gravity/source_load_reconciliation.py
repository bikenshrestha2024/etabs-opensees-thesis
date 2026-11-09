"""Audit all exported gravity sources without fitting loads to ETABS reactions.

[REF docs/source/components/gravity/source_load_reconciliation.py.md]
The assembled load-provenance ledger is the authoritative attribution of
OpenSees source loads. These checks NEVER edit gravity, stiffness or mass.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import os
from collections import defaultdict
from pathlib import Path

TOL_REL=1.e-8
COMPONENTS=("self_weight_beam","self_weight_column","self_weight_brace",
            "self_weight_floor","self_weight_shear wall",
            "area_load","frame_load","point_load")
REQUIRED=("OpenSees_Complete_Model_Data_V118.json",
          "OpenSees_Complete_Model_Config_V118.json",
          "OpenSees_Source_Model_Metadata_V118.json",
          "OpenSees_Load_Conversion_Audit.json",
          "ETABS_OpenSees_Beam_Weight_Reconciliation.json")


def _load_json(path,required=True):
    path=Path(path)
    if not path.exists():
        if required: raise FileNotFoundError("Required gravity source: "+str(path))
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def source_load_audit(model_folder,gravity_profile,output_folder,*,etabs_total_kN=None):
    """Make an independently checkable load-by-source ledger.

    [REF components/model/assembly.py add and apply_gravity_profile]
    """
    folder=Path(model_folder).resolve()
    out=Path(output_folder).resolve()
    data=_load_json(folder/REQUIRED[0])
    cfg=_load_json(folder/REQUIRED[1])
    meta=_load_json(folder/REQUIRED[2])
    conversion=_load_json(folder/REQUIRED[3])
    beam=_load_json(folder/REQUIRED[4])
    # Geometry overlap is a separate potential issue from accidental
    # self-weight pattern duplication. Audit it without subtracting loads.
    joint=_load_json(folder/"OpenSees_Joint_Volume_Ownership_Audit.json",
                     required=False)
    pattern_count=_load_json(folder/"Gravity_Single_Count_Self_Weight_Audit.json",
                             required=False)
    slab_physical=_load_json(folder/"Gravity_Slab_Self_Weight_Audit.json",
                             required=False)
    native_weight=_load_json(folder/"Gravity_Physical_Weight_Modifier_Audit.json",
                             required=False)
    if not isinstance(data.get("load_provenance"),list) or not data["load_provenance"]:
        raise ValueError("Export has no complete load_provenance; rebuild with current exporter")
    from OpenSees_Complete_Export_V118 import apply_gravity_profile
    selected_data=dict(data)
    selected_context=apply_gravity_profile(selected_data,cfg,gravity_profile,
                                meta.get("pattern_types",{}))
    factors=selected_context["factors"]
    if not isinstance(factors,dict):
        raise ValueError("Gravity factors unavailable")
    by_source=defaultdict(float)
    by_pattern=defaultdict(float)
    by_component=defaultdict(float)
    rows=[]
    for i,item in enumerate(data["load_provenance"],1):
        pattern=str(item["pattern"])
        if pattern not in factors:
            raise ValueError("Unclassified load pattern "+pattern)
        factor=float(factors[pattern])
        unfactored=float(item["downward_kN"])
        if not all(math.isfinite(x) for x in (factor,unfactored)) or factor<0:
            raise ValueError("Nonfinite/negative source load or factor at row "+str(i))
        applied=unfactored*factor
        component=str(item.get("component","UNCLASSIFIED"))
        source=str(item.get("source","UNKNOWN"))
        by_source[(pattern,component,source)]+=applied
        by_pattern[pattern]+=applied
        by_component[component]+=applied
        rows.append(dict(row=i,pattern=pattern,component=component,
                         source=source,node=item.get("node"),
                         unfactored_kN=unfactored,gravity_factor=factor,
                         applied_kN=applied))
    total=sum(by_pattern.values())
    expected=float(selected_data["total_downward_load_kN"])
    pattern_expected=selected_data["gravity_by_pattern_kN"]
    delta=total-expected
    tolerance=max(.01,abs(expected)*TOL_REL)
    mismatches=[dict(pattern=k,source_sum_kN=by_pattern.get(k,0.),
                     assembled_sum_kN=v)
                for k,v in pattern_expected.items()
                if abs(by_pattern.get(k,0.)-float(v))>max(.01,abs(float(v))*TOL_REL)]
    if abs(delta)>tolerance or mismatches:
        raise ValueError("Load provenance does not reconcile to assembled gravity: "+
                         f"sum={total:.9f}, assembled={expected:.9f}, "
                         f"delta={delta:.9f}, pattern discrepancies={mismatches[:6]}")
    # Verify actual assembled floor dead-weight nodal forces independently
    # against source floor geometry and true ETABS pattern allocations.
    physical_slab_weight=None
    expected_applied_slab_weight=None
    floor_weight_from_assembled=by_component.get("self_weight_floor",0.)
    if slab_physical is not None:
        if pattern_count is None:
            raise ValueError("Slab physical audit exists but self-weight allocation audit is missing")
        physical_slab_weight=float(slab_physical["gross_slab_self_weight_kN"])
        allocation=0.
        for entry in pattern_count["etabs_pattern_rows"]:
            pat=str(entry["pattern"])
            multiplier=float(entry["etabs_self_weight_multiplier"])
            if not math.isfinite(multiplier) or multiplier<0:
                raise ValueError("Invalid slab self-weight pattern multiplier for "+pat)
            # An ETABS pattern with ZERO self-weight adds ZERO slab gravity,
            # even if the active gravity profile has no factor for it.
            # EQX/EQY, Roof Live and derived cases must not be assigned
            # invented factors merely to satisfy this audit.
            if multiplier==0.0:
                continue
            if pat not in factors:
                raise ValueError("Slab self-weight pattern factor missing for NONZERO "+pat)
            factor=float(factors[pat])
            if not math.isfinite(factor) or factor<0:
                raise ValueError("Invalid slab self-weight gravity factor for "+pat)
            allocation+=multiplier*factor
        expected_applied_slab_weight=physical_slab_weight*allocation
        if abs(floor_weight_from_assembled-expected_applied_slab_weight)>max(
                .01,abs(expected_applied_slab_weight)*1e-8):
            raise ValueError(
                "SLAB SELF-WEIGHT DOUBLE/OMISSION RISK: original source slab area*"
                "thickness*unit weight, after pattern multipliers, is "
                f"{expected_applied_slab_weight:.6f} kN but actual OpenSees "
                f"self_weight_floor load vectors total {floor_weight_from_assembled:.6f} kN")
    beam_delta=float(beam.get("potential_offset_reduction_kN",0))
    beam_gross=float(beam.get("gross_beam_weight_kN",0))
    if not all(math.isfinite(x) and x>=0 for x in (beam_delta,beam_gross)):
        raise ValueError("Nonfinite beam offset weight audit")
    beam_policy=cfg.get("etabs_beam_weight_policy","GROSS_SECTION_LENGTH")
    # Conditional interpretation; never substitute a global ETABS reaction
    # difference for evidence of the native ETABS Self Weight Option.
    predicted_after=expected-beam_delta if beam_policy=="GROSS_SECTION_LENGTH" else expected
    etabs=None
    if etabs_total_kN is not None:
        etabs=float(etabs_total_kN)
        if not math.isfinite(etabs) or etabs<=0:raise ValueError("Invalid ETABS FZ")
    native_beam_path=folder/"ETABS_Beam_Material_List_Reviewed.csv"
    native_beam_proof=None
    if native_beam_path.is_file():
        # Existing conservative reviewer checks every beam's source-offset
        # metadata and aggregate native material-list weight. It never edits.
        from Gravity_Safe_Engineering_Review_V1 import beam_checks
        native_beam_proof=beam_checks(folder,source_beam_csv=native_beam_path)
        if native_beam_proof.get("candidate_eligible") is True:
            native_beam_proof["status"]="NATIVE_MATERIAL_WEIGHT_NUMERIC_MATCH_CANDIDATE_ONLY"
        else:
            native_beam_proof["status"]="NATIVE_MATERIAL_WEIGHT_NOT_FULLY_VERIFIED"
    # Reproduce the original geometric overlap review inside EACH gravity-run
    # evidence directory, rather than requiring the reviewer to locate an
    # unrelated exporter folder. Never alter applied nodal loads or mass.
    joint_overlap_review = None
    joint_overlap_evidence = {
        "status": "MISSING_SOURCE_LEDGER_NOT_APPLIED",
        "source_path": str(folder / "OpenSees_Joint_Volume_Ownership_Audit.json"),
        "source_sha256": None,
        "files": [],
        "applied_gravity_correction_kN": 0.0,
    }
    if joint is not None:
        source_joint = folder / "OpenSees_Joint_Volume_Ownership_Audit.json"
        joint_hash = hashlib.sha256(source_joint.read_bytes()).hexdigest()
        declared_policy = cfg.get("joint_volume_weight_policy", "AUDIT_ONLY")
        if joint.get("policy") != declared_policy:
            raise ValueError(
                "Joint-overlap source ledger policy differs from current "
                "gravity model configuration: " + str(joint.get("policy"))
                + " vs " + str(declared_policy))
        from components.gravity.joint_overlap_review import review_joint_overlap
        joint_overlap_review = review_joint_overlap(
            joint, out,
            beam_offset_candidate_kN=beam_delta,
            observed_global_gap_kN=(expected-etabs if etabs is not None else None))
        joint_overlap_evidence = {
            "status": "SOURCE_LEDGER_GEOMETRY_AUDITED_NOT_ETABS_VERIFIED",
            "source_path": str(source_joint),
            "source_sha256": joint_hash,
            "policy": joint.get("policy"),
            "geometry_verified": joint.get("geometry_verified", False),
            "potential_overlap_kN": joint_overlap_review[
                "actual_ledger_global_overlap_kN"],
            "files": [
                str(out / "Gravity_Joint_Type_Overlap_Review.json"),
                str(out / "Gravity_Joint_Type_Overlap_Review.csv"),
                str(out / "Gravity_Joint_Type_Overlap_Review.xlsx"),
                str(out / "Gravity_Joint_Type_Overlap_Solids.csv"),
            ],
            "applied_gravity_correction_kN": 0.0
            if declared_policy == "AUDIT_ONLY" else None,
        }
        # When a reviewed single-owner volume policy was explicitly applied
        # in the SOURCE EXPORT, do not misrepresent its correction as zero.
        if declared_policy == "VERIFIED_SINGLE_OWNER":
            joint_overlap_evidence["status"] = (
                "SOURCE_MODEL_ALREADY_CORRECTED_REQUIRES_ETABS_VERIFICATION")
            joint_overlap_evidence["applied_gravity_correction_kN"] = None
    note=(
      "POTENTIAL_ONLY: clear-span deduction not enabled. Confirm original ETABS "
      "Material List per source beam, frame Self Weight Option, end offsets and "
      "any joint solid-volume deductions before adopting ETABS_BEAM_CLEAR_LENGTH.")
    if beam_policy=="ETABS_BEAM_CLEAR_LENGTH":
        note="ACTIVE: beam clear-length correction is in source model; check native ETABS corroboration"
    info=dict(schema="assembled-gravity-source-reconciliation-v1",
          profile=gravity_profile,applied_total_kN=expected,
          provenance_applied_total_kN=total,
          provenance_balance_error_kN=delta,
          gravity_by_pattern_kN=dict(sorted(by_pattern.items())),
          gravity_by_component_kN=dict(sorted(by_component.items())),
          beam_weight_policy=beam_policy,
          gross_beam_weight_kN=beam_gross,
          potential_beam_offset_reduction_kN=beam_delta,
          post_offset_total_hypothesis_kN=predicted_after,
          etabs_independent_base_reaction_kN=etabs,
          source_to_etabs_difference_kN=(expected-etabs if etabs is not None else None),
          hypothetical_post_offset_difference_kN=(predicted_after-etabs if etabs is not None else None),
          beam_offset_verified=bool(beam.get("etabs_clear_weight_confirmed",False)),
          beam_offset_unresolved_count=beam.get("unresolved_offset_count"),
          self_weight_components=[k for k in by_component if k.startswith("self_weight_")],
          unclassified_components=[k for k in by_component if k=="UNCLASSIFIED"],
          status="SOURCE_LEDGER_RECONCILED_NOT_ETABS_VALIDATED",
          engineering_caveat=note,
          etabs_source_material_weight_comparison=(
              "ETABS_BEAM_MATERIAL_LIST_CANDIDATE_REVIEWED" if native_beam_proof
              and native_beam_proof.get("candidate_eligible") else
              "ETABS_BEAM_MATERIAL_LIST_PROOF_BLOCKED" if native_beam_proof else
              "INDEPENDENT_ETABS_MATERIAL_LIST_REQUIRED"),
          native_beam_proof=native_beam_proof,
          single_count_pattern_audit=pattern_count,
          native_etabs_weight_modifier_verified=bool(
              native_weight and native_weight.get("source_weight_modifier_verified")),
          etabs_weight_modifier_audit_status=(
              native_weight.get("status") if native_weight else "NOT_CAPTURED"),
          physical_slab_gross_self_weight_kN=physical_slab_weight,
          expected_full_gravity_slab_self_weight_kN=expected_applied_slab_weight,
          actual_applied_slab_self_weight_kN=floor_weight_from_assembled,
          slab_source_conservation_verified=(slab_physical is not None and
              expected_applied_slab_weight is not None),
          geometric_joint_ownership_audit=(
              {"policy":joint.get("policy"),
               "gross_RCC_weight_kN":joint.get("gross_RCC_weight_kN"),
               "net_RCC_weight_kN":joint.get("net_RCC_weight_kN"),
               "potentially_duplicated_RCC_weight_kN":
                    joint.get("potentially_duplicated_RCC_weight_kN"),
               "interpretation":"GEOMETRY AUDIT; never add to the beam clear-length deduction"}
              if joint else None),
          joint_overlap_run_evidence=joint_overlap_evidence,
          active_native_model_identity="NOT_VERIFIED_BY_THIS_OFFLINE_AUDIT")
    if native_weight is None:
        info["status"]="NATIVE_ETABS_WEIGHT_MODIFIERS_NOT_VERIFIED"
    elif native_weight.get("source_weight_conflict"):
        raise ValueError("Native ETABS source weight modifier not unity: "
                         "physical gravity source is not equivalent")
    elif not native_weight.get("source_weight_modifier_verified"):
        info["status"]="NATIVE_ETABS_WEIGHT_MODIFIERS_NOT_VERIFIED"
    if pattern_count is None:
        info["status"]="LEGACY_EXPORT_SINGLE_COUNT_NOT_VERIFIED"
    elif slab_physical is None:
        info["status"]="LEGACY_EXPORT_SLAB_PHYSICAL_WEIGHT_NOT_VERIFIED"
    elif pattern_count.get("status")!="SELF_WEIGHT_PATTERN_ACCOUNTING_PASS_NOT_JOINT_SOLID_VALIDATED":
        info["status"]="SELF_WEIGHT_PATTERN_ACCOUNTING_NOT_VERIFIED"
    if info["unclassified_components"]:
        info["status"]="SOURCE_COMPONENT_CLASSIFICATION_INCOMPLETE"
    # Older source exports lack the complete geometric and per-beam schema.
    # Do not break their established source-load diagnostics, but never
    # fabricate an available joint quantity audit for legacy inputs.
    quantities_ready = (
        joint is not None and slab_physical is not None
        and beam.get("schema") == "beam-self-weight-end-offset-v1")
    if quantities_ready:
        from components.gravity.joint_weight_reconciliation import (
            reconcile_joint_weight_scenarios)
        weight_scenarios = reconcile_joint_weight_scenarios(
            folder, out, expected, etabs, by_component=by_component)
        info["joint_weight_scenarios"] = {
            "status": weight_scenarios["status"],
            "rcc_gross_weight_kN": weight_scenarios["rcc_gross_weight_kN"],
            "rcc_potential_overlap_kN":
                weight_scenarios["rcc_potential_overlap_kN"],
            "beam_end_offset_candidate_kN":
                weight_scenarios["beam_end_offset_candidate_kN"],
            "source_hashes_sha256": weight_scenarios["source_hashes_sha256"],
            "automatic_gravity_correction_kN": 0.0,
            "files": [
                str(out/"Gravity_Joint_Weight_Reconciliation.json"),
                str(out/"Gravity_Joint_Weight_Scenarios.csv"),
                str(out/"Gravity_Joint_Weight_By_Solid.csv"),
                str(out/"Gravity_Original_ETABS_Object_Quantities.csv"),
            ],
        }
    else:
        weight_scenarios = None
        info["joint_weight_scenarios"] = {
            "status": "LEGACY_OR_INCOMPLETE_GEOMETRY_EVIDENCE",
            "automatic_gravity_correction_kN": 0.0,
            "files": [],
        }
    # Native ETABS XLSX confirmation is opt-in, source-bound and read-only.
    # It never activates beam length or joint-volume weight corrections.
    original_assignment=os.environ.get("ETABS_GRAVITY_ASSIGNMENT_WORKBOOK", "").strip()
    if original_assignment:
        from components.validation.etabs_assignment_gravity_audit import (
            audit_native_assignment_workbook)
        native_source=audit_native_assignment_workbook(
            original_assignment,out,
            beam_audit_path=folder/"ETABS_OpenSees_Beam_Weight_Reconciliation.json")
        info["etabs_native_assignment_evidence"]={
            "status":native_source["opensees_beam_crosswalk_status"],
            "source_workbook_name":native_source["source_workbook_name"],
            "source_workbook_sha256":native_source["source_workbook_sha256"],
            "native_material_weights_kN":native_source["weights_kN"],
            "native_beam_objects":native_source["native_beam_objects"],
            "clear_candidate_matches_native_quantity":
                native_source.get("clear_candidate_matches_native_quantity"),
            "file":str(out/"ETABS_Native_Assignment_Gravity_Quantity_Audit.json"),
            "automatic_correction_kN":0.0,
        }
        if native_source.get("clear_candidate_matches_native_quantity") is not True:
            raise ValueError("Native ETABS assignment workbook does not confirm "
                             "clear-length beam weight; no gravity weight correction allowed")
    else:
        # The verified source-export proof persists after the environment
        # variable is cleared. Do not falsely report it as missing.
        proof_path=folder/"ETABS_Native_Assignment_Gravity_Quantity_Audit.json"
        if proof_path.is_file():
            proof=_load_json(proof_path)
            if (proof.get("opensees_beam_crosswalk_status") !=
                    "SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH" or
                    proof.get("clear_candidate_matches_native_quantity") is not True):
                raise ValueError("Stored ETABS native assignment evidence is not accepted")
            info["etabs_native_assignment_evidence"]={
                "status":"SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH",
                "source_workbook_name":proof.get("source_workbook_name"),
                "source_workbook_sha256":proof.get("source_workbook_sha256"),
                "native_material_weights_kN":proof.get("weights_kN"),
                "native_beam_objects":proof.get("native_beam_objects"),
                "file":str(proof_path),
                "file_sha256":hashlib.sha256(proof_path.read_bytes()).hexdigest(),
                "automatic_correction_kN":0.0,
            }
        else:
            info["etabs_native_assignment_evidence"]={
                "status":"NOT_CONFIGURED",
                "required_for_verified_clear_weight":"Set ETABS_GRAVITY_ASSIGNMENT_WORKBOOK to original ETABS assignment XLSX",
                "automatic_correction_kN":0.0,
            }
    out.mkdir(parents=True,exist_ok=True)
    (out/"Gravity_Source_Components_Audit.json").write_text(
        json.dumps(info,indent=2,allow_nan=False),encoding="utf-8")
    with (out/"Gravity_Source_Components_Detail.csv").open(
         "w",newline="",encoding="utf-8-sig") as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    with (out/"Gravity_Source_Components_Totals.csv").open(
         "w",newline="",encoding="utf-8-sig") as stream:
        w=csv.writer(stream);w.writerow(["component","applied_downward_kN"])
        for comp,value in sorted(by_component.items()):
            w.writerow([comp,value])
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill
    wb=Workbook();ws=wb.active;ws.title="Source totals"
    ws.append(["Source component","Applied net downward kN"])
    for comp,value in sorted(by_component.items()):
        ws.append([comp,value])
    ws.append(["GRAND TOTAL",total])
    wp=wb.create_sheet("Patterns")
    wp.append(["Load pattern","Full gravity kN","Gravity factor"])
    for pat,value in sorted(by_pattern.items()):
        wp.append([pat,value,float(factors[pat])])
    wd=wb.create_sheet("Source node ledger")
    fields=list(rows[0])
    wd.append(fields)
    for row in rows:wd.append([row.get(k) for k in fields])
    ws2=wb.create_sheet("Audit and hypotheses")
    for k,v in info.items():
        if not isinstance(v,(dict,list)):
            ws2.append([k,v])
    for sheet in wb:
        sheet.freeze_panes="A2";sheet.auto_filter.ref=sheet.dimensions
        sheet.column_dimensions["A"].width=45
        sheet.column_dimensions["B"].width=25
        for c in sheet[1]:
            c.font=Font(color="FFFFFF",bold=True)
            c.fill=PatternFill("solid",fgColor="17365D")
    if weight_scenarios is not None:
        candidates=wb.create_sheet("Exclusive weight scenarios")
        candidates.append(["Scenario","Total kN","Candidate deduction kN",
                           "Difference OpenSees minus ETABS kN",
                           "Currently applied?","ETABS quantity verified?"])
        for entry in weight_scenarios["scenarios_EXCLUSIVE_NOT_APPLIED"]:
            candidates.append([entry["id"],entry["total_kN"],
                               entry["correction_kN"],
                               entry["scenario_minus_etabs_kN"],
                               entry["applied"],
                               entry["etabs_material_quantity_validated"]])
        candidates.freeze_panes="A2"
        candidates.column_dimensions["A"].width=42
        candidates.column_dimensions["B"].width=24
        candidates.column_dimensions["C"].width=27
        candidates.column_dimensions["D"].width=42
        candidates.column_dimensions["E"].width=21
        candidates.column_dimensions["F"].width=29
    joint_sheet=wb.create_sheet("Joint overlap source audit")
    joint_sheet.append(["Evidence", "Value", "Interpretation"])
    for key,value in joint_overlap_evidence.items():
        if isinstance(value,(str,int,float,bool)) or value is None:
            joint_sheet.append([key,value,
                "Read-only source geometry; no ETABS equivalence implied"])
    joint_sheet.append(["beam_offset_candidate_kN",beam_delta,
        "Separate hypothesis, do not add to joint overlap"])
    joint_sheet.append(["observed_ETABS_gap_kN",
        (expected-etabs if etabs is not None else None),
        "Diagnostic only; not an inferred weight correction"])
    joint_sheet.append(["automatic_overlap_deduction","PROHIBITED",
        "Only explicitly reviewed source-export policy can change physical loads"])
    joint_sheet.column_dimensions["A"].width=44
    joint_sheet.column_dimensions["B"].width=78
    joint_sheet.column_dimensions["C"].width=70
    wd.column_dimensions["C"].width=28
    wd.column_dimensions["D"].width=35
    ws2.column_dimensions["B"].width=95
    wb.save(out/"Gravity_Source_Components_Audit.xlsx")
    return info
