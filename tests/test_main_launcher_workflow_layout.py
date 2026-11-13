"""Static safety for the native Tk main-launcher reorganization.

No ETABS/COM/OpenSees imports or GUI display required.
[REF docs/source/tests/test_main_launcher_workflow_layout.py.md]
"""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"components/ui/application.py"


class LauncherWorkflowLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=SRC.read_text(encoding="utf-8")
        cls.tree=ast.parse(cls.code,filename=str(SRC))
        cls.actions=[node for node in ast.walk(cls.tree)
                     if isinstance(node,ast.Call) and
                     isinstance(node.func,ast.Name) and node.func.id=="action"]

    def test_all_legacy_launchers_preserved_once(self):
        # 41 separate source actions; dynamic saved-view loop produces four.
        self.assertEqual(len(self.actions),41)
        for method in ("_show_last_exports","_open_section_mapping",
                       "_open_gravity_analysis","_open_nbc105_esm",
                       "_open_modal_audit","_open_linear_time_history",
                       "_open_nonlinear_time_history","_open_nonlinear_readiness",
                       "_open_result_interpretation","_open_area_integration",
                       "_open_spectrum_diagnostics"):
            self.assertEqual(self.code.count("command=self."+method),1)
        for name in ("OpenSees_Workflow_V144","OpenSees_Load_Path_V141",
                     "OpenSees_Model_Response_Spectrum_V132",
                     "OpenSees_Wall_Validation_V147"):
            self.assertIn(name,self.code)

    def test_stage_navigation_search_and_grouping(self):
        for label in ("Import & audit","Build the model","Gravity & NBC setup",
                      "Linear analysis","Nonlinear analysis",
                      "Material laboratory","Review & results"):
            self.assertIn(label,self.code)
        self.assertIn("stage_tabs=ttk.Notebook(shell)",self.code)
        self.assertIn("workflow_search.trace_add",self.code)
        self.assertIn("command=original.invoke",self.code)
        self.assertNotIn('columns=ttk.Frame(shell); columns.pack(',self.code)
        self.assertIn('if not matches:',self.code)

    def test_log_keeps_copy_and_two_axes_of_scrolling(self):
        for item in ('orient="vertical",command=self.logbox.yview',
                     'orient="horizontal",command=self.logbox.xview',
                     'xscrollcommand=sx.set','yscrollcommand=sb.set',
                     'text="Copy log"','text="Scroll to start"',
                     'text="Scroll to latest"'):
            self.assertIn(item,self.code)

    def test_source_export_commands_untouched(self):
        for snippet in ("command=self._run)",
                        "command=self._rebuild_complete_export)",
                        "command=self._browse_file)",
                        "command=self._browse_dir)",
                        "variable=self.include_live"):
            self.assertIn(snippet,self.code)
        self.assertIn("ETABS is closed without saving",self.code)


if __name__=="__main__":
    unittest.main()
