"""Offline ETABS reaction-based base node selection for a diagnostic gravity case.

Does not infer actual CSI PointObj.GetRestraint from zero FZ. This is a
deliberate sensitivity scenario, not a replica of native support conditions.
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
    original_fixed = {str(k): list(v) for k,v in original_supports.items()
                      if len(v) == 6 and bool(v[2])}
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
                 project_primary_status="SELECTED_AS_MAIN_DIAGNOSTIC_NOT_NATIVE_RESTRAINT_VERIFIED",
                 source_table=str(Path(etabs_table).resolve()),
                 source_sha256=hashlib.sha256(Path(etabs_table).read_bytes()).hexdigest(),
                 warning="DIAGNOSTIC ONLY: ETABS FZ=0 does not demonstrate free UZ or six free DOFs. "
                         "Retain 76- and 97-support runs. Review native source restraints "
                         "and internal wall-edge mesh constraints for acceptance.")
    return selected,audit
