"""Static Tk GUI contract tests; do not require a native display or OpenSees."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GUI=ROOT/"components/gravity/gui_and_reports.py"


class GravityLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=GUI.read_text(encoding="utf-8")
        cls.tree=ast.parse(cls.source,filename=str(GUI))
        cls.funcs={
            node.name: node
            for node in ast.walk(cls.tree)
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))
        }

    def test_main_actions_are_grouped_without_callback_duplication(self):
        source=self.source
        for tab in (
            'text="Review saved results"',
            'text="Verify ETABS and load path"',
            'text="Reports and evidence"',
        ):
            self.assertIn(tab,source)
        self.assertIn("action_tabs=ttk.Notebook(actions)",source)
        self.assertEqual(source.count('command=self._select_reaction_nodes'),1)
        for callback in (
            "_view_saved_case", "_compare_three_saved_cases",
            "_organize_existing_gravity_cases", "_audit_native_equivalence",
            "_direct_etabs_gravity_compare", "_export_all_pages",
            "_export_comparison_bundle", "_export_organized_evidence",
            "_open_output_folder",
        ):
            self.assertIn("self."+callback,source)

    def test_log_has_both_scrollbars_and_page_jumps(self):
        source=self.source
        self.assertIn('log_y=ttk.Scrollbar(log_frame,orient="vertical"',source)
        self.assertIn('log_x=ttk.Scrollbar(log_frame,orient="horizontal"',source)
        self.assertIn('text="Scroll to start"',source)
        self.assertIn('text="Scroll to latest"',source)
        self.assertIn("xscrollcommand=log_x.set",source)
        self.assertIn("yscrollcommand=log_y.set",source)
        self.assertIn('text="Copy entire log"',source)

    def test_process_status_is_color_coded_but_not_engineering_accepted(self):
        source=self.source
        self.assertIn('"RUNNING":("#155e75","#e0f2fe")',source)
        self.assertIn('"FINISHED":("#166534","#dcfce7")',source)
        self.assertIn('"BLOCKED":("#991b1b","#fee2e2")',source)
        self.assertIn('"MISMATCH":("#991b1b","#fee2e2")',source)
        self.assertIn('"CANCELLED":("#92400e","#fef3c7")',source)
        self.assertIn("PROCESS STATUS ONLY",source)
        self.assertIn("ETABS equivalence not inferred",source)
        self.assertIn("def _set_gravity_operation",self.funcs)

    def test_physics_callbacks_and_analysis_routines_remain_named(self):
        for callback in ("run", "run_both_wall_supports", "_inputs",
                         "_set_gravity_operation", "_export_all_pages"):
            self.assertIn(callback,self.funcs)


if __name__ == "__main__":
    unittest.main()
