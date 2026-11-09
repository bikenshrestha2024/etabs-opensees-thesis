"""Deterministic offline node-mapping checks; no ETABS/OpenSees/plotly required."""
import csv
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from components.validation.gravity_reactions_3d import load_rows, create_audit

HEADERS = ["ETABS Unique Name", "ETABS Label", "OpenSees Node Tag",
           "X (m)", "Y (m)", "Z (m)", "ETABS FZ (kN)",
           "OpenSees source FZ (kN)", "OpenSees continuous FZ (kN)"]

class TestGravity3DMapping(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/"nodes.csv"
        with self.path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(HEADERS)
            w.writerow(["725", "23", "9", "6", "7.2", "0", "0", "4627.425", "2912.951"])
            w.writerow(["264", "47", "41", "12", "12", "0", "14748.522", "3887.122", "3816.614"])

    def test_zero_reaction_does_not_mean_free(self):
        a,b = load_rows(self.path)
        self.assertEqual(a["native_restraint"], "UNVERIFIED")
        self.assertEqual(a["source_kN"], 4627.425)
        self.assertIn("does not establish", a["zero_reaction_note"])
        self.assertEqual(b["source_minus_etabs_kN"], 3887.122-14748.522)

    def test_proven_native_restraint_flags(self):
        native = Path(self.temp.name)/"native.csv"
        with native.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ETABS Unique Name", "restraint_verified", "uz_restrained"])
            w.writerow(["725", "true", "false"])
            w.writerow(["264", "true", "true"])
        a,b = load_rows(self.path, native)
        self.assertEqual(a["native_restraint"], "UZ_FREE")
        self.assertEqual(b["native_restraint"], "UZ_FIXED")

    def test_duplicate_etabs_id_fails(self):
        with self.path.open("a") as f:
            f.write("264,47,42,12,12,0,0,0,0\n")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            load_rows(self.path)

    def test_html_traces_keep_labels_separate_from_hover_evidence(self):
        try:
            import plotly.offline
        except ImportError:
            self.skipTest("Plotly is optional for CSV mapping; required for HTML export")
        with patch.object(plotly.offline, "plot") as render:
            create_audit(self.path, Path(self.temp.name)/"output")
        figure = render.call_args.args[0]
        self.assertEqual(len(figure.data), 5)
        self.assertIn("264", figure.data[0].text)
        self.assertIn("OpenSees node 9", figure.data[0].hovertext[0])
        self.assertIn("UNVERIFIED", figure.data[0].hovertext[0])

if __name__ == "__main__":
    unittest.main()
