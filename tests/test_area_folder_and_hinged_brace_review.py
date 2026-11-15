"""Source-only regression for area output navigation and hinged brace evidence.

No ETABS or native OpenSees/FSAM solver is exercised. The brace checks
verify export report metadata contracts, not connection constitutive behavior.
"""
import ast
from pathlib import Path
import tempfile
import unittest

from components.sections.area_elements import area_output_directory

ROOT=Path(__file__).resolve().parents[1]


class AreaOutputFolderTests(unittest.TestCase):
    def test_selected_existing_output_directory_opens_without_creating(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.assertEqual(area_output_directory(root),root)
            self.assertFalse((root/"02_MODEL").exists())
            expected=root/"02_MODEL"/"AREA_INTEGRATION"
            expected.mkdir(parents=True)
            self.assertEqual(area_output_directory(root),expected)
            self.assertEqual(area_output_directory(topology_json=root/"topology.json"),expected)

    def test_missing_export_directory_is_not_created(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"nonexistent"
            with self.assertRaises(FileNotFoundError):
                area_output_directory(target)
            self.assertFalse(target.exists())

    def test_gui_button_bound_to_safe_folder_resolution(self):
        source=(ROOT/"components/sections/area_elements.py").read_text(encoding="utf-8")
        self.assertIn('text="Open output folder"',source)
        self.assertIn('command=open_output_folder',source)
        self.assertIn('selected=area_output_directory(',source)
        self.assertIn('os.startfile(str(selected))',source)


class BraceReviewContractTests(unittest.TestCase):
    def test_raw_releases_and_three_id_namespaces_in_assembly_report(self):
        path=ROOT/"components/model/assembly.py"
        source=path.read_text(encoding="utf-8")
        ast.parse(source,filename=str(path))
        for key in ("hinged_brace_release_review","etabs_GetReleases_raw",
                    "etabs_unique_frame_id","opensees_topology_preview_tag",
                    "solver_element_tags","reviewed_nonlinear_status",
                    "BLOCKED_UNVERIFIED_CONNECTION_AND_BRACE"):
            with self.subTest(key=key):
                self.assertIn(key,source)
        # The future solver tags are computed from the actual frame element
        # insertion sequence, not a topology preview or an ETABS frame ID.
        self.assertIn('100000+len(frame_elements)',source)
        self.assertIn('if e.get(\'hinged_brace\'): raise ValueError',source)


if __name__=="__main__":
    unittest.main()
