"""Static regressions for responsive ETABS source conversion GUI.

These tests deliberately do not execute ETABS or touch a source EDB.
They check the GUI's process isolation and worker invocation contracts.
"""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

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

    def test_source_has_single_export_button_binding(self):
        self.assertEqual(self.app_source.count("command=self._run)"), 1)
        self.assertIn("command=self._cancel_conversion", self.app_source)


if __name__ == "__main__":
    unittest.main()
