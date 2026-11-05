"""Bounded post-failure evidence capture; responses may be contaminated."""
from __future__ import annotations

import json
import math
from pathlib import Path


def _numbers(raw):
    if raw is None:
        return []
    if isinstance(raw, (int, float)):
        return [float(raw)]
    try:
        return [float(value) for value in raw]
    except TypeError:
        return [float(raw)]


def snapshot_selected_state(ops, output_path, *, suspect_tags,
                            stage="LAST_ACCEPTED_COMMITTED", max_values=24):
    """Minimal element/node evidence for a committed (not failed) state.

    Only actual live solver tags are queried. Unsupported eleResponse
    channels are identified explicitly. This never updates the solver
    state, alters the material, or assumes that a nonfinite response is
    the initiating cause. Use immediately after gravity and each accepted
    diagnostic step; the last committed snapshot survives a failed attempt.
    """
    tags=sorted({int(tag) for tag in suspect_tags})
    if len(tags)>16 or any(t<=0 for t in tags):
        raise ValueError("suspect_tags must have 1..16 positive solver tags")
    existing=set(map(int,ops.getEleTags()))
    report={"status":stage,"time_s":float(ops.getTime()),
            "tag_count":len(tags),"elements":[],"missing_tags":[],
            "warning":"Committed response evidence is not material qualification."}
    for tag in tags:
        if tag not in existing:
            report["missing_tags"].append(tag)
            continue
        item={"tag":tag,"nodes":[],"responses":{}}
        try:
            elements_nodes=[int(x) for x in ops.eleNodes(tag)]
        except Exception as exc:
            item["node_query_error"]=str(exc)
            elements_nodes=[]
        for node in elements_nodes:
            entry={"tag":node}
            for name in ("nodeCoord","nodeDisp","nodeVel","nodeAccel"):
                try:
                    values=_numbers(getattr(ops,name)(node))
                    entry[name]={"status":"FINITE" if all(math.isfinite(v) for v in values) else "NONFINITE",
                                 "values":[str(v) for v in values[:max_values]]}
                except Exception as exc:
                    entry[name]={"status":"UNSUPPORTED_OR_ERROR","error":str(exc)}
            item["nodes"].append(entry)
        for name,args in (
            ("localForce",("localForce",)),
            ("basicDeformation",("basicDeformation",)),
            ("globalForce",("globalForce",)),
            ("ShearDef",("ShearDef",)),
            ("Curvature",("Curvature",)),
            ("RCPanel1_panel_stress",("RCPanel",1,"panel_stress")),
            ("RCPanel1_panel_strain",("RCPanel",1,"panel_strain"))):
            try:
                value=_numbers(ops.eleResponse(tag,*args))
                item["responses"][name]={
                    "status":("UNSUPPORTED_EMPTY" if not value else
                              "FINITE" if all(math.isfinite(v) for v in value) else "NONFINITE"),
                    "values":[str(v) for v in value[:max_values]]}
            except Exception as exc:
                item["responses"][name]={"status":"UNSUPPORTED_OR_ERROR","error":str(exc)}
        report["elements"].append(item)
    output=Path(output_path)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf-8")
    return report


def snapshot_failed_step(
    ops, output_path, *, algorithm, dt, return_code,
    element_map_path=None, maximum_findings=150, suspect_tags=None,
):
    """Write observed non-finite responses without treating missing responses as zero."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    inverse = {}
    if element_map_path and Path(element_map_path).is_file():
        mapping = json.loads(
            Path(element_map_path).read_text(encoding="utf-8-sig")
        )
        for source, tags in mapping.items():
            if isinstance(tags, list):
                for tag in tags:
                    inverse[int(tag)] = source

    report = {
        "status": "FAILED_STEP_DIAGNOSTIC",
        "analysis_time_s": float(ops.getTime()),
        "attempt_dt_s": float(dt),
        "return_code": int(return_code),
        "algorithm": str(algorithm),
        "element_map": str(element_map_path) if element_map_path else None,
        "warning": (
            "Post-failure responses may be rollback/contaminated states; "
            "the first observed non-finite element is not necessarily the cause."
        ),
        "nodes_scanned": 0,
        "elements_scanned": 0,
        "nonfinite_nodes": [],
        "nonfinite_elements": [],
        "unsupported_responses": {},
        "query_errors": [],
    }

    focus=set(map(int,suspect_tags)) if suspect_tags is not None else None
    if focus is not None and (len(focus)>16 or any(t<=0 for t in focus)):
        raise ValueError("suspect_tags must contain 1..16 positive element tags")
    report["focused_element_tags"]=sorted(focus) if focus is not None else None
    for tag in ([] if focus is not None else ops.getNodeTags()):
        report["nodes_scanned"] += 1
        try:
            values = _numbers(ops.nodeDisp(tag))
            if any(not math.isfinite(value) for value in values):
                report["nonfinite_nodes"].append(
                    {"tag": int(tag), "displacement": [str(v) for v in values]}
                )
        except Exception as exc:
            if len(report["query_errors"]) < maximum_findings:
                report["query_errors"].append({"node": int(tag), "error": str(exc)})

    for tag in (sorted(focus) if focus is not None else ops.getEleTags()):
        report["elements_scanned"] += 1
        source = inverse.get(int(tag))
        queries = [
            ("localForce", ("localForce",)),
            ("basicDeformation", ("basicDeformation",)),
            ("globalForce", ("globalForce",)),
        ]
        if source and source.startswith("AREA:"):
            queries.extend([
                ("ShearDef", ("ShearDef",)),
                ("Curvature", ("Curvature",)),
                ("RCPanel1_panel_stress", ("RCPanel", 1, "panel_stress")),
                ("RCPanel1_panel_strain", ("RCPanel", 1, "panel_strain")),
            ])
        for label, args in queries:
            try:
                values = _numbers(ops.eleResponse(int(tag), *args))
                if not values:
                    unsupported = report["unsupported_responses"]
                    unsupported[label] = unsupported.get(label, 0) + 1
                elif any(not math.isfinite(value) for value in values):
                    if len(report["nonfinite_elements"]) < maximum_findings:
                        report["nonfinite_elements"].append({
                            "tag": int(tag),
                            "source": source,
                            "response": label,
                            "values": [str(value) for value in values[:30]],
                        })
            except Exception as exc:
                if len(report["query_errors"]) < maximum_findings:
                    report["query_errors"].append({
                        "element": int(tag),
                        "response": label,
                        "error": str(exc),
                    })

    out.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    return report
