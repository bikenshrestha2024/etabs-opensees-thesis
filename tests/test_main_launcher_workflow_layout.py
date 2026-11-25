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
        # Preserve the original launcher set while allowing new, separately
        # tested audit and on-demand actions. The historic fixed count of 41
        # became stale when four valid actions were added to the UI.
        self.assertGreaterEqual(len(self.actions),41)
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
        self.assertIn('previous_workflow_stage',self.code)
        self.assertIn('stage_tabs.select(previous_workflow_stage[0])',self.code)
        for short_tab in ('1. Import','2. Model','3. Gravity / NBC',
                          '4. Linear','5. Nonlinear','6. Materials','7. Results'):
            self.assertIn(short_tab,self.code)

    def test_elastic_settings_shortcut_reuses_bound_gravity_model(self):
        self.assertIn('command=self._open_elastic_comparison_settings',self.code)
        funcs={n.name:n for n in ast.walk(self.tree) if isinstance(n,ast.FunctionDef)}
        shortcut=ast.get_source_segment(self.code,funcs['_open_elastic_comparison_settings'])
        self.assertIn('_open_gravity_analysis(require_manifest=True)',shortcut)
        self.assertIn('_rebuild_verified_clear_beam(elastic_comparison=True)',shortcut)
        gravity=ast.get_source_segment(self.code,funcs['_open_gravity_analysis'])
        self.assertIn('if require_manifest and not bound:',gravity)

    def test_linear_and_nonlinear_launchers_use_selected_folder(self):
        funcs={n.name:n for n in ast.walk(self.tree) if isinstance(n,ast.FunctionDef)}
        for name in ('_open_nbc105_esm','_open_modal_audit',
                     '_open_linear_time_history','_open_nonlinear_time_history'):
            source=ast.get_source_segment(self.code,funcs[name])
            self.assertIn('folder = self._model_review_folder()',source)
            self.assertIn('if folder is None:',source)
        for name,role in (('_open_modal_audit','modal_model_script'),
                          ('_open_linear_time_history','linear_model_script'),
                          ('_open_nonlinear_time_history','nonlinear_model_script')):
            source=ast.get_source_segment(self.code,funcs[name])
            self.assertIn("if not autoselect_inputs(gui, folder, '"+role+"'):",source)
        self.assertIn('ttk.Label(linear_header,textvariable=self.out',self.code)
        self.assertIn('ttk.Label(nonlinear_header,textvariable=self.out',self.code)

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
