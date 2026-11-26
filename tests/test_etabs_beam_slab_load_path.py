"""Deterministic tests for tools/etabs_beam_slab_load_path.py (no ETABS, no OpenSees)."""
import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from tools import etabs_beam_slab_load_path as lp
from tools.audit_output_layout import audit_run_layout

BOX = (5., 7., -1., 7.)  # contains points B (6, 0) and C (6, 6)

SHEETS = {
    "Point Object Connectivity": (["UniqueName", "X", "Y", "Z"],
                                  [["A", 0, 0, 3], ["B", 6, 0, 3], ["C", 6, 6, 3], ["D", 0, 6, 3]]),
    "Beam Object Connectivity": (["Unique Name", "Story", "UniquePtI", "UniquePtJ", "Length"],
                                 [["1", "Story1", "A", "B", 6]]),
    "Floor Object Connectivity": (["Unique Name", "Story", "UniquePt1", "UniquePt2", "UniquePt3",
                                   "UniquePt4", "Area"], [["F1", "Story1", "A", "B", "C", "D", 36]]),
    "Frame Assigns - End Len Offsets": (["UniqueName", "Offset I", "Offset J"], [["1", 500, 0]]),
    "Frame Assigns - Sect Prop": (["UniqueName", "Section Property"], [["1", "B1"]]),
    "Frame Sec Def - Conc Rect": (["Name", "Material", "Depth", "Width", "Weight Modifier"],
                                  [["B1", "M1", 500, 300, 1]]),
    "Mat Prop - Basic Mech Props": (["Material", "UnitWeight", "UnitMass"],
                                    [["M1", 25, 25 / 9.80665 * 1000]]),
    "Frame Loads - Distributed": (["UniqueName", "Load Pattern", "Direction", "Distance Type",
                                   "Relative Distance A", "Relative Distance B", "Force A",
                                   "Force B"], [["1", "Wall", "Gravity", "Relative", 0, 1, 2, 2]]),
    "Load Cases - Linear Static": (["Name", "Load Type", "Load Name", "Load SF"],
                                   [["Dead", "Load", "Self Weight", 1], ["Dead", "Load", "Wall", 1],
                                    ["Live", "Load", "Live", 1]]),
    "Load Pattern Definitions": (["Name", "Self Weight Multiplier"],
                                 [["Self Weight", 1], ["Wall", 0], ["Live", 0]]),
    "Mass Summary by Story": (["Story", "UX"], [["Story1", 1000.], ["Base", 100.]]),
}
HEADER = ["Story", "Beam", "Unique Name", "Output Case", "Case Type", "Step Type",
          "Step Number", "Station", "P", "V2", "V3", "T", "M2", "M3"]


def table(wb, name, header, rows):
    ws = wb.create_sheet(name)
    ws.append(["TABLE:  " + name])
    ws.append(header)
    ws.append([""] * len(header))
    for row in rows:
        ws.append(row)


def force(case, station, v2):
    return ["Story1", "B1", "1", case, "LinStatic", "", None, station, 0, v2, 0, 0, 0, 0]


def build(tmp, live_overlap=-2.0):
    wb = Workbook(); wb.remove(wb.active)
    for name, (header, rows) in SHEETS.items():
        table(wb, name, header, rows)
    assignment = tmp / "assignment.xlsx"; wb.save(assignment)
    files = []
    parts = ([force("Dead", 0.5, -15.), force("Dead", 3.25, 0.8125), force("Dead", 6.0, 16.625),
              force("Live", 0.5, -2.)],
             [force("Live", 0.5, live_overlap), force("Live", 3.25, -2.), force("Live", 6.0, -2.),
              force("EQX", 0.5, 99.)])
    for k, rows in enumerate(parts):
        wb = Workbook(); wb.remove(wb.active)
        table(wb, "Element Forces - Beams", HEADER, rows)
        path = tmp / f"beams_{k}.xlsx"; wb.save(path); files.append(path)
    return assignment, files


class LoadPath(unittest.TestCase):
    def test_span_load_end_shears_and_slab_corners(self):
        with tempfile.TemporaryDirectory() as tmp:
            assignment, files = build(Path(tmp))
            ledger = [dict(storey="BASE", weight_kN=0.981), dict(storey="Storey 1", weight_kN=9.81)]
            rep = lp.analyse(assignment, files, core_box=BOX, ledger=ledger)
        dead, live = rep["storeys"]["Story1|Dead"], rep["storeys"]["Story1|Live"]
        # Self weight 0.3*0.5*25 = 3.75 kN/m plus 2 kN/m over the 5.5 m clear span.
        self.assertAlmostEqual(dead["expected_clear_span_load_kN"], 5.75 * 5.5)
        self.assertAlmostEqual(dead["clear_span_load_kN"], 31.625)
        # I end: 15 kN shear + 2 kN/m on the 0.5 m rigid zone; self weight not on rigid zone.
        self.assertAlmostEqual(dead["beam_load_to_joints_kN"], 16. + 16.625)
        self.assertAlmostEqual(dead["to_box_joints_kN"], 16.625)
        self.assertAlmostEqual(dead["to_box_joints_simple_span_kN"], 31.625 / 2)
        self.assertAlmostEqual(dead["beam_flexure_transfer_to_box_kN"], 0.8125)
        # Constant V2: no load on the span, end moments move 2 kN out of the box.
        self.assertAlmostEqual(live["clear_span_load_kN"], 0.)
        self.assertAlmostEqual(live["max_V2_variation_kN"], 0.)
        self.assertAlmostEqual(live["to_box_joints_kN"], -2.)
        self.assertEqual(rep["slab_corner_split"]["Story1"],
                         dict(area_m2=36., box_corner_area_m2=18., floors=1))
        self.assertEqual([c["data_rows"] for c in rep["coverage"]], [4, 4])
        self.assertFalse(any(c["reached_excel_row_limit"] for c in rep["coverage"]))
        mass = {r["storey"]: r for r in rep["storey_mass_comparison"]}
        self.assertAlmostEqual(mass["Storey 1"]["diff_at_g_kN"], 0.)
        self.assertAlmostEqual(mass["Storey 1"]["etabs_kN_at_source_g"], 9.80665)
        self.assertAlmostEqual(rep["source_gravity_m_s2"], 9.80665)
        self.assertEqual(rep["status"], "DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE")

    def test_conflicting_overlap_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            assignment, files = build(Path(tmp), live_overlap=-2.5)
            with self.assertRaises(ValueError):
                lp.analyse(assignment, files, core_box=BOX)

    def test_ledger_from_breakdown_and_cli_run_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            breakdown = tmp / "breakdown.json"
            breakdown.write_text(json.dumps(dict(rows=[
                dict(storey="BASE", dead_total_kN=1., live_total_kN=0., storage_live_kN=0.),
                dict(storey="Storey 1", dead_total_kN=8., live_total_kN=6., storage_live_kN=0.)])))
            ledger = lp.ledger_from_breakdown(breakdown)
            self.assertAlmostEqual(ledger[1]["weight_kN"], 9.8)
            assignment, files = build(tmp)
            export = tmp / "EXPORT_CASE"; export.mkdir()
            self.assertEqual(lp.main(["--assignment", str(assignment), "--beam-forces",
                                      *map(str, files), "--core-box", *map(str, BOX),
                                      "--storey-breakdown", str(breakdown),
                                      "--export-dir", str(export), "--case-id", "T"]), 0)
            runs = list((export / "02_GRAVITY" / "RUNS" / "AS_CONFIGURED" / "T").iterdir())
            self.assertEqual(len(runs), 1)
            self.assertTrue(audit_run_layout(runs[0])["ok"])
            report = json.loads((runs[0] / "05_COMPARISONS" / "ETABS_BEAM_SLAB_LOAD_PATH.json")
                                .read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE")
            self.assertIn("storey_mass_comparison", report)


if __name__ == "__main__":
    unittest.main()
