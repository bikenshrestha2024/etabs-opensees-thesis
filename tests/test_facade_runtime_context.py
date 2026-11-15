"""Root facade and direct components module must resolve same code/project root.

This test extracts the real source helper from the affected active modules,
then exercises direct-import, root compatibility facade and exported-runtime
paths without importing ETABS, OpenSees or creating a GUI.
"""
from __future__ import annotations

import ast
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODULES={
    "components/inputs/analysis_autofill.py":"OpenSees_Linear_Autofill_V124.py",
    "components/response_spectrum/model_analysis.py":"OpenSees_Model_Response_Spectrum_V132.py",
    "components/ui/building_exploratory_gui.py":"OpenSees_Building_Exploratory_GUI_V138.py",
    "components/gravity/gui_and_reports.py":"OpenSees_Gravity_GUI_V110.py",
    "components/inputs/project_workbooks.py":"OpenSees_Project_Inputs_V123.py",
    "components/model/assembly.py":"OpenSees_Complete_Export_V118.py",
    "components/modal/gui_and_reports.py":"OpenSees_Modal_GUI_NBC105_V111.py",
    "components/validation/irregularity_review.py":"OpenSees_Irregularity_Review_V134.py",
    "components/ui/literature_demo_gui.py":"OpenSees_Literature_Demo_GUI_V137.py",
    "components/ui/window_manager.py":"OpenSees_Window_Manager_V129.py",
}


def isolated_root_function(source):
    tree=ast.parse(Path(source).read_text(encoding="utf-8-sig"))
    funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef)
           and n.name=="_runtime_repo_root"]
    if len(funcs)!=1:
        raise AssertionError("Exactly one context resolver expected: "+str(source))
    module=ast.fix_missing_locations(ast.Module(body=funcs,type_ignores=[]))
    return compile(module,str(source),"exec")


class FacadeContextTests(unittest.TestCase):
    def test_direct_root_facade_and_exported_runtime_paths_match(self):
        for rel,alias in MODULES.items():
            with self.subTest(component=rel):
                actual=ROOT/rel
                facade=ROOT/alias
                self.assertTrue(actual.is_file())
                self.assertTrue(facade.is_file())
                func=isolated_root_function(actual)
                for label,globals_for_case in (
                    ("direct", {"__file__":str(actual)}),
                    ("facade", {"__file__":str(facade),
                                "_component_source":str(actual)}),
                ):
                    env={"Path":Path,**globals_for_case}
                    exec(func,env)
                    self.assertEqual(env["_runtime_repo_root"](),ROOT,
                                     (rel,label))
                with tempfile.TemporaryDirectory() as td:
                    runtime=Path(td)/"Export"/"OpenSees_Runtime_V118"
                    target=runtime/rel
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_text("# synthetic\n",encoding="utf-8")
                    facade_copy=runtime.parent/alias
                    facade_copy.write_text("# synthetic root alias\n",encoding="utf-8")
                    env={"Path":Path,"__file__":str(facade_copy),
                         "_component_source":str(target)}
                    exec(func,env)
                    self.assertEqual(env["_runtime_repo_root"](),runtime)

    def test_existing_aliases_keep_exec_facade_contract(self):
        for rel,alias in MODULES.items():
            source=(ROOT/alias).read_text(encoding="utf-8-sig")
            with self.subTest(facade=alias):
                self.assertIn("_component_source",source)
                self.assertIn("exec(compile(",source)


if __name__=="__main__":
    unittest.main()
