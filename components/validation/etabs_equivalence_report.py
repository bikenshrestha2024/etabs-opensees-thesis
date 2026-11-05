"""Evidence-gated ETABS ↔ OpenSees quantitative comparison and Excel charts.

Discrepancy targets are user-selectable research screening tolerances, NEVER
automatic NBC 105:2025 acceptance criteria. CQC modal envelopes, story-maximum
edge drifts and joint-master displacement are different physical quantities
unless the reviewer establishes same analysis, spatial location, combination
and amplification basis. No reference value is silently treated as zero.
"""
from __future__ import annotations
import math
from pathlib import Path

DEFAULT_PERCENT_LIMITS = {
    "period":2.0,"cumulative_mass":1.0,"individual_mass":1.0,"base_shear":5.0,
    "story_shear":5.0,"displacement":5.0,"drift_ratio":5.0,
}
DEFAULT_ABS_ZERO = {"period":1e-5,"base_shear":0.01,
                    "story_shear":0.01,"displacement":1e-5,
                    "drift_ratio":1e-6,"cumulative_mass":0.01,"individual_mass":0.01}


def evaluate(open_rows, ref_rows, fields, policy=None):
    """Return comparison rows; EXACT match across eight semantic key fields.

    Every reference case must have a distinct combination and unit/basis.
    Evidence gate: policy.assumptions_verified may only be explicitly signed
    after model mass, stiffness, gravity, spectrum/damping, CQC, scales,
    eccentricity and same response location are independently reviewed.
    """
    policy=policy or {}
    checked=bool(policy.get("assumptions_verified",False))
    limits=dict(DEFAULT_PERCENT_LIMITS)
    limits.update(policy.get("percent_limits",{}))
    zero=dict(DEFAULT_ABS_ZERO)
    zero.update(policy.get("absolute_zero_limits",{}))
    for val in list(limits.values())+list(zero.values()):
        if not math.isfinite(float(val)) or float(val)<0:
            raise ValueError("Comparison tolerances must be finite and nonnegative.")
    idx={}
    for r in ref_rows:
        key=tuple(str(r.get(k,"")) for k in fields)
        if key in idx:raise ValueError("Duplicate ETABS normalized key: "+repr(key))
        v=float(r["value"])
        if not math.isfinite(v):raise ValueError("Nonfinite reference "+repr(key))
        idx[key]=v
    appeared=set()
    referenced=set()
    result=[]
    for source in open_rows:
        r=dict(source)
        key=tuple(str(r.get(k,"")) for k in fields)
        if key in appeared:raise ValueError("Duplicate OpenSees normalized key: "+repr(key))
        appeared.add(key)
        v=idx.get(key)
        match_key="|".join(key)
        exact=v is not None
        # A unit or result-basis mismatch cannot be turned into an implicit
        # conversion. Keep it visible; don't claim those values are equal.
        near=[k for k in idx if k[:6]==key[:6] and k!=key]
        # A reference with the same physical quantity but different units or
        # response basis was PRESENT, not missing. Do not count it again as
        # MISSING_OPENSEES in the final unmatched-reference pass.
        referenced.update(near)
        if not exact:
            status="NOT_COMPARABLE" if near else "MISSING_ETABS"
            note="Unit/basis or case mismatch: "+", ".join(str(k[6:]) for k in near) if near else "No exact ETABS method/state/case/axis/story/metric/unit/basis key"
            error=delta=None
        else:
            appeared.add(key)
            delta=float(r["value"])-v
            error=None if v==0 else 100*abs(delta)/abs(v)
            if not checked:
                status="NOT_COMPARABLE"
                note="Matching key only; independent model and spectrum basis not approved"
            elif v==0:
                limit=zero.get(r["metric"])
                status="NOT_COMPARABLE" if limit is None else ("PASS" if abs(delta)<=float(limit) else "FAIL")
                note="Zero reference: compare absolute difference in "+r["unit"]+"; no percent error"
            else:
                limit=limits.get(r["metric"])
                status="NOT_COMPARABLE" if limit is None else ("PASS" if error<=float(limit) else "FAIL")
                note="Research screening tolerance "+str(limit)+" percent; not NBC acceptance"
        r.update(etabs_value=v,difference=delta,percent_difference=error,
                 status=status,note=note,matching_key=match_key)
        result.append(r)
    for k,v in idx.items():
        if k not in appeared and k not in referenced:
            result.append({**dict(zip(fields,k)),"value":None,"etabs_value":v,
                "difference":None,"percent_difference":None,
                "status":"MISSING_OPENSEES","note":"ETABS quantity has no normalized OpenSees result",
                "matching_key":"|".join(k)})
    return result


def export_excel(outdir, rows, etabs_rows, compared, policy):
    """Create read-only-to-sources Excel comparison with charts and provenance."""
    from openpyxl import Workbook
    from openpyxl.chart import ScatterChart, Reference, Series
    from openpyxl.styles import Font, PatternFill, Alignment
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    wb=Workbook();overview=wb.active;overview.title="Summary"
    navy="17324A";green="DDF2E7";red="FCE8E6"
    def sheet(name, data, headers):
        ws=wb.create_sheet(name);ws.append(headers)
        for record in data:ws.append([record.get(k) for k in headers])
        ws.freeze_panes="A2";ws.auto_filter.ref=ws.dimensions
        for cell in ws[1]:
            cell.font=Font(color="FFFFFF",bold=True)
            cell.fill=PatternFill("solid",fgColor=navy)
        for i,key in enumerate(headers,1):
            ws.column_dimensions[__import__("openpyxl").utils.get_column_letter(i)].width=min(54,max(14,len(key)+5))
        return ws
    counts={k:sum(r["status"]==k for r in compared) for k in
            ("PASS","FAIL","NOT_COMPARABLE","MISSING_ETABS","MISSING_OPENSEES")}
    for row in [
        ["ETABS–OpenSees equivalence", "Software screening; NOT a Nepal code design approval"],
        ["Model/spectrum comparability approved",bool(policy.get("assumptions_verified",False))],
        ["Source selection","Exact .EDB and explicitly mapped ETABS analysis cases"],
        ["Response basis","Modal CQC envelopes are not signed simultaneous response"],
        ["PASS",counts["PASS"]],["FAIL",counts["FAIL"]],
        ["NOT COMPARABLE",counts["NOT_COMPARABLE"]],
        ["MISSING ETABS",counts["MISSING_ETABS"]],
        ["MISSING OPENSEES",counts["MISSING_OPENSEES"]],
        ["Screening thresholds",str(policy.get("percent_limits",DEFAULT_PERCENT_LIMITS))],
        ["Zero reference thresholds",str(policy.get("absolute_zero_limits",DEFAULT_ABS_ZERO))],
    ]:overview.append(row)
    overview.column_dimensions["A"].width=41;overview.column_dimensions["B"].width=91
    overview["A1"].font=Font(bold=True,color="FFFFFF");overview["A1"].fill=PatternFill("solid",fgColor=navy)
    headers=["method","limit_state","case","axis","location","metric","unit","basis","value","source_file"]
    sheet("OpenSees Results",rows,headers)
    sheet("ETABS API Results",etabs_rows,headers+["etabs_source_case","etabs_step_type","etabs_step_number"])
    cmp_fields=headers[:8]+["value","etabs_value","difference","percent_difference","status","note"]
    ws=sheet("Comparison",compared,cmp_fields)
    for n,row in enumerate(compared,2):
        if row["status"] in ("FAIL","MISSING_ETABS","MISSING_OPENSEES"):
            for cell in ws[n]:cell.fill=PatternFill("solid",fgColor=red)
        elif row["status"]=="PASS":
            for cell in ws[n]:cell.fill=PatternFill("solid",fgColor=green)
    # A source-matched plot for each case/direction/metric with numeric story IDs.
    graphs=wb.create_sheet("Profiles and Charts")
    groups={}
    for r in compared:
        if r["metric"] not in ("displacement","drift_ratio","story_shear"):continue
        try:loc=int(r["location"])
        except (ValueError,TypeError):continue
        key=(r["method"],r["limit_state"],r["case"],r["axis"],r["metric"],r["unit"],r["basis"])
        groups.setdefault(key,[]).append((loc,r))
    row0=1;num_charts=0
    for key,points in sorted(groups.items()):
        if len(points)<2 or num_charts>=16:continue
        points.sort()
        graphs.cell(row0,1," / ".join(map(str,key)))
        graphs.cell(row0+1,1,"Storey")
        graphs.cell(row0+1,2,"OpenSees")
        graphs.cell(row0+1,3,"ETABS")
        for j,(st,r) in enumerate(points,row0+2):
            graphs.cell(j,1,st)
            if r.get("value") is not None:graphs.cell(j,2,float(r["value"]))
            if r.get("etabs_value") is not None:graphs.cell(j,3,float(r["etabs_value"]))
        chart=ScatterChart();chart.title=" ".join(map(str,key[:5]))
        chart.x_axis.title="Storey";chart.y_axis.title=str(key[5])
        x=Reference(graphs,min_col=1,min_row=row0+2,max_row=row0+1+len(points))
        for col,label in ((2,"OpenSees"),(3,"ETABS")):
            y=Reference(graphs,min_col=col,min_row=row0+2,max_row=row0+1+len(points))
            chart.series.append(Series(y,x,title=label))
        chart.width=16;chart.height=9
        graphs.add_chart(chart,"E"+str(row0))
        row0+=max(23,len(points)+4);num_charts+=1
    graphs.column_dimensions["A"].width=45
    graphs.column_dimensions["B"].width=20
    graphs.column_dimensions["C"].width=20
    target=outdir/"ETABS_OpenSees_Equivalence.xlsx"
    wb.save(target)
    return target
