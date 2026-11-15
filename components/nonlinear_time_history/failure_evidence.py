"""Bounded post-failure evidence capture; responses may be contaminated."""
from __future__ import annotations

import json
import math
from pathlib import Path

from components.inputs.output_contract import atomic_json


def _solver_time_evidence(value):
    """Record a nonfinite solver clock without emitting illegal JSON numbers."""
    clock=float(value)
    if math.isfinite(clock):
        return clock, "FINITE"
    return None, "NONFINITE_" + ("NAN" if math.isnan(clock) else "INFINITY")


def _validate_capture_limits(maximum_findings, max_values=None):
    if type(maximum_findings) is not int or maximum_findings < 1 or maximum_findings > 100000:
        raise ValueError("maximum_findings must be an integer from 1 to 100000")
    if max_values is not None and (
            type(max_values) is not int or max_values < 1 or max_values > 10000):
        raise ValueError("max_values must be an integer from 1 to 10000")


def _focus_tags(raw):
    """Do not coerce fractional/boolean element identities into other tags."""
    if raw is None:
        raise ValueError("Focused diagnostic requires explicitly selected element tags")
    tags=set()
    for value in raw:
        if type(value) is int and value>0:
            tag=value
        elif isinstance(value,str) and value.isdecimal() and int(value)>0:
            tag=int(value)
        else:
            raise ValueError("Focused element tag must be a positive integer")
        tags.add(tag)
        if len(tags)>16:
            raise ValueError("At most 16 focused element tags")
    if not tags:
        raise ValueError("Focused diagnostic requires at least one element tag")
    return sorted(tags)


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
    _validate_capture_limits(1,max_values)
    tags=_focus_tags(suspect_tags)
    existing=set(map(int,ops.getEleTags()))
    clock,time_status=_solver_time_evidence(ops.getTime())
    report={"status":stage,"time_s":clock,"time_status":time_status,
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
    atomic_json(output_path,report)
    return report


def snapshot_failed_step(
    ops, output_path, *, algorithm, dt, return_code,
    element_map_path=None, maximum_findings=150, suspect_tags=None,
):
    """Write observed non-finite responses without treating missing responses as zero."""
    _validate_capture_limits(maximum_findings)
    out = Path(output_path)
    inverse = {}
    mapping_error = None
    if element_map_path:
        try:
            candidate=Path(element_map_path)
            if candidate.is_symlink():
                raise ValueError("Linked element source mapping refused")
            if not candidate.is_file():
                raise FileNotFoundError("Source element mapping not found")
            mapping=json.loads(candidate.read_text(encoding="utf-8-sig"))
            if not isinstance(mapping,dict):
                raise ValueError("Element source mapping must be a JSON object")
            for source,tags in mapping.items():
                if not isinstance(source,str) or not isinstance(tags,list):
                    raise ValueError("Invalid element source mapping record")
                for raw in tags:
                    tag=int(raw)
                    if tag<=0:
                        raise ValueError("Nonpositive element tag in source mapping")
                    if tag in inverse and inverse[tag]!=source:
                        raise ValueError("Conflicting source mapping for element "+str(tag))
                    inverse[tag]=source
        except (OSError,ValueError,TypeError,OverflowError) as exc:
            mapping_error=str(exc)
            inverse={}
    clock,time_status=_solver_time_evidence(ops.getTime())
    attempt=float(dt)
    if not math.isfinite(attempt) or attempt<=0:
        raise ValueError("Failed-step evidence requires a positive finite attempted time step")
    report = {
        "status": "FAILED_STEP_DIAGNOSTIC",
        "analysis_time_s": clock,
        "analysis_time_status":time_status,
        "attempt_dt_s": attempt,
        "return_code": int(return_code),
        "algorithm": str(algorithm),
        "element_map": str(element_map_path) if element_map_path else None,
        "element_map_status":("NOT_SUPPLIED" if not element_map_path else
                               "INVALID_SOURCE_MAPPING" if mapping_error else
                               "SOURCE_MAPPING_PARSED_NOT_PHYSICALLY_VERIFIED"),
        "element_map_error":mapping_error,
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

    focus=set(_focus_tags(suspect_tags)) if suspect_tags is not None else None
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

    atomic_json(out,report)
    return report
