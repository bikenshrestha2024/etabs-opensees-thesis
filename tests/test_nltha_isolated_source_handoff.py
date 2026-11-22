"""Regression for the real 32-foundation NLTHA builder source handoff.

The old exploratory runner copied five JSON files but omitted the
OpenSees_Element_Connectivity.json file that build_complete_model() reads.
No OpenSees numerical model or source data are fabricated by this test.
"""
import hashlib
import tempfile
import unittest
from pathlib import Path

from components.nonlinear_time_history import building_exploratory
from components.nonlinear_time_history.source_model_handoff import (
    REQUIRED_SOURCE_FILES, OPTIONAL_SOURCE_FILES
)


class NonlinearIsolatedSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "original_etabs_export"
        self.target = self.root / "run" / "isolated_model"
        self.source.mkdir()
        for filename in REQUIRED_SOURCE_FILES + OPTIONAL_SOURCE_FILES:
            (self.source / filename).write_bytes(
                ("immutable ETABS source: " + filename).encode("utf-8"))

    def test_actual_nltha_runner_stages_topology_with_five_core_jsons(self):
        manifest = building_exploratory.stage_existing_nltha_inputs(
            self.source, self.target)
        self.assertTrue((self.target / "OpenSees_Element_Connectivity.json").is_file())
        for filename in REQUIRED_SOURCE_FILES + OPTIONAL_SOURCE_FILES:
            original = (self.source / filename).read_bytes()
            self.assertEqual((self.target / filename).read_bytes(), original)
            self.assertEqual(manifest[filename], hashlib.sha256(original).hexdigest())

    def test_missing_connectivity_aborts_before_constructing_output(self):
        (self.source / "OpenSees_Element_Connectivity.json").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "OpenSees_Element_Connectivity"):
            building_exploratory.stage_existing_nltha_inputs(self.source, self.target)
        self.assertFalse(self.target.exists())

    def test_changed_existing_copy_is_not_overwritten(self):
        self.target.mkdir(parents=True)
        (self.target / "OpenSees_Element_Connectivity.json").write_text("different data")
        with self.assertRaisesRegex(FileExistsError, "OpenSees_Element_Connectivity"):
            building_exploratory.stage_existing_nltha_inputs(self.source, self.target)
        self.assertEqual(
            (self.target / "OpenSees_Element_Connectivity.json").read_text(),
            "different data")


if __name__ == "__main__":
    unittest.main()
