"""Offline ETABS reaction-based node selection for the primary gravity case.

Does not infer actual CSI PointObj.GetRestraint from zero FZ. This is a
user-selected main case; native support equivalence remains independently checked.
[REF docs/review/GRAVITY_REACTION_FILTER_DIAGNOSTIC.md]
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from components.validation.gravity_etabs_offline import read_etabs_joint_reactions

PROFILE = "1. DL + LL"
MODE = "ETABS_NONZERO_REACTION_DIAGNOSTIC"
# User-confirmed 32 OpenSees support tags for the present November 2026
# 25-storey project ONLY. Do not silently substitute for other EDB exports.
PROJECT_PRIMARY_32 = (
    76,1,2,75,72,4,5,73,71,3,74,6,7,14,63,70,
    35,42,25,26,51,52,23,24,53,54,8,64,13,69,36,41
)
assert len(PROJECT_PRIMARY_32)==len(set(PROJECT_PRIMARY_32))==32



def classify_supports(etabs_table, connectivity, original_supports, *, tolerance_kN=1e-6):
    """Classify full original support set by signed original ETABS vertical FZ.

    [REF docs/review/GRAVITY_REACTION_FILTER_DIAGNOSTIC.md]
    """
    table = read_etabs_joint_reactions(etabs_table, PROFILE)
    if not isinstance(connectivity, dict):
        connectivity = json.loads(Path(connectivity).read_text(encoding="utf-8-sig"))
    if not isinstance(original_supports, dict):
        raise ValueError("Original supports must be the unmodified assembled-model restraints")
    node_map = {}
    reverse = {}
    for point in connectivity.get("node_map", []):
        name = str(point.get("etabs_point_name", "")).strip()
        tag = str(point.get("opensees_node_tag", "")).strip()
        if not name or not tag:
            continue
        if name in node_map and node_map[name] != tag:
            raise ValueError("Conflicting ETABS point mapping for "+name)
        if tag in reverse and reverse[tag] != name:
            raise ValueError("Multiple ETABS source points map to OpenSees tag "+tag)
        node_map[name] = tag
        reverse[tag] = name
    if not node_map:
        raise ValueError("Source point mapping is unavailable")
    tolerance_kN = float(tolerance_kN)
    if not math.isfinite(tolerance_kN) or tolerance_kN < 0:
        raise ValueError("Reaction-zero tolerance must be finite and nonnegative")
    selected, excluded, details = {}, [], []
    # Never silently omit corrupted source restraints: a missing point
    # changes the physical boundary condition before the 32/76/97 audit.
    original_fixed={}
    for node,flags in original_supports.items():
        if (not isinstance(flags,(list,tuple)) or len(flags)!=6 or
                any(type(flag) not in (bool,int) or flag not in (0,1,False,True)
                    for flag in flags)):
            raise ValueError("Invalid original six-DOF restraint flags at node "+str(node))
        if bool(flags[2]):
            original_fixed[str(node)]=[int(flag) for flag in flags]
    if not original_fixed:
        raise ValueError("No vertical source support restraints in assembled model")
    for tag in sorted(original_fixed, key=lambda s:int(s)):
        unique = reverse.get(tag)
        if not unique or unique not in table:
            raise ValueError("Missing original ETABS Joint Reactions for mapped source support "+tag+
                             "; refusing incomplete/ambiguous support filtering")
        fz = float(table[unique]["etabs_FZ_kN"])
        if not math.isfinite(fz):
            raise ValueError("Invalid ETABS FZ for "+unique)
        keep = abs(fz) > tolerance_kN
        if keep:
            selected[tag] = original_fixed[tag]
        else:
            excluded.append(int(tag))
        details.append(dict(opensees_node=int(tag),etabs_unique=unique,
                            etabs_FZ_kN=fz,selected=keep,
                            source_restraints=original_fixed[tag]))
    unmatched = sorted(set(table)-set(node_map))
    if unmatched:
        raise ValueError("ETABS Joint Reactions include unmapped source points: "+str(unmatched[:12]))
    if len(details) != len(table):
        raise ValueError("ETABS support records and originally fixed source nodes differ; "
                         "review native ETABS restraints and mapping before diagnostic")
    if not selected:
        raise ValueError("All source supports would be removed: refusing gravity run")
    actual=set(map(int,selected))
    expected=set(PROJECT_PRIMARY_32)
    if actual!=expected:
        raise ValueError(
            "PRIMARY ETABS REACTION VALIDATION support list disagrees with this "
            "project's user-confirmed 32 nodes. Missing="+str(sorted(expected-actual))+
            " unexpected="+str(sorted(actual-expected))+
            ". Verify original ETABS table, exact model, mapping and threshold; "
            "do not alter supports to force matching reactions.")
    # Preserve DOF restraints on points whose vertical restraint is not being
    # removed; removed joints are deliberately released for *all* DOFs only
    # in the diagnostic case, and never in the saved model.
    audit = dict(mode=MODE,case=PROFILE,tolerance_kN=tolerance_kN,
                 etabs_total_FZ_kN=sum(t["etabs_FZ_kN"] for t in details),
                 original_support_count=len(original_fixed),
                 kept_support_count=len(selected),released_support_count=len(excluded),
                 released_opensees_nodes=excluded,mapping=details,
                 project_primary_support_tags=list(PROJECT_PRIMARY_32),
                 user_confirmed_32_exact_match=True,
                 project_primary_status="PRIMARY_GRAVITY_CASE_NATIVE_RESTRAINT_EQUIVALENCE_PENDING",
                 source_table=str(Path(etabs_table).resolve()),
                 source_sha256=hashlib.sha256(Path(etabs_table).read_bytes()).hexdigest(),
                 warning="Primary gravity case: ETABS FZ=0 alone does not demonstrate free UZ or six free DOFs. "
                         "Retain 76- and 97-support runs. Review native source restraints "
                         "and internal wall-edge mesh constraints for acceptance.")
    return selected,audit

def matched_primary_32_workbook_comparison(gravity_dir, result):
    """[REF docs/source/components/gravity/comparison_bundle.py.md] Verify saved workbook-derived FZ evidence."""
    from components.inputs.project_output_layout import sha256_file

    if result.get('wall_support_strategy') != MODE or result.get('gravity_profile') != 'GRAVITY_1.0D_1.0L':
        return None
    folder = Path(gravity_dir)
    report_path = folder / 'Primary_32_ETABS_OpenSees_Reactions.json'
    audit_path = folder / 'ETABS_Nonzero_Reaction_Support_Audit.json'
    try:
        report = json.loads(report_path.read_text(encoding='utf-8-sig'))
        audit = json.loads(audit_path.read_text(encoding='utf-8-sig'))
        workbook = Path(audit['source_table'])
        if (audit['case'] != PROFILE or report['original_ETABS_case'] != PROFILE
                or audit.get('user_confirmed_32_exact_match') is not True
                or audit['source_sha256'] != report['original_etabs_table_sha256']
                or workbook.is_symlink() or sha256_file(workbook) != audit['source_sha256']):
            return None
        original_reactions = read_etabs_joint_reactions(workbook, PROFILE)
        if sha256_file(workbook) != audit['source_sha256']:
            return None
        support = set(PROJECT_PRIMARY_32)
        solved = {int(row['node_tag']): float(row['rz_kN']) for row in result['reactions']}
        mapping = {int(row['opensees_node']): row for row in audit['mapping'] if row['selected'] is True}
        rows = {int(row['opensees_node']): row for row in report['node_reactions']}
        if (set(map(int, result['support_node_tags'])) != support or len(result['reactions']) != len(support)
                or len(report['node_reactions']) != len(support) or not support == solved.keys() == mapping.keys() == rows.keys()):
            return None
        discrepancies = []
        native_points = set()
        etabs_total = 0.0
        for tag in sorted(support):
            reference = float(mapping[tag]['etabs_FZ_kN'])
            saved = rows[tag]
            point = str(mapping[tag]['etabs_unique'])
            native_fz = float(original_reactions[point]['etabs_FZ_kN'])
            if (point in native_points or not point or not all(map(math.isfinite, (reference, solved[tag])))
                    or not math.isclose(native_fz, reference, rel_tol=0, abs_tol=1e-8)
                    or str(saved['etabs_unique_name']) != point
                    or not math.isclose(float(saved['opensees_FZ_kN']), solved[tag], rel_tol=0, abs_tol=1e-8)
                    or not math.isclose(float(saved['etabs_FZ_kN']), reference, rel_tol=0, abs_tol=1e-8)):
                return None
            native_points.add(point)
            etabs_total += reference
            discrepancies.append(dict(etabs_point=point, opensees_node=tag,
                etabs_global_rz_kN=reference, abs_delta_kN=abs(solved[tag]-reference)))
        discrepancies.sort(key=lambda row: row['abs_delta_kN'], reverse=True)
        return dict(etabs_base_FZ_kN=etabs_total, opensees_support_FZ_kN=sum(solved.values()),
            node_comparison={'valid_one_to_one_global_z_count': len(support)},
            top_node_discrepancies=discrepancies, evidence_path=report_path)
    except (OSError, ValueError, TypeError, KeyError):
        return None


def export_primary_32_comparison(gravity_result, audit_json, output_dir):
    """Compare solved 32-node reaction values with original ETABS source FZ.

    [REF docs/review/GRAVITY_REACTION_FILTER_DIAGNOSTIC.md]
    """
    import csv
    result = gravity_result if isinstance(gravity_result, dict) else json.loads(
        Path(gravity_result).read_text(encoding="utf-8-sig"))
    audit = audit_json if isinstance(audit_json, dict) else json.loads(
        Path(audit_json).read_text(encoding="utf-8-sig"))
    if result.get("ok") is not True or result.get("wall_support_strategy") != MODE:
        raise ValueError("A completed, correctly labelled primary diagnostic result is required")
    if sorted(map(int,result.get("support_node_tags",[]))) != sorted(PROJECT_PRIMARY_32):
        raise ValueError("Solved support list is not exactly the confirmed 32 tags")
    reaction_rows = result.get("reactions",[])
    reactions = {}
    for row in reaction_rows:
        tag=int(row["node_tag"])
        if tag in reactions: raise ValueError("Duplicate solver reaction at "+str(tag))
        value=float(row["rz_kN"])
        if not math.isfinite(value):raise ValueError("Nonfinite support reaction at "+str(tag))
        reactions[tag]=value
    if set(reactions)!=set(PROJECT_PRIMARY_32):
        raise ValueError("Solver reaction output does not contain exactly the 32 expected supports")
    etabs={}
    for source in audit["mapping"]:
        if source["selected"]:
            tag=int(source["opensees_node"])
            if tag in etabs:
                raise ValueError("Duplicate selected ETABS source mapping at "+str(tag))
            etabs[tag]=source
    if set(etabs)!=set(PROJECT_PRIMARY_32):
        raise ValueError("Source ETABS point mapping does not cover exactly 32 supports")
    rows=[]
    for tag in PROJECT_PRIMARY_32:
        m=etabs[tag]
        original=float(m["etabs_FZ_kN"])
        if not math.isfinite(original):
            raise ValueError("Nonfinite original ETABS reaction at "+str(tag))
        got=reactions[tag]
        delta=got-original
        if not math.isfinite(delta):
            raise ValueError("Nonfinite ETABS–OpenSees reaction difference at "+str(tag))
        rows.append(dict(opensees_node=tag,etabs_unique_name=m["etabs_unique"],
                         etabs_FZ_kN=original,opensees_FZ_kN=got,
                         delta_kN=delta,
                         percent_delta=(100*delta/original if abs(original)>1e-9 else None),
                         abs_delta_kN=abs(delta)))
    rows.sort(key=lambda row:row["abs_delta_kN"],reverse=True)
    etabs_total=sum(r["etabs_FZ_kN"] for r in rows)
    open_total=sum(r["opensees_FZ_kN"] for r in rows)
    solver_total=float(result["report"]["support_vertical_reaction_kN"])
    if not all(math.isfinite(value) for value in (etabs_total,open_total,solver_total)):
        raise ValueError("Nonfinite total ETABS/OpenSees support reaction")
    if abs(open_total-solver_total)>max(0.01,abs(solver_total)*1e-7):
        raise ValueError("Saved 32-node reactions do not sum to solver support total")
    global_diff=open_total-etabs_total
    # Same pointwise numerical screen as the native direct comparison.
    # This is diagnostic, never a structural acceptance tolerance.
    max_abs=rows[0]["abs_delta_kN"]
    sum_abs=sum(row["abs_delta_kN"] for row in rows)
    rms=math.sqrt(sum(row["delta_kN"]**2 for row in rows)/len(rows))
    global_ok=abs(global_diff)<=max(1.0,abs(etabs_total)*0.005)
    pointwise_ok=max_abs<=1.0
    # Report diagnostics without converting a numerical match to structural acceptance.
    summary=dict(
        mode=MODE,classification="PRIMARY_PROJECT_GRAVITY_CASE",
        original_ETABS_case=PROFILE,expected_support_count=32,
        matched_support_count=len(rows),
        etabs_total_FZ_kN=etabs_total,opensees_total_FZ_kN=open_total,
        global_difference_kN=global_diff,
        global_difference_percent=(100*global_diff/etabs_total if etabs_total else None),
        worst_abs_node_difference_kN=rows[0]["abs_delta_kN"],
        worst_node=rows[0]["opensees_node"],
        original_etabs_table_sha256=audit["source_sha256"],
        global_screening_status="WITHIN_SCREEN_ONLY" if global_ok else "MISMATCH",
        pointwise_screening_status=("POINTWISE_NUMERICAL_SCREEN_ONLY_NOT_ENGINEERING_ACCEPTANCE"
                                    if pointwise_ok else "POINTWISE_RESIDUAL_EXCEEDS_NUMERICAL_SCREEN"),
        pointwise_numerical_screen_threshold_kN=1.0,
        sum_absolute_nodal_difference_kN=sum_abs,
        rms_nodal_difference_kN=rms,
        numerical_agreement="SCREENING_ONLY" if global_ok and pointwise_ok else "MISMATCH",
        structural_validation="NOT_ESTABLISHED",
        warning="Converged reaction agreement does not verify ETABS internal mesh restraint mapping, "
                "wall stiffness, beam end-zone weight or equivalent load path.",
        node_reactions=rows)
    out=Path(output_dir)
    if out.is_symlink() or out.parent.is_symlink():
        raise ValueError("Refusing linked primary-32 evidence output directory")
    targets={
        "json":out/"Primary_32_ETABS_OpenSees_Reactions.json",
        "csv":out/"Primary_32_ETABS_OpenSees_Reactions.csv",
        "xlsx":out/"Primary_32_ETABS_OpenSees_Reactions.xlsx",
    }
    if any(target.is_symlink() for target in targets.values()):
        raise ValueError("Refusing linked primary-32 evidence output file")
    # Shared staged writers guarantee that invalid engineering values never
    # replace an existing JSON/CSV result with a partially written document.
    from components.inputs.output_contract import atomic_json, write_table
    # Validate the entire report before writing any output.
    json.dumps(summary,allow_nan=False)
    columns=("opensees_node","etabs_unique_name","etabs_FZ_kN",
             "opensees_FZ_kN","delta_kN","percent_delta","abs_delta_kN")
    out.mkdir(parents=True,exist_ok=True)
    atomic_json(targets["json"],summary)
    write_table(targets["csv"],rows,columns=columns)
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill
    wb=Workbook();sheet=wb.active;sheet.title="32 support comparison"
    sheet.append(list(columns))
    for row in rows:sheet.append([row[k] for k in columns])
    sheet.freeze_panes="A2";sheet.auto_filter.ref=sheet.dimensions
    for c in sheet[1]:
        c.font=Font(color="FFFFFF",bold=True)
        c.fill=PatternFill("solid",fgColor="183B56")
    for col,width in {"A":20,"B":22,"C":24,"D":24,"E":20,"F":18,"G":20}.items():
        sheet.column_dimensions[col].width=width
    info=wb.create_sheet("Total and limitations")
    for key,value in summary.items():
        if key!="node_reactions" and not isinstance(value,(dict,list)):
            info.append([key,value])
    info.column_dimensions["A"].width=38
    info.column_dimensions["B"].width=95
    import os
    import tempfile
    fd,name=tempfile.mkstemp(prefix=".primary32_",suffix=".xlsx",dir=out)
    os.close(fd)
    stage=Path(name)
    try:
        wb.save(stage)
        os.replace(stage,targets["xlsx"])
    finally:
        stage.unlink(missing_ok=True)
    return summary

