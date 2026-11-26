"""Read ETABS table exports and report the floor load path (slab -> beams -> joints).

[REF docs/source/tools/etabs_beam_slab_load_path.py.md]
[REF docs/validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md]

Post-processing diagnostic only. Inputs are an ETABS database-table export
(assignment workbook: title row, header row, units row per sheet) and one or more
'Element Forces - Beams' workbooks, which may be split or truncated at the Excel
row limit. Both are read with streaming openpyxl readers; nothing is modified,
no EDB is opened and no solver is imported. Units: kN, m.

What it reports:
* beam-force file coverage: rows read, whether a sheet reached the Excel row
  limit, beams per (storey, case); overlapping rows must agree or it fails;
* per storey and load case: the vertical load carried on the beam clear spans
  (V2 at the J face minus V2 at the I face) against the beam self weight and
  uniform frame loads on the clear span, and the beam end shears delivered to
  joints inside a plan box (the core) compared with simple-span statics;
* the share of each floor object's area whose corners lie in the box when each
  corner takes a quarter (the load path of an unmeshed four-node floor shell);
* ETABS storey masses times g against an OpenSees storey ledger.

Status is always DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATUS = "DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE"
SCHEMA = "etabs-beam-slab-load-path-v1"
EXCEL_DATA_ROW_LIMIT = 1048576 - 3  # ETABS table: title, header and units rows
TABLES = ("Point Object Connectivity", "Beam Object Connectivity",
          "Floor Object Connectivity", "Frame Assigns - End Len Offsets",
          "Frame Assigns - Sect Prop", "Frame Sec Def - Conc Rect",
          "Mat Prop - Basic Mech Props", "Frame Loads - Distributed",
          "Load Cases - Linear Static", "Load Pattern Definitions")


def read_tables(workbook, names=TABLES):
    """Return {sheet: [row dict]} for the named sheets of an ETABS table export."""
    from openpyxl import load_workbook
    from components.validation.etabs_assignment_gravity_audit import _rows
    wb = load_workbook(workbook, read_only=True, data_only=True)
    try:
        missing = [n for n in names if n not in wb.sheetnames]
        if missing:
            raise ValueError("Assignment export lacks sheets: " + ", ".join(missing))
        return {n: _rows(wb, n) for n in names}
    finally:
        wb.close()


def scan_beam_forces(paths, cases, *, atol=1e-6, rtol=1e-9):
    """Stream beam-force workbooks; keep rows of `cases`; check overlaps and coverage."""
    from components.validation.etabs_split_beam_forces import _stream_tables
    wanted = set(cases)
    records, coverage = {}, []
    for path in paths:
        count, last, beams = 0, None, defaultdict(set)
        for _sheet, row in _stream_tables(path):
            if row["Output Case"] in (None, "") and row["Story"] in (None, ""):
                continue  # ETABS units row below the column names
            count += 1
            story, case = str(row["Story"]), str(row["Output Case"])
            beams[(story, case)].add(str(row["Unique Name"]))
            last = (story, str(row["Unique Name"]), case)
            if case not in wanted:
                continue
            key = (story, str(row["Unique Name"]), case, round(float(row["Station"]), 6))
            value = tuple(float(row[c]) for c in ("P", "V2", "M3"))
            old = records.get(key)
            if old is not None and not all(math.isclose(a, b, abs_tol=atol, rel_tol=rtol)
                                           for a, b in zip(old, value)):
                raise ValueError(f"Conflicting overlapping beam-force rows at {key}")
            records[key] = value
        coverage.append(dict(file=Path(path).name, data_rows=count,
                             reached_excel_row_limit=count >= EXCEL_DATA_ROW_LIMIT,
                             last_row_identity=list(last) if last else None,
                             beams_per_story_case={f"{s}|{c}": len(v) for (s, c), v in
                                                   beams.items() if c in wanted}))
    return records, coverage


def _num(value, name):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Nonfinite value for " + name)
    return number


def model_geometry(tables):
    """Beam end points, clear-span offsets, self weight per m and case line loads."""
    pts = {str(r["UniqueName"]): (_num(r["X"], "X"), _num(r["Y"], "Y"), _num(r["Z"], "Z"))
           for r in tables["Point Object Connectivity"]}
    unit_weight = {str(r["Material"]): _num(r["UnitWeight"], "UnitWeight")
                   for r in tables["Mat Prop - Basic Mech Props"]}
    rect = {str(r["Name"]): _num(r["Depth"], "Depth") * _num(r["Width"], "Width") / 1e6
            * unit_weight[str(r["Material"])] * _num(r["Weight Modifier"], "Weight Modifier")
            for r in tables["Frame Sec Def - Conc Rect"]}
    section = {str(r["UniqueName"]): str(r["Section Property"])
               for r in tables["Frame Assigns - Sect Prop"]}
    offsets = {str(r["UniqueName"]): (_num(r["Offset I"], "Offset I") / 1000.,
                                      _num(r["Offset J"], "Offset J") / 1000.)
               for r in tables["Frame Assigns - End Len Offsets"]}
    self_weight = {str(r["Name"]): _num(r["Self Weight Multiplier"], "multiplier")
                   for r in tables["Load Pattern Definitions"]}
    case_patterns, current = defaultdict(list), None
    for r in tables["Load Cases - Linear Static"]:
        current = str(r["Name"]) if r.get("Name") not in (None, "") else current
        if str(r.get("Load Type")) == "Load":
            case_patterns[current].append((str(r["Load Name"]), _num(r["Load SF"], "Load SF")))
    line = defaultdict(lambda: defaultdict(float))
    for r in tables["Frame Loads - Distributed"]:
        if (str(r["Direction"]) != "Gravity" or str(r["Distance Type"]) != "Relative"
                or _num(r["Relative Distance A"], "A") != 0 or _num(r["Relative Distance B"], "B") != 1
                or _num(r["Force A"], "Force A") != _num(r["Force B"], "Force B")):
            raise ValueError("Only full-length uniform gravity frame loads are supported: "
                             + str(r["UniqueName"]))
        line[str(r["UniqueName"])][str(r["Load Pattern"])] += _num(r["Force A"], "Force A")
    beams = {}
    for r in tables["Beam Object Connectivity"]:
        uid = str(r["Unique Name"])
        sec = section[uid]
        if sec not in rect:
            raise ValueError(f"Beam {uid}: section {sec} is not a concrete rectangle")
        beams[uid] = dict(story=str(r["Story"]), i=pts[str(r["UniquePtI"])],
                          j=pts[str(r["UniquePtJ"])], length=_num(r["Length"], "Length"),
                          offsets=offsets[uid], self_weight_kN_m=rect[sec], line=dict(line[uid]))
    return dict(beams=beams, points=pts, case_patterns=dict(case_patterns),
                self_weight_multiplier=self_weight)


def in_box(box, xy, tol=1e-9):
    x0, x1, y0, y1 = box
    return x0 - tol <= xy[0] <= x1 + tol and y0 - tol <= xy[1] <= y1 + tol


def beam_load_path(records, geometry, core_box):
    """Per storey/case: clear-span load, expected load, end shears to box joints."""
    stations = defaultdict(list)
    for (story, uid, case, st), value in records.items():
        stations[(story, uid, case)].append((st, value))
    out, beams_out = {}, []
    for (story, uid, case), rows in sorted(stations.items()):
        rows.sort()
        b = geometry["beams"].get(uid)
        if b is None or b["story"] != story:
            raise ValueError(f"Beam {uid} ({story}) is not in the assignment export")
        oi, oj = b["offsets"]
        if abs(rows[0][0] - oi) > 1e-4 or abs(rows[-1][0] - (b["length"] - oj)) > 1e-4:
            raise ValueError(f"Beam {uid} {case}: end stations are not at the rigid-zone faces")
        w = 0.
        for pattern, factor in geometry["case_patterns"].get(case, ()):
            w += factor * (geometry["self_weight_multiplier"].get(pattern, 0.) * b["self_weight_kN_m"]
                           + b["line"].get(pattern, 0.))
        w_line = sum(f * b["line"].get(p, 0.) for p, f in geometry["case_patterns"].get(case, ()))
        vi, vj = rows[0][1][1], rows[-1][1][1]
        clear = b["length"] - oi - oj
        # Self weight is not applied on rigid zones (ETABS weight is clear-length);
        # uniform frame loads on rigid zones go straight to the joint.
        ri, rj = -vi + w_line * oi, vj + w_line * oj
        ci, cj = in_box(core_box, b["i"]), in_box(core_box, b["j"])
        d = out.setdefault(f"{story}|{case}", defaultdict(float))
        d["clear_span_load_kN"] += vj - vi
        d["expected_clear_span_load_kN"] += w * clear
        d["beam_load_to_joints_kN"] += ri + rj
        d["to_box_joints_kN"] += ri * ci + rj * cj
        if ci != cj:
            d["mixed_beams"] += 1
            d["mixed_box_end_simple_span_kN"] += (vj - vi) / 2 + w_line * (oi if ci else oj)
        d["max_abs_P_kN"] = max(d["max_abs_P_kN"], max(abs(v[0]) for _, v in rows))
        variation = max(v[1] for _, v in rows) - min(v[1] for _, v in rows)
        d["max_V2_variation_kN"] = max(d["max_V2_variation_kN"], variation)
        beams_out.append(dict(story=story, beam=uid, case=case, box_ends=int(ci) + int(cj),
                              clear_m=clear, V2_I_kN=vi, V2_J_kN=vj,
                              clear_span_load_kN=vj - vi, expected_kN=w * clear))
    for d in out.values():
        d["to_box_joints_simple_span_kN"] = d["mixed_box_end_simple_span_kN"]
        d["beam_flexure_transfer_to_box_kN"] = d["to_box_joints_kN"] - d["mixed_box_end_simple_span_kN"]
    return {k: dict(v) for k, v in out.items()}, beams_out


def slab_corner_split(tables, core_box):
    """Floor area per storey and the part assigned to box corners, a quarter per corner."""
    pts = {str(r["UniqueName"]): (_num(r["X"], "X"), _num(r["Y"], "Y"))
           for r in tables["Point Object Connectivity"]}
    out = defaultdict(lambda: dict(area_m2=0., box_corner_area_m2=0., floors=0))
    for r in tables["Floor Object Connectivity"]:
        corners = [pts[str(r[f"UniquePt{k}"])] for k in range(1, 5)]
        area = _num(r["Area"], "Area")
        d = out[str(r["Story"])]
        d["area_m2"] += area
        d["box_corner_area_m2"] += area * sum(in_box(core_box, c) for c in corners) / 4.
        d["floors"] += 1
    return dict(out)


def source_gravity(tables):
    """ETABS internal g (m/s^2) from UnitWeight (kN/m3) / UnitMass (kg/m3) of the materials."""
    ratios = sorted(_num(r["UnitWeight"], "UnitWeight") * 1000. / _num(r["UnitMass"], "UnitMass")
                    for r in tables["Mat Prop - Basic Mech Props"] if r.get("UnitMass"))
    if not ratios or ratios[-1] - ratios[0] > 1e-4 * ratios[0]:
        raise ValueError("Materials do not share one weight/mass ratio: " + str(ratios))
    return ratios[len(ratios) // 2]


def story_mass_comparison(mass_rows, ledger_rows, *, g, g_source):
    """ETABS 'Mass Summary by Story' UX (kg) times g against ledger weights (kN).

    g is the project value; g_source is the ETABS internal value that turned the
    source weights into masses (see source_gravity), so m * g_source recovers them.
    """
    etabs = {str(r["Story"]).replace(" ", "").lower(): _num(r["UX"], "UX") for r in mass_rows}
    rows = []
    for led in ledger_rows:
        key = str(led["storey"]).replace("Storey", "Story").replace(" ", "").lower()
        if key not in etabs:
            raise ValueError("No ETABS storey mass for " + str(led["storey"]))
        m = etabs[key]
        w = _num(led["weight_kN"], "ledger weight")
        rows.append(dict(storey=led["storey"], ledger_kN=w, etabs_mass_kg=m,
                         etabs_kN_at_g=m * g / 1000., etabs_kN_at_source_g=m * g_source / 1000.,
                         diff_at_g_kN=w - m * g / 1000., diff_at_source_g_kN=w - m * g_source / 1000.))
    return rows


def ledger_from_breakdown(path, *, live_factor=0.3, storage_factor=0.6):
    """Storey seismic weights from a Gravity_Storey_Load_Breakdown JSON (rows).

    W = dead + live_factor * live + storage_factor * storage; roof live excluded.
    The factors are the caller's mass-source assumption, not read from ETABS.
    """
    rows = json.loads(Path(path).read_text(encoding="utf-8"))["rows"]
    return [dict(storey=r["storey"], weight_kN=_num(r["dead_total_kN"], "dead")
                 + live_factor * _num(r["live_total_kN"], "live")
                 + storage_factor * _num(r["storage_live_kN"], "storage")) for r in rows]


def analyse(assignment, beam_files, *, cases=("Dead", "Live"), core_box=(6., 18., 6., 12.),
            ledger=None, g=None):
    from components.nbc105.constants import GRAVITY_M_S2
    g = GRAVITY_M_S2 if g is None else g
    names = TABLES + (("Mass Summary by Story",) if ledger is not None else ())
    tables = read_tables(assignment, names)
    geometry = model_geometry(tables)
    records, coverage = scan_beam_forces(beam_files, cases)
    storeys, beams = beam_load_path(records, geometry, core_box)
    totals = defaultdict(float)
    for key, d in storeys.items():
        for name in ("clear_span_load_kN", "expected_clear_span_load_kN", "beam_load_to_joints_kN",
                     "to_box_joints_kN", "to_box_joints_simple_span_kN",
                     "beam_flexure_transfer_to_box_kN"):
            totals[key.split("|")[1] + "." + name] += d[name]
    report = dict(status=STATUS, schema=SCHEMA, core_box=list(core_box), cases=list(cases),
                  coverage=coverage, storeys=storeys, totals=dict(totals),
                  slab_corner_split=slab_corner_split(tables, core_box), beams=beams)
    if ledger is not None:
        report["source_gravity_m_s2"] = source_gravity(tables)
        report["storey_mass_comparison"] = story_mass_comparison(
            tables["Mass Summary by Story"], ledger, g=g, g_source=report["source_gravity_m_s2"])
    return report


def write_run(report, export_dir, case_id, *, state="AS_CONFIGURED", inputs=()):
    """Write the report to a new run folder (docs/OUTPUT_FOLDER_STANDARD.md)."""
    import hashlib
    from components.inputs.output_contract import atomic_json, create_case_run, write_table
    run = create_case_run(export_dir, "GRAVITY", case_id, state=state)
    hashes = {}
    for path in inputs:
        h = hashlib.sha256()
        with Path(path).open("rb") as fp:
            for block in iter(lambda: fp.read(1 << 20), b""):
                h.update(block)
        hashes[Path(path).name] = h.hexdigest()
    atomic_json(run / "00_INPUT_SOURCE" / "ETABS_BEAM_SLAB_LOAD_PATH_INPUTS.json",
                dict(status=STATUS, input_sha256=hashes))
    atomic_json(run / "05_COMPARISONS" / "ETABS_BEAM_SLAB_LOAD_PATH.json",
                dict({k: v for k, v in report.items() if k != "beams"}, input_sha256=hashes))
    columns = ("story", "beam", "case", "box_ends", "clear_m", "V2_I_kN", "V2_J_kN",
               "clear_span_load_kN", "expected_kN")
    write_table(run / "05_COMPARISONS" / "ETABS_BEAM_SLAB_LOAD_PATH_BEAMS.csv",
                report["beams"], columns=columns)
    return run


def main(argv=None):
    """CLI entry point; see the source guide.

    [REF docs/source/tools/etabs_beam_slab_load_path.py.md]
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--assignment", required=True, help="ETABS assignment table export (.xlsx)")
    ap.add_argument("--beam-forces", required=True, nargs="+", help="Element Forces - Beams .xlsx")
    ap.add_argument("--cases", nargs="+", default=["Dead", "Live"])
    ap.add_argument("--core-box", nargs=4, type=float, required=True,
                    metavar=("XMIN", "XMAX", "YMIN", "YMAX"))
    ap.add_argument("--storey-breakdown", help="Gravity_Storey_Load_Breakdown_V131.json (optional)")
    ap.add_argument("--live-factor", type=float, default=0.3)
    ap.add_argument("--g", type=float, help="Project g (default components.nbc105.constants)")
    ap.add_argument("--export-dir", help="Export case root; omit to print only")
    ap.add_argument("--case-id", default="BEAM_SLAB_LOAD_PATH")
    ap.add_argument("--state", default="AS_CONFIGURED")
    args = ap.parse_args(argv)
    ledger = (ledger_from_breakdown(args.storey_breakdown, live_factor=args.live_factor)
              if args.storey_breakdown else None)
    report = analyse(args.assignment, args.beam_forces, cases=tuple(args.cases),
                     core_box=tuple(args.core_box), ledger=ledger, g=args.g)
    summary = {k: report[k] for k in ("status", "coverage", "totals", "storey_mass_comparison")
               if k in report}
    if args.export_dir:
        run = write_run(report, args.export_dir, args.case_id, state=args.state,
                        inputs=[args.assignment, *args.beam_forces])
        summary["run_dir"] = str(run)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
