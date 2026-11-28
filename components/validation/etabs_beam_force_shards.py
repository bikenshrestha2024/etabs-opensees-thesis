"""Reference audit of ETABS ``Element Forces - Beams`` workbook shards.

[REF docs/source/components/validation/etabs_beam_force_shards.py.md]
Excel stops at 1,048,576 rows, so a long beam-force table is exported as several
workbooks. This module checks that the shards together hold every element, case,
step and station exactly once, that rows repeated between shards agree, and that
a shard cut at the Excel limit did not drop rows. It reads rows only; it never
changes a model or a workbook and is not engineering acceptance.
"""
from __future__ import annotations

import hashlib
from collections import Counter, defaultdict

SCHEMA = "ETABS_BEAM_FORCE_SHARDS_V1"
STATUS = "REFERENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE"
EXCEL_ROW_LIMIT = 1_048_576
SHEET_HEADER_ROWS = 3  # TABLE title, column names, units
_KEY = ("Unique Name", "Output Case", "Step Type", "Step Number", "Station")
_VALUES = ("P", "V2", "V3", "T", "M2", "M3")


def _digest(parts) -> int:
    return int.from_bytes(hashlib.blake2b("\x1f".join(parts).encode(), digest_size=8).digest(), "big")


def _text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def audit_beam_force_shards(shards, *, frame_elements=None, excel_row_limit=EXCEL_ROW_LIMIT):
    """[REF docs/source/components/validation/etabs_beam_force_shards.py.md]

    ``shards`` is an ordered list of ``(name, rows)``; ``rows`` iterates dicts keyed
    by the ETABS column names. ``frame_elements`` optionally maps an element name to
    its story (from ``Objects and Elements - Frames``). Row identity is
    element + case + step type + step number + station; a 64-bit hash of that key
    and of the six force values is kept, not the rows.
    """
    seen = {}                      # key hash -> value hash
    per_shard = []
    stations = defaultdict(set)    # element -> stations
    cell = Counter()               # (element, case-step) -> station rows
    case_steps = set()
    story_of = {}
    conflicts = Counter()
    cross_repeats = Counter()
    shard_elements = []
    nonfinite = 0
    for name, rows in shards:
        n = 0
        elements = set()
        within = Counter()
        keys_here = set()
        for row in rows:
            n += 1
            key_parts = [_text(row.get(c)) for c in _KEY]
            vals = []
            for c in _VALUES:
                try:
                    v = float(row.get(c))
                except (TypeError, ValueError):
                    v = float("nan")
                vals.append(v)
            if any(v != v or v in (float("inf"), float("-inf")) for v in vals):
                nonfinite += 1  # rows with a missing or nonfinite value, counted once
            kh = _digest(key_parts)
            vh = _digest([repr(v) for v in vals])
            elem = key_parts[0]
            elements.add(elem)
            if kh in keys_here:
                within[elem] += 1
                continue
            keys_here.add(kh)
            if kh in seen:
                cross_repeats[(elem)] += 1
                if seen[kh] != vh:
                    conflicts[elem] += 1
                continue
            seen[kh] = vh
            cs = tuple(key_parts[1:4])
            case_steps.add(cs)
            stations[elem].add(key_parts[4])
            cell[(elem, cs)] += 1
            story_of.setdefault(elem, _text(row.get("Story")))
        per_shard.append({
            "shard": name, "data_rows": n, "elements": len(elements),
            "duplicate_key_rows_inside_shard": sum(within.values()),
            "at_excel_row_limit": n + SHEET_HEADER_ROWS >= excel_row_limit})
        shard_elements.append(elements)
    incomplete = sorted({e for (e, cs), c in cell.items() if c != len(stations[e])}
                        | {e for e in stations
                           if sum(1 for cs in case_steps if (e, cs) in cell) != len(case_steps)})
    pair_overlap = {}
    for i in range(len(shard_elements)):
        for j in range(i + 1, len(shard_elements)):
            pair_overlap[f"{per_shard[i]['shard']}&{per_shard[j]['shard']}"] = len(shard_elements[i] & shard_elements[j])
    doc = {
        "schema": SCHEMA, "status": STATUS, "engineering_acceptance": "NOT_VERIFIED",
        "shards": per_shard,
        "union": {"unique_rows": len(seen), "elements": len(stations), "case_step_keys": len(case_steps),
                  "stations_per_element": dict(Counter(len(s) for s in stations.values())),
                  "elements_with_incomplete_case_station_grid": len(incomplete),
                  "incomplete_element_sample": incomplete[:10]},
        "shared_elements_between_shards": pair_overlap,
        "rows_repeated_in_later_shard": sum(cross_repeats.values()),
        "repeated_rows_with_different_values": sum(conflicts.values()),
        "nonfinite_values": nonfinite,
    }
    findings = []
    cut = [s["shard"] for s in per_shard if s["at_excel_row_limit"]]
    if cut:
        findings.append({"id": "SHARD_AT_EXCEL_ROW_LIMIT", "severity": "INFO",
                         "text": f"{', '.join(cut)} stop at the Excel limit; the cut falls inside an element, so a later shard must supply the remainder"})
    if doc["rows_repeated_in_later_shard"]:
        findings.append({"id": "SHARD_ROWS_REPEATED", "severity": "INFO",
                         "text": "rows exported in more than one shard; keep one copy of each key"})
    if conflicts:
        findings.append({"id": "SHARD_REPEAT_CONFLICT", "severity": "ERROR",
                         "text": "a repeated key carries different force values in different shards"})
    if incomplete:
        findings.append({"id": "BEAM_GRID_INCOMPLETE", "severity": "ERROR",
                         "text": f"{len(incomplete)} elements lack rows for some case/station: the cut was not recovered by another shard"})
    if any(s["duplicate_key_rows_inside_shard"] for s in per_shard):
        findings.append({"id": "DUPLICATE_KEY_INSIDE_SHARD", "severity": "ERROR", "text": "repeated key inside one shard"})
    if nonfinite:
        findings.append({"id": "NONFINITE_FORCE_VALUES", "severity": "ERROR", "text": "missing or nonfinite force values"})
    if frame_elements is not None:
        missing = sorted(set(stations) - set(frame_elements))
        story_diff = sorted(e for e in stations if e in frame_elements and frame_elements[e] != story_of.get(e))
        doc["frame_table_match"] = {"beam_elements_missing_from_frame_table": len(missing),
                                    "story_disagreements": len(story_diff)}
        if missing or story_diff:
            findings.append({"id": "BEAM_FRAME_TABLE_MISMATCH", "severity": "ERROR",
                             "text": "beam elements absent from, or on a different story than, the frame table"})
    doc["findings"] = findings
    doc["union_status"] = ("UNION_COMPLETE_AND_CONSISTENT"
                           if not any(f["severity"] == "ERROR" for f in findings) else "UNION_HAS_ERRORS")
    return doc
