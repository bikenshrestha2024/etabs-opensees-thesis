"""Deterministic tests for tools/gravity_reaction_attribution.py (no ETABS, no OpenSees)."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools import gravity_reaction_attribution as gra
from tools.audit_output_layout import audit_run_layout


def sup(label, x, y, etabs, opensees):
    return dict(label=label, x=x, y=y, etabs=etabs, opensees=opensees)


def symmetric_case():
    # Core walls at x=4 (two supports), columns at x=0 and x=8; plan symmetric about x=4, y=2.
    supports = [
        sup("c1", 0, 0, 100., 90.), sup("c2", 0, 4, 100., 90.),
        sup("c3", 8, 0, 100., 90.), sup("c4", 8, 4, 100., 90.),
        sup("w1", 4, 0, 200., 220.), sup("w2", 4, 4, 200., 220.),
        sup("z1", 4, 2, 0., 0.),
    ]
    loads = [(0, 0, 50.), (8, 4, 50.), (2, 0, 30.), (4, 2, 40.)]
    return supports, loads


class TributaryBenchmark(unittest.TestCase):
    def test_nearest_support_with_equal_tie_split(self):
        supports, loads = symmetric_case()
        trib = gra.tributary_benchmark(supports, loads)
        # (2,0) is equidistant from c1 (0,0) and w1 (4,0): 15 kN each.
        # (4,2) is equidistant from w1 and w2 (z1 carries no ETABS reaction): 20 kN each.
        self.assertAlmostEqual(trib[0], 50. + 15.)
        self.assertAlmostEqual(trib[4], 15. + 20.)
        self.assertAlmostEqual(trib[5], 20.)
        self.assertIsNone(trib[6])
        self.assertAlmostEqual(sum(t for t in trib if t is not None), 170.)

    def test_requires_reaction_bearing_support(self):
        with self.assertRaises(ValueError):
            gra.tributary_benchmark([sup("a", 0, 0, 0., 1.)], [(0, 0, 1.)])


class GroupScaling(unittest.TestCase):
    def test_pure_group_split_is_fully_explained(self):
        supports, _ = symmetric_case()
        groups = ["perimeter"] * 4 + ["core"] * 3
        out = gra.group_scaling(supports, groups)
        self.assertAlmostEqual(out["ratios"]["perimeter"], 0.9)
        self.assertAlmostEqual(out["ratios"]["core"], 1.1)
        self.assertAlmostEqual(out["sum_abs_raw_kN"], 80.)
        self.assertAlmostEqual(out["sum_abs_residual_kN"], 0.)
        self.assertAlmostEqual(out["explained_fraction"], 1.)

    def test_local_residual_is_reported(self):
        supports, _ = symmetric_case()
        supports[4]["opensees"] = 240.
        supports[5]["opensees"] = 200.
        groups = ["perimeter"] * 4 + ["core"] * 3
        out = gra.group_scaling(supports, groups)
        self.assertAlmostEqual(out["residuals"][4], 20.)
        self.assertAlmostEqual(out["residuals"][5], -20.)


class SymmetryStiffnessAndClassification(unittest.TestCase):
    def test_mirror_asymmetry_zero_for_symmetric_delta(self):
        supports, _ = symmetric_case()
        out = gra.mirror_asymmetry(supports, mirror_x=4, mirror_y=2)
        self.assertGreater(out["pairs_checked"], 0)
        self.assertAlmostEqual(out["max_asymmetry_kN"], 0.)
        supports[0]["opensees"] = 80.
        self.assertAlmostEqual(gra.mirror_asymmetry(supports, mirror_x=4)["max_asymmetry_kN"], 10.)

    def test_axial_stiffness_indicator(self):
        supports, _ = symmetric_case()
        groups = ["perimeter"] * 4 + ["core"] * 3
        # Core: 10 % more force but 30 % less displacement in OpenSees -> EA ratio 1.1/0.7.
        disp = {(0, 0): (-0.9e-2, -1e-2), (8, 4): (-0.9e-2, -1e-2),
                (4, 0): (-0.7e-2, -1e-2), (4, 4): (-0.7e-2, -1e-2)}
        out = gra.axial_stiffness_indicator(supports, groups, disp)
        self.assertAlmostEqual(out["core"]["axial_stiffness_ratio"], 1.1 / 0.7)
        self.assertAlmostEqual(out["perimeter"]["axial_stiffness_ratio"], 1.0)

    def test_classification_rules(self):
        self.assertEqual(gra.classify(sup("z", 0, 0, 0., 4563.), None), "SUPPORT_TOPOLOGY")
        self.assertEqual(gra.classify(sup("a", 0, 0, 100., 120.), 5.), "WITHIN_TOLERANCE")
        self.assertEqual(gra.classify(sup("a", 0, 0, 14748.5, 17789.8), 524.4),
                         "GROUP_AXIAL_STIFFNESS_SPLIT")
        self.assertEqual(gra.classify(sup("a", 0, 0, 1000., 1300.), 290.),
                         "LOCAL_REDISTRIBUTION")
        self.assertEqual(gra.classify(sup("a", 0, 0, 1000., None), None), "UNMATCHED")


class CliWritesStandardRunFolder(unittest.TestCase):
    def test_cli_creates_conforming_run(self):
        supports, loads = symmetric_case()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            s_csv, l_csv = tmp / "supports.csv", tmp / "applied.csv"
            with s_csv.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["etabs_point", "x_m", "y_m", "etabs_global_rz_kN", "opensees_rz_kN"])
                for s in supports:
                    w.writerow([s["label"], s["x"], s["y"], s["etabs"], s["opensees"]])
            with l_csv.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["pattern", "x_m", "y_m", "fz_kN", "gravity_factor"])
                for x, y, fz in loads:
                    w.writerow(["Dead", x, y, -fz, 1.0])
            export = tmp / "EXPORT_CASE"
            export.mkdir()
            self.assertEqual(gra.main([
                "--supports", str(s_csv), "--applied", str(l_csv),
                "--core-box", "4", "4", "0", "4", "--mirror-x", "4", "--tolerance-kN", "5",
                "--export-dir", str(export), "--case-id", "TEST_CASE"]), 0)
            runs = list((export / "02_GRAVITY" / "RUNS" / "AS_CONFIGURED" / "TEST_CASE").iterdir())
            self.assertEqual(len(runs), 1)
            self.assertTrue(audit_run_layout(runs[0])["ok"])
            self.assertEqual(sorted(p.name for p in export.iterdir()), ["02_GRAVITY"])
            report = json.loads((runs[0] / "05_COMPARISONS" /
                                 "GRAVITY_REACTION_ATTRIBUTION.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE")
            self.assertAlmostEqual(report["group_scaling"]["explained_fraction"], 1.)
            self.assertEqual(report["classification_counts"]["GROUP_AXIAL_STIFFNESS_SPLIT"], 6)
            self.assertEqual(report["classification_counts"]["WITHIN_TOLERANCE"], 1)
            self.assertIn("supports.csv", report["input_sha256"])


if __name__ == "__main__":
    unittest.main()
