"""[REF docs/source/components/validation/etabs_lot_consistency.py.md]
Cross-lot consistency diagnostics for ETABS analysis-export workbooks.

Reference evidence only: every function reads already-ingested table rows and
returns a report. Nothing here edits a model, a workbook or an OpenSees input,
and no result is engineering acceptance (ETABS_OPENSEES_MATCHED stays NOT_VERIFIED).

Units follow the export: kN, kN-m, kg, mm for joint coordinates in the object
tables. Findings were derived from the real six-lot export of the 25-storey
model (see docs/validation/20261128_ETABS_LOT_CONSISTENCY_AUDIT.md).
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from contextlib import closing
import json
import sqlite3
from pathlib import Path

from components.nbc105.constants import GRAVITY_M_S2, SUPERSEDED_GRAVITY_M_S2

SCHEMA = "ETABS_LOT_CONSISTENCY_V1"
STATUS = "REFERENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE"
# Soil-C research set fixed in AGENTS.md (6 near-field + 2 far-field).
CONTRACT_EVENTS = ("Gorkha", "Landers", "Northridge", "Kobe", "Kocaeli",
                   "Chi Chi", "Hector Mine", "Loma Prieta")
_FORCE = ("FX", "FY", "FZ", "MX", "MY", "MZ")


def _f(value):
    """Finite float or ValueError; blanks and text are never silently zero."""
    if isinstance(value, bool) or value is None or value == "":
        raise ValueError(f"Missing numeric value: {value!r}")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Nonfinite numeric value: {value!r}")
    return result


def derive_primary_support_tags(joints, reactions, *, expected_tags=None, tolerance_kN=1e-6):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Reproduce the 32 physical-support tags from export data alone.

    Rule (an observed ordering, not an ETABS API fact): number the Base-story
    joints 1..N by ascending (global X, global Y); the joints with a nonzero
    vertical reaction in the supplied full-gravity combination are the
    supports. The remaining Base joints must carry exactly zero in all six
    components (the 44 shear-wall mesh points are not supports).
    ``reactions`` must already be the rows of ONE output case.
    """
    base = []
    for row in joints:
        if str(row["Story"]).strip() != "Base":
            continue
        base.append((_f(row["Global X"]), _f(row["Global Y"]), str(row["Element Name"]).strip()))
    ordered = sorted(base)
    if len({(x, y) for x, y, _ in ordered}) != len(ordered):
        raise ValueError("Base joints share a coordinate; ordering rule is ambiguous")
    tag = {name: i for i, (_, _, name) in enumerate(ordered, 1)}
    seen = {}
    for row in reactions:
        name = str(row["Unique Name"]).strip()
        if name in seen:
            raise ValueError("Duplicate joint reaction row: " + name)
        seen[name] = [_f(row[c]) for c in _FORCE]
    if set(seen) != set(tag):
        raise ValueError("Reaction joints differ from Base joints")
    nonzero = sorted(tag[n] for n, v in seen.items() if abs(v[2]) > tolerance_kN)
    zero_rows = {n: v for n, v in seen.items() if abs(v[2]) <= tolerance_kN}
    leaking = sorted(tag[n] for n, v in zero_rows.items() if any(abs(c) > tolerance_kN for c in v))
    names = {t: n for n, t in tag.items()}
    result = {
        "base_joint_count": len(tag), "support_count": len(nonzero),
        "zero_reaction_count": len(zero_rows),
        "zero_reaction_rows_with_nonzero_other_component": leaking,
        "derived_support_tags": nonzero,
        "support_etabs_unique_names": [names[t] for t in nonzero],
        "ordering_rule": "BASE_JOINTS_SORTED_BY_GLOBAL_X_THEN_Y_RANK",
        "physical_support_mapping": "NOT_VERIFIED",
    }
    if expected_tags is not None:
        want = sorted(int(t) for t in expected_tags)
        result["expected_tags"] = want
        result["status"] = ("DERIVED_TAGS_MATCH_EXPECTED" if want == nonzero and not leaking
                            else "DERIVED_TAGS_DIFFER_FROM_EXPECTED")
        result["missing_from_derived"] = sorted(set(want) - set(nonzero))
        result["unexpected_in_derived"] = sorted(set(nonzero) - set(want))
    return result


def seismic_mass_source_identity(masses, joints, *, dead_fz_kN, live_fz_kN,
                                 roof_live_fz_kN=0.0, candidate_g=None):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Identify the ETABS mass source and the g it used to convert weight to mass.

    Compares sum(UZ)*g with Dead + f*Live for each candidate g and reports the
    implied live participation f. Seismic weight is the non-Base horizontal
    mass times g (restrained Base-story mass carries no dynamic weight).
    """
    candidate_g = tuple(candidate_g or (SUPERSEDED_GRAVITY_M_S2, GRAVITY_M_S2))
    story = {str(r["Element Name"]).strip(): str(r["Story"]).strip() for r in joints}
    total_uz = total_ux_dyn = total_ux_base = 0.0
    seen = set()
    for row in masses:
        name = str(row["Point Element"]).strip()
        if name in seen:
            raise ValueError("Duplicate assembled-mass joint: " + name)
        seen.add(name)
        if name not in story:
            raise ValueError("Assembled mass joint absent from joint table: " + name)
        total_uz += _f(row["UZ"])
        if story[name] == "Base":
            total_ux_base += _f(row["UX"])
        else:
            total_ux_dyn += _f(row["UX"])
    live_total = live_fz_kN + roof_live_fz_kN
    rows = []
    for g in candidate_g:
        weight = total_uz * g / 1000.0
        implied = (weight - dead_fz_kN) / live_total if live_total else float("nan")
        rows.append({"g_m_s2": g, "vertical_mass_weight_kN": weight,
                     "residual_to_dead_plus_0p3_live_kN": weight - (dead_fz_kN + 0.3 * live_fz_kN),
                     "implied_live_fraction": implied,
                     "seismic_weight_nonbase_horizontal_kN": total_ux_dyn * g / 1000.0})
    best = min(rows, key=lambda r: abs(r["residual_to_dead_plus_0p3_live_kN"]))
    other = [r for r in rows if r is not best]
    return {
        "mass_joint_rows": len(seen), "joints_without_mass": len(set(story) - seen),
        "sum_UZ_kg": total_uz, "sum_UX_nonbase_kg": total_ux_dyn, "sum_UX_base_kg": total_ux_base,
        "candidates": rows, "best_g_m_s2": best["g_m_s2"],
        "best_residual_kN": best["residual_to_dead_plus_0p3_live_kN"],
        "implied_live_fraction_at_best_g": best["implied_live_fraction"],
        "g_discrimination_kN": (abs(other[0]["residual_to_dead_plus_0p3_live_kN"]) if other else None),
        "project_g_m_s2": GRAVITY_M_S2,
        "mass_ratio_if_weight_divided_by_project_g": (best["g_m_s2"] / GRAVITY_M_S2),
        "status": "ETABS_MASS_SOURCE_IDENTIFIED_NOT_NBC_ACCEPTANCE",
    }


def time_history_step_availability(table_rows):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Report whether NonModHist rows carry a step series or only Max/Min envelopes."""
    steps = Counter()
    cases = set()
    for row in table_rows:
        if row.get("Case Type") == "NonModHist":
            steps[str(row.get("Step Type") or "")] += 1
            cases.add(row["Output Case"])
    if not steps:
        status = "NO_NONMODAL_HISTORY_ROWS"
    elif set(steps) <= {"Max", "Min"}:
        status = "ENVELOPE_ONLY_NO_STEP_SERIES"
    else:
        status = "STEP_SERIES_PRESENT"
    return {"cases": len(cases), "step_types": dict(steps), "status": status}


def classify_time_history_cases(case_names, *, contract_events=CONTRACT_EVENTS):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Pair ``Time History X`` with ``Time History X-1`` and compare with the contract set."""
    names = set(case_names)
    events = defaultdict(set)
    for name in names:
        match = re.fullmatch(r"Time History (.+?)(-1)?", name)
        if match:
            events[match[1]].add("YX_OR_SECOND" if match[2] else "FIRST")
    paired = sorted(e for e, v in events.items() if v == {"FIRST", "YX_OR_SECOND"})
    unpaired = sorted(e for e, v in events.items() if len(v) == 1)
    contract = set(contract_events)
    irregular = sorted(n for n in names if re.fullmatch(r"EQ[XY][+-] P[- ]Delta", n))
    hyphen = {n for n in irregular if "P-Delta" in n}
    return {
        "events_in_export": sorted(events), "paired_events": paired, "unpaired_events": unpaired,
        "contract_events": sorted(contract),
        "contract_events_missing": sorted(contract - set(paired)),
        "events_not_in_contract": sorted(set(events) - contract),
        "total_time_history_cases": sum(len(v) for v in events.values()),
        "p_delta_case_names_mixed_hyphenation": bool(hyphen) and hyphen != set(irregular),
        "p_delta_case_names": irregular,
        "status": ("CONTRACT_EVENTS_COMPLETE_EXTRA_EVENTS_PRESENT"
                   if not (contract - set(paired)) and set(events) - contract
                   else "CONTRACT_EVENTS_COMPLETE" if not (contract - set(paired))
                   else "CONTRACT_EVENTS_INCOMPLETE"),
    }


def modal_participation_diagnostics(period_rows, ratio_rows, *, target=0.90):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Flag torsional-participation gaps and export period quantisation."""
    periods = [(_f(r["Period"]), _f(r["CircFreq"])) for r in period_rows]
    quantisation = max((abs(t - 2 * math.pi / w) / (2 * math.pi / w) for t, w in periods), default=0.0)
    totals = {k: 0.0 for k in ("UX", "UY", "UZ", "RX", "RY", "RZ")}
    first = {}
    cumulative = {k: 0.0 for k in totals}
    for index, row in enumerate(ratio_rows, 1):
        for key in totals:
            value = _f(row[key])
            totals[key] += value
            cumulative[key] += value
            if key not in first and cumulative[key] >= target:
                first[key] = index
    return {
        "modes": len(periods), "mass_ratio_sums": totals,
        "first_mode_reaching_target": first, "target": target,
        "no_torsional_participation": totals["RZ"] < 1e-9,
        "max_relative_period_vs_circular_frequency_error": quantisation,
        "use_circular_frequency_not_rounded_period": quantisation > 1e-3,
        "status": "REFERENCE_ONLY_NOT_NBC_ACCEPTANCE",
    }


def table_data_identity(rows_a, rows_b):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    True when two tables hold the same multiset of data rows (worksheet_row ignored)."""
    def bag(rows):
        return Counter(tuple(v for k, v in row.items() if k != "worksheet_row") for row in rows)
    a, b = bag(rows_a), bag(rows_b)
    return {"rows_a": sum(a.values()), "rows_b": sum(b.values()), "identical": a == b}


def classify_lot_overlap(audit):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Find a combined lot that is exactly the union of its split parts.

    ``audit`` is the result of ``audit_analysis_workbooks``. Content hashes are
    compared per worksheet; a file whose every worksheet is reproduced
    byte-for-byte by two or more other files is reported as a combined
    duplicate. Such files must never be loaded together.
    """
    owners = defaultdict(list)
    sheets = {}
    for index, entry in enumerate(audit["files"]):
        sheets[index] = {s["sheet"]: s.get("content_sha256") for s in entry["worksheets"]}
        for name, digest in sheets[index].items():
            owners[(name, digest)].append(index)
    combined = []
    for index, own in sheets.items():
        if not own or any(None is d for d in own.values()):
            continue
        parts = sorted({o for name, d in own.items() for o in owners[(name, d)] if o != index})
        if len(parts) >= 2 and all(any(o != index for o in owners[(n, d)]) for n, d in own.items()):
            combined.append({
                "combined_lot": index + 1, "duplicated_by_lots": [p + 1 for p in parts],
                "sheets": sorted(own), "action": "LOAD_COMBINED_OR_PARTS_NEVER_BOTH"})
    return {"duplicate_groups": combined,
            "status": "COMBINED_LOT_DUPLICATES_PARTS" if combined else "NO_FULL_LOT_OVERLAP"}


class AnalysisReferenceRows:
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Read-only row access to the SQLite store written by ``read_analysis_reference``.

    ``report`` is its returned manifest (or the saved JSON); ``database`` the
    SQLite file named in ``report['row_storage']``. Mirrors
    ``CombinedReference.rows`` so either object feeds ``lot_consistency_report``.
    """

    def __init__(self, report, database):
        self.analysis = report
        self.database = Path(database)

    def rows(self, table, *, case=None):
        meta = self.analysis["tables"].get(table)
        if meta is None:
            raise ValueError("Reference table absent: " + str(table))
        if meta["case_column"] and case is not None and case not in meta["case_row_counts"]:
            raise ValueError("Output case absent: " + str(case))
        with closing(sqlite3.connect(self.database.as_uri() + "?mode=ro", uri=True)) as db:
            sql = "SELECT worksheet_row, values_json FROM reference_rows WHERE table_id=?"
            params = (meta["table_id"],)
            if case is not None:
                sql += " AND case_name=?"
                params += (case,)
            for number, values in db.execute(sql + " ORDER BY worksheet_row", params):
                yield dict(zip(meta["columns"], [number, *json.loads(values)]))


def lot_consistency_report(source, *, expected_support_tags=None, audit=None,
                           gravity_case="1. DL + LL"):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Run every consistency diagnostic on a verified reference ``source``."""
    tables = source.analysis["tables"]
    findings = []

    def add(ident, severity, text):
        findings.append({"id": ident, "severity": severity, "text": text})

    out = {"schema": SCHEMA, "status": STATUS, "engineering_acceptance": "NOT_VERIFIED",
           "source_model_identity": "UNVERIFIED", "findings": findings}
    joints = list(source.rows("Objects and Elements - Joints"))
    out["support_tags"] = derive_primary_support_tags(
        joints, source.rows("Joint Reactions", case=gravity_case), expected_tags=expected_support_tags)
    if out["support_tags"].get("status") == "DERIVED_TAGS_DIFFER_FROM_EXPECTED":
        add("SUPPORT_TAGS_DIFFER", "ERROR", "Derived support tags differ from the expected 32.")
    elif out["support_tags"]["zero_reaction_rows_with_nonzero_other_component"]:
        add("ZERO_FZ_ROWS_CARRY_OTHER_COMPONENTS", "ERROR",
            "Zero-FZ Base joints carry moments or shear; they are not inert mesh points.")

    def fz(case):
        return sum(_f(r["FZ"]) for r in source.rows("Joint Reactions", case=case))
    dead, live = fz("Dead"), fz("Live")
    roof = fz("Roof Live") if "Roof Live" in tables["Joint Reactions"]["case_row_counts"] else 0.0
    out["seismic_mass_source"] = seismic_mass_source_identity(
        source.rows("Assembled Joint Masses"), joints,
        dead_fz_kN=dead, live_fz_kN=live, roof_live_fz_kN=roof)
    best = out["seismic_mass_source"]
    if abs(best["best_g_m_s2"] - GRAVITY_M_S2) > 1e-9:
        add("EXPORT_G_DIFFERS_FROM_PROJECT_G", "WARNING",
            f"ETABS masses reproduce Dead+0.3Live only with g={best['best_g_m_s2']} m/s^2; the project "
            f"uses g={GRAVITY_M_S2}. Masses rebuilt as weight/{GRAVITY_M_S2} are "
            f"{1 - best['mass_ratio_if_weight_divided_by_project_g']:.4%} lighter than the ETABS masses. "
            "Reconstruct from ETABS kg, or declare the g choice per comparison.")

    steps = {}
    for name, meta in tables.items():
        if "Case Type" not in meta["columns"] or "Output Case" not in meta["columns"]:
            continue
        histories = [c for c in meta["case_row_counts"] if c.startswith("Time History ")]
        if histories:
            steps[name] = time_history_step_availability(source.rows(name, case=histories[0]))
    out["time_history_step_availability"] = {n: v["status"] for n, v in sorted(steps.items())}
    if steps and all(v["status"] == "ENVELOPE_ONLY_NO_STEP_SERIES" for v in steps.values()):
        add("TIME_HISTORY_ENVELOPE_ONLY", "WARNING",
            "No exported table carries a time-history step series; ETABS-OpenSees NLTHA comparison "
            "is limited to Max/Min envelopes until step-by-step tables are exported.")
    cases = set(tables["Joint Reactions"]["case_row_counts"])
    out["time_history_cases"] = classify_time_history_cases(cases)
    if out["time_history_cases"]["events_not_in_contract"]:
        add("TIME_HISTORY_EVENTS_BEYOND_CONTRACT", "WARNING",
            "Export holds events outside the 8-pair Soil-C set: "
            + ", ".join(out["time_history_cases"]["events_not_in_contract"]))
    if out["time_history_cases"]["p_delta_case_names_mixed_hyphenation"]:
        add("P_DELTA_CASE_NAME_HYPHENATION_MIXED", "INFO",
            "Cases mix 'P-Delta' and 'P Delta'; always match case names literally.")
    out["modal"] = modal_participation_diagnostics(
        source.rows("Modal Periods And Frequencies", case="Modal Ritz"),
        source.rows("Modal Participating Mass Ratios", case="Modal Ritz"))
    if out["modal"]["no_torsional_participation"]:
        add("NO_RZ_MODAL_PARTICIPATION", "WARNING",
            "All Ritz modes report zero RZ mass participation; torsion is absent from modal and "
            "response-spectrum results.")
    if out["modal"]["use_circular_frequency_not_rounded_period"]:
        add("PERIODS_ROUNDED_TO_MILLISECOND", "INFO",
            "Export periods are rounded to 0.001 s; use CircFreq/Eigenvalue for comparisons.")
    out["identical_tables"] = {}
    if all(n in tables for n in ("Joint Reactions", "Joint Design Reactions")):
        same = table_data_identity(source.rows("Joint Reactions"), source.rows("Joint Design Reactions"))
        out["identical_tables"]["Joint Reactions == Joint Design Reactions"] = same
        if same["identical"]:
            add("JOINT_DESIGN_REACTIONS_DUPLICATE", "INFO",
                "Joint Design Reactions repeats Joint Reactions row for row; do not count it as a second source.")
    if audit is not None:
        out["lot_overlap"] = classify_lot_overlap(audit)
        if out["lot_overlap"]["duplicate_groups"]:
            add("COMBINED_LOT_DUPLICATES_PARTS", "WARNING",
                "A combined lot repeats its split parts byte for byte; load one form only.")
    return out


def time_history_reference_envelopes(source, *, top_story=None):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Per-case ETABS NLTHA envelope targets: base shear, roof CM displacement, story drift.

    Envelope values only (Max/Min rows). They are comparison targets for an
    OpenSees run, not a step-history reference and not acceptance evidence.
    Displacements keep the export unit recorded in the table metadata.
    """
    tables = source.analysis["tables"]
    cases = sorted(c for c in tables["Base Reactions"]["case_row_counts"] if c.startswith("Time History "))
    if top_story is None:
        height = {}
        for row in source.rows("Diaphragm CM Displacements", case=cases[0]):
            height[str(row["Story"])] = _f(row["Z"])
        top_story = max(height, key=height.get)
    out = []
    for case in cases:
        base = list(source.rows("Base Reactions", case=case))
        roof = [r for r in source.rows("Diaphragm CM Displacements", case=case) if r["Story"] == top_story]
        drift = list(source.rows("Story Drifts", case=case))
        record = {"case": case}
        for axis in ("FX", "FY"):
            values = [_f(r[axis]) for r in base]
            record[axis + "_max_kN"], record[axis + "_min_kN"] = max(values), min(values)
        for axis in ("UX", "UY"):
            record["roof_" + axis + "_abs_max"] = max(abs(_f(r[axis])) for r in roof)
        for direction in ("X", "Y"):
            values = [abs(_f(r["Drift"])) for r in drift if r["Direction"] == direction]
            record["story_drift_ratio_" + direction + "_abs_max"] = max(values)
        out.append(record)
    return {"top_story": top_story,
            "roof_displacement_unit": tables["Diaphragm CM Displacements"].get("units", {}).get("UX"),
            "step_series": "ABSENT_ENVELOPE_ONLY", "cases": out,
            "status": "ETABS_ENVELOPE_TARGETS_NOT_ACCEPTANCE"}


_ADDITIVE_STEPS = ("", "Step By Step", "Mode")


def base_reaction_equilibrium(base_rows, reaction_rows, joints):
    """[REF docs/source/components/validation/etabs_lot_consistency.py.md]
    Six-component check of ETABS Base Reactions against summed joint reactions.

    Joint moments are moved to the Base Reactions reference point with
    M = M_j + r x F. Only additive step types (single/combination values,
    Step By Step, Mode) are compared; Max/Min envelope rows are not additive
    (a sum of per-joint maxima is not the maximum of the sum) and are counted
    but never pass or fail. Returns residuals in kN and kN-m.
    """
    position = {str(r["Element Name"]).strip(): (_f(r["Global X"]), _f(r["Global Y"]), _f(r["Global Z"]))
                for r in joints}
    key = lambda r: (r["Output Case"], r["Case Type"], r.get("Step Type") or "", r.get("Step Number"))
    sums = {}
    for row in reaction_rows:
        name = str(row["Unique Name"]).strip()
        if name not in position:
            raise ValueError("Reaction joint absent from joint table: " + name)
        x, y, z = position[name]
        fx, fy, fz, mx, my, mz = (_f(row[c]) for c in _FORCE)
        acc = sums.setdefault(key(row), [0.0] * 6)
        acc[0] += fx
        acc[1] += fy
        acc[2] += fz
        acc[3] += mx
        acc[4] += my
        acc[5] += mz
        # moments about the origin; shifted to the reference point afterwards
        acc[3] += y * fz - z * fy
        acc[4] += z * fx - x * fz
        acc[5] += x * fy - y * fx
    compared = envelope = 0
    worst = {"force_kN": 0.0, "moment_kNm": 0.0}
    worst_case = {}
    unmatched = []
    seen = set()
    for row in base_rows:
        k = key(row)
        seen.add(k)
        step = k[2]
        if step not in _ADDITIVE_STEPS:
            envelope += 1
            continue
        if k not in sums:
            unmatched.append(k)
            continue
        ref = (_f(row["X"]), _f(row["Y"]), _f(row["Z"]))
        fx, fy, fz, mx, my, mz = sums[k]
        # shift joint-sum moments (about origin) to the reported reference point
        mx -= ref[1] * fz - ref[2] * fy
        my -= ref[2] * fx - ref[0] * fz
        mz -= ref[0] * fy - ref[1] * fx
        force = max(abs(fx - _f(row["FX"])), abs(fy - _f(row["FY"])), abs(fz - _f(row["FZ"])))
        moment = max(abs(mx - _f(row["MX"])), abs(my - _f(row["MY"])), abs(mz - _f(row["MZ"])))
        compared += 1
        if force > worst["force_kN"]:
            worst["force_kN"], worst_case["force"] = force, k[0]
        if moment > worst["moment_kNm"]:
            worst["moment_kNm"], worst_case["moment"] = moment, k[0]
    return {"additive_rows_compared": compared, "envelope_rows_not_additive": envelope,
            "base_rows_without_joint_rows": len(unmatched),
            "joint_rows_without_base_row": len(set(sums) - seen),
            "max_force_residual_kN": worst["force_kN"], "max_moment_residual_kNm": worst["moment_kNm"],
            "worst_case": worst_case, "status": "REFERENCE_ONLY_NOT_NATIVE_SUPPORT_ACCEPTANCE"}
