"""ETABS source-role picker + split beam force workbook regressions."""
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from components.inputs.etabs_excel_selection import (
    classify_etabs_excel_selection, validate_full_table_selection,
    discover_beam_force_parts, build_analysis_table_catalog, resolve_analysis_table,
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

    def test_split_selection_routes_only_unique_joint_reaction_owner(self):
        first=self.workbook("Analysis Export FIRST LOT.xlsx", ["Story Forces"])
        third=self.workbook("Analysis Export THIRD LOT.xlsx", ["Joint Reactions"])
        beam=self.workbook("Beam Forces Element 1 latest.xlsx", ["Element Forces - Beams"])
        selected=classify_etabs_excel_selection([first, third, beam], split_analysis=True)
        self.assertEqual(selected["analysis"], third)
        self.assertEqual(selected["analysis_files"], [first, third])
        duplicate=self.workbook("Analysis Export duplicate.xlsx", ["Story Forces"])
        with self.assertRaises(ValueError):
            classify_etabs_excel_selection([first, third, duplicate, beam], split_analysis=True)

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

    def test_split_table_index_unique_owners_and_missing_table(self):
        first=self.workbook("First.xlsx",["Story Forces","Story Drifts"])
        second=self.workbook("Second.xlsx",["Modal Periods And Frequencies"])
        third=self.workbook("Third.xlsx",["Joint Reactions"])
        catalog=build_analysis_table_catalog([first,second,third])
        self.assertEqual(catalog["engineering_acceptance"],"NOT_VERIFIED")
        self.assertEqual(resolve_analysis_table(catalog,"STORY FORCES"),(first,"Story Forces"))
        self.assertEqual(resolve_analysis_table(catalog,"Joint Reactions"),(third,"Joint Reactions"))
        self.assertEqual(resolve_analysis_table(catalog,"Modal Periods And Frequencies")[0],second)
        with self.assertRaisesRegex(ValueError,"found 0"):
            resolve_analysis_table(catalog,"Joint Restraint Assignments")

    def test_split_table_index_ambiguity_and_source_changes(self):
        first=self.workbook("First.xlsx",["Story Forces"])
        second=self.workbook("Second.xlsx",["Story Forces","Joint Reactions"])
        catalog=build_analysis_table_catalog([first,second])
        self.assertEqual(catalog["ambiguous_tables"],["story forces"])
        with self.assertRaisesRegex(ValueError,"found 2"):
            resolve_analysis_table(catalog,"Story Forces")
        self.workbook("Second.xlsx",["Changed"])
        with self.assertRaisesRegex(ValueError,"bytes changed"):
            resolve_analysis_table(catalog,"Joint Reactions")
        second.write_bytes(first.read_bytes())
        with self.assertRaisesRegex(ValueError,"identical bytes"):
            build_analysis_table_catalog([first,second])

    def test_index_command_is_private_and_does_not_register(self):
        import json
        from tools.REGISTER_CURRENT_ETABS_TABLES import main
        first=self.workbook("First.xlsx",["Story Forces"])
        second=self.workbook("Second.xlsx",["Joint Reactions"])
        target=self.root/"catalog.private.json"
        args=["--analysis-files",str(first),str(second),"--table-index-output",str(target)]
        self.assertEqual(main(args),0)
        catalog=json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(resolve_analysis_table(catalog,"Joint Reactions")[0],second)
        self.assertFalse((self.root/"01_ETABS_EXPORT").exists())
        with self.assertRaises(SystemExit):
            main(args)
        with self.assertRaises(SystemExit):
            main(args+["--audit-output",str(self.root/"audit.private.json")])

    def test_combined_selection_is_wired_into_gravity_gui(self):
        code=(Path(__file__).resolve().parents[1]/"components"/"gravity"/
              "gui_and_reports.py").read_text(encoding="utf-8-sig")
        self.assertIn("def _choose_all_etabs_excel_sources(self):",code)
        self.assertIn("filedialog.askopenfilenames(",code)
        self.assertIn("classify_etabs_excel_selection(selected, split_analysis=True)",code)
        self.assertIn("self.etabs_beam_forces_paths=list(grouped",code)
        self.assertIn("self._choose_etabs_full_table",code)
        self.assertIn("self._discover_etabs_beam_parts_folder",code)


if __name__=="__main__":
    unittest.main()
