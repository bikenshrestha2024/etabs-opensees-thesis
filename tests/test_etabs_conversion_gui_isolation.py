"""Static regressions for responsive ETABS source conversion GUI.

These tests deliberately do not execute ETABS or touch a source EDB.
They check the GUI's process isolation and worker invocation contracts.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "components/ui/application.py"
WORKER = ROOT / "tools/etabs_conversion_worker.py"


def method(cls, name):
    return next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == name)


class TestConversionGuiIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_source = APP.read_text(encoding="utf-8")
        cls.worker_source = WORKER.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.app_source)
        cls.worker_tree = ast.parse(cls.worker_source)
        cls.gui_cls = next(x for x in cls.tree.body
                           if isinstance(x, ast.ClassDef) and x.name == "App")

    def test_gui_conversion_callback_starts_child(self):
        run = method(self.gui_cls, "_run")
        self.assertTrue(any(
            isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
            and x.func.attr == "Popen" for x in ast.walk(run)
        ))
        self.assertFalse(any(
            isinstance(x, ast.Call) and isinstance(x.func, ast.Name)
            and x.func.id == "convert_model" for x in ast.walk(run)
        ))

    def test_gui_does_not_use_thread_for_etabs_com(self):
        run = method(self.gui_cls, "_run")
        self.assertFalse(any(
            isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
            and x.func.attr in ("Thread", "join", "communicate", "wait")
            for x in ast.walk(run)
        ))
        self.assertIn("self.root.after(250, self._poll_conversion_worker)",
                      self.app_source)

    def test_worker_logs_and_cancellation_available(self):
        self.assertIn("def _poll_conversion_worker(self)", self.app_source)
        self.assertIn("def _cancel_conversion(self)", self.app_source)
        self.assertIn("def main() -> int:", self.worker_source)
        self.assertIn("convert_model(str(edb), str(output), log, include_live)",
                      self.worker_source)
        self.assertIn("model_equivalence", self.worker_source)
        self.assertIn("NOT_VERIFIED", self.worker_source)

    def test_worker_resolves_from_compiled_module_not_legacy_launcher(self):
        run = method(self.gui_cls, "_run")
        # The facade may execute compiled implementation with a different
        # global __file__. Only the callable's code origin is reliable.
        snippet = ast.get_source_segment(self.app_source, run)
        self.assertIn("type(self)._run.__code__.co_filename", snippet)
        self.assertIn('repo_root / "tools" / "etabs_conversion_worker.py"', snippet)
        self.assertIn('cmd, cwd=str(repo_root)', snippet)
        self.assertNotIn('worker = Path(__file__).resolve().parents[2]', snippet)

    def test_exec_facade_preserves_implementation_code_filename(self):
        with __import__("tempfile").TemporaryDirectory() as td:
            real_source = Path(td) / "repo" / "components" / "ui" / "application.py"
            real_source.parent.mkdir(parents=True)
            real_source.write_text(
                "class Dummy:\n"
                "    def _run(self):\n"
                "        return __file__\n",
                encoding="utf-8",
            )
            namespace = {"__file__": str(Path(td) / "launcher.py")}
            exec(compile(real_source.read_text(), str(real_source), "exec"),
                 namespace, namespace)
            instance = namespace["Dummy"]()
            self.assertEqual(instance._run(), namespace["__file__"])
            self.assertEqual(
                Path(type(instance)._run.__code__.co_filename).resolve(),
                real_source.resolve(),
            )

    def test_import_root_guard_precedes_first_output_write(self):
        snippet=ast.get_source_segment(self.app_source,method(self.gui_cls,"_run"))
        self.assertLess(snippet.index("require_import_root(output)"),snippet.index("output.mkdir"))
        self.assertLess(self.worker_source.index("require_import_root(output)"),self.worker_source.index("output.mkdir"))

    def test_selected_project_tools_use_shared_boundary(self):
        from components.ui import application
        gui=Mock()
        gui._model_review_folder.return_value=None
        with patch("importlib.import_module") as load:
            self.assertIsNone(application.App._launch_selected_tool(gui,"example"))
            load.assert_not_called()
        gui._model_review_folder.return_value="selected"
        with patch("importlib.import_module") as load:
            application.App._launch_selected_tool(gui,"example","launch_response_viewer",path_arg=True)
            load.return_value.launch_response_viewer.assert_called_once_with(gui.root,Path("selected"))

    def test_source_has_single_export_button_binding(self):
        self.assertEqual(self.app_source.count("command=self._run)"), 1)
        self.assertIn("command=self._cancel_conversion", self.app_source)

    def test_completed_export_view_remains_bound_to_the_worker_folder(self):
        from components.ui import application

        with TemporaryDirectory() as directory:
            original = Path(directory) / 'original'
            current = Path(directory) / 'different_selection'
            worker_log = original / '09_SOFTWARE_DIAGNOSTICS' / 'worker.log'
            worker_log.parent.mkdir(parents=True)
            result = {'report': str(original / 'OpenSees_Complete_Export_Report_V118.json'),
                      'assembly_errors': [], 'categorized_mirror': {'status': 'completed'}}
            worker_log.write_text('[WORKER_RESULT] ' + json.dumps(result), encoding='utf-8')
            gui = Mock()
            gui.out.get.return_value = str(current)
            gui._conversion_process.poll.return_value = 0
            gui._conversion_log_file = worker_log
            gui._conversion_log_offset = 0
            gui._conversion_started_at = 0
            gui._conversion_last_activity = 0
            gui._conversion_cancel_requested = False
            with patch.object(application.messagebox, 'showinfo'):
                application.App._poll_conversion_worker(gui)
            self.assertEqual(Path(gui._last_exports[1]).parent, original)
            self.assertIn('Review the model', gui.conversion_progress.set.call_args.args[0])
            gui.out.set.assert_not_called()


if __name__ == "__main__":
    unittest.main()
