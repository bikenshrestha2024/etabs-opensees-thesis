"""ETABS source-role picker + split beam force workbook regressions."""
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from components.inputs.etabs_excel_selection import (
    classify_etabs_excel_selection, validate_full_table_selection,
    discover_beam_force_parts,
)


class EtabsExcelRoleSelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def workbook(self,name,sheets):
        file=self.root/name
        book=Workbook()
        book.active.title=sheets[0]
        for sheet in sheets[1:]:
            book.create_sheet(sheet)
        book.save(file)
        return file

    def test_all_sources_selected_together_and_sorted(self):
        analysis=self.workbook("Analysis Export ULS 3 storey latest_compressed.xlsx",
                               ["Joint Reactions","Story Forces"])
        assign=self.workbook("Assignment Export ULS 3 storey latest.xlsx",
                             ["Frame Assigns - Summary","Material List by Object Type"])
        parts=[self.workbook(f"Beam Forces Element {i} latest.xlsx",
                             ["Element Forces - Beams"]) for i in (3,1,2)]
        selected=classify_etabs_excel_selection([parts[0],analysis,
                                                 parts[1],assign,parts[2]])
        self.assertEqual(selected["analysis"],analysis)
        self.assertEqual(selected["assignment"],assign)
        self.assertEqual([p.name for p in selected["beam"]],
                         [f"Beam Forces Element {i} latest.xlsx" for i in (1,2,3)])

    def test_three_beam_tables_not_accepted_as_full_table(self):
        wrong=self.workbook("Beam Forces Element 1 latest.xlsx",
                            ["Element Forces - Beams",
                             "Element Forces - Beams 2",
                             "Element Forces - Beams 3"])
        with self.assertRaisesRegex(ValueError,"BEAM-FORCE-ONLY"):
            validate_full_table_selection(wrong)

    def test_partial_analysis_lots_cannot_replace_joint_reactions(self):
        first=self.workbook("Analysis Export FIRST LOT.xlsx",
                            ["Story Forces","Story Drifts"])
        second=self.workbook("Analysis Export SECOND LOT.xlsx",
                             ["Objects and Elements - Joints","Modal Periods And Frequencies"])
        for path in (first,second):
            with self.subTest(path=path.name):
                with self.assertRaisesRegex(ValueError,"requires exactly one Joint Reactions"):
                    validate_full_table_selection(path)
        complete=self.workbook("Analysis Export complete.xlsx",
                               ["Joint Reactions","Story Forces"])
        self.assertEqual(validate_full_table_selection(complete),complete)

    def test_multiple_analysis_candidates_are_not_silently_replaced(self):
        first=self.workbook("Analysis Export ULS 3 storey latest.xlsx",
                            ["Joint Reactions"])
        second=self.workbook("Analysis Export ULS 3 storey latest_compressed.xlsx",
                             ["Joint Reactions"])
        beam=self.workbook("Beam Forces Element 1 latest.xlsx",
                           ["Element Forces - Beams"])
        with self.assertRaisesRegex(ValueError,"Multiple analyzed exports"):
            classify_etabs_excel_selection([first,second,beam])

    def test_folder_autodiscovery_requires_all_numbered_parts(self):
        parts=[self.workbook(f"Beam Forces Element {i} latest.xlsx",
                              ["Element Forces - Beams"]) for i in (2,1,3)]
        result=discover_beam_force_parts(self.root)
        self.assertEqual([p.name for p in result],
                         [f"Beam Forces Element {i} latest.xlsx"
                          for i in (1,2,3)])
        parts[1].unlink()
        with self.assertRaisesRegex(ValueError,"Missing numbered"):
            discover_beam_force_parts(self.root)
        parts[1]=self.workbook("Beam Forces Element 1 latest.xlsx",
                               ["Element Forces - Beams"])
        self.workbook("Beam Forces Element 2 alternate.xlsx",
                      ["Element Forces - Beams"])
        with self.assertRaisesRegex(ValueError,"Multiple beam force"):
            discover_beam_force_parts(self.root)

    def test_combined_selection_is_wired_into_gravity_gui(self):
        code=(Path(__file__).resolve().parents[1]/"components"/"gravity"/
              "gui_and_reports.py").read_text(encoding="utf-8-sig")
        self.assertIn("def _choose_all_etabs_excel_sources(self):",code)
        self.assertIn("filedialog.askopenfilenames(",code)
        self.assertIn("classify_etabs_excel_selection(selected)",code)
        self.assertIn("self.etabs_beam_forces_paths=list(grouped",code)
        self.assertIn("self._choose_etabs_full_table",code)
        self.assertIn("self._discover_etabs_beam_parts_folder",code)


if __name__=="__main__":
    unittest.main()
