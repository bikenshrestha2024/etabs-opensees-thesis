"""Stage 38 is an indexable alias to the existing native NLTHA CLI.

This test checks program discovery, rather than solving the full building.
No second constitutive solver or model converter may be introduced.
"""
import csv
import subprocess
import sys
import unittest
from pathlib import Path

from tools.audit_active_repository import CANONICAL

ROOT = Path(__file__).resolve().parents[1]


class DirectNLTHAStage38Navigation(unittest.TestCase):
    def test_stage38_single_canonical_alias(self):
        self.assertEqual(CANONICAL[38], "38_DIRECT_EXISTING_NLTHA.py")
        source = ROOT / CANONICAL[38]
        self.assertTrue(source.is_file())
        code = source.read_text(encoding="utf-8")
        self.assertIn("components.nonlinear_time_history.direct_existing_model", code)
        self.assertNotIn("openseespy.opensees", code)

    def test_stage38_documented_in_both_indices(self):
        for path in ("docs/programs/00_PROGRAM_INDEX.md", "launchers/README.md"):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("38_DIRECT_EXISTING_NLTHA.py", text, path)

    def test_single_owner_in_registry(self):
        with (ROOT/"engineering/registry/CANONICAL_MODULES.csv").open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(
            [row["existing_canonical_path"] for row in rows
             if row["domain"]=="nltha_existing_direct_execution"],
            ["components/nonlinear_time_history/direct_existing_model.py"])

    def test_alias_help_needs_no_native_solver_or_source_data(self):
        cli = ROOT / "38_DIRECT_EXISTING_NLTHA.py"
        result = subprocess.run([sys.executable, str(cli), "--help"],
                                cwd=ROOT, capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("--model-folder", result.stdout)
        self.assertIn("--x-path", result.stdout)
        self.assertIn("--y-path", result.stdout)
        self.assertIn("--output-dir", result.stdout)


if __name__=="__main__":
    unittest.main()
