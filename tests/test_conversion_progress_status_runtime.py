"""Execute the conversion status expression without ETABS or Tk startup.

Regression for 2026-11-16 TypeError: 'str' object is not callable
at the GUI worker polling callback. Parsing/compiling Python alone misses
adjacent string literal/parenthesized expression call mistakes.
"""
from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


class TestConversionProgressFormatting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (Path(__file__).resolve().parents[1]
                  / "components" / "ui" / "application.py").read_text(
                      encoding="utf-8")
        tree = ast.parse(source)
        app = next(node for node in tree.body
                   if isinstance(node, ast.ClassDef) and node.name == "App")
        callback = next(node for node in app.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "_poll_conversion_worker")
        calls = [node for node in ast.walk(callback)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute)
                 and node.func.attr == "set"
                 and isinstance(node.func.value, ast.Attribute)
                 and node.func.value.attr == "conversion_progress"]
        candidates = [
            node.args[0] for node in calls
            if len(node.args) == 1 and any(
                isinstance(t, ast.Constant)
                and isinstance(t.value, str)
                and "Conversion running:" in t.value
                for t in ast.walk(node.args[0]))
        ]
        if len(candidates) != 1:
            raise AssertionError("Exactly one running progress expression is required")
        cls.code = compile(
            ast.fix_missing_locations(ast.Expression(candidates[0])),
            "<conversion-progress-regression>", "eval")

    def test_active_conversion_short_silence(self):
        obj = SimpleNamespace(_conversion_stage="ETABS model assembly")
        status = eval(self.code, {"getattr": getattr},
                      {"self": obj, "elapsed": 50, "silent": 7})
        self.assertIn("Conversion running: 50s", status)
        self.assertIn("ETABS model assembly", status)
        self.assertIn("last worker log 7s ago", status)
        self.assertIn("Mesh assembly", status)

    def test_long_silence_displays_recovery_hint_without_crashing(self):
        obj = SimpleNamespace(_conversion_stage="ETABS COM: OpenFile")
        status = eval(self.code, {"getattr": getattr},
                      {"self": obj, "elapsed": 1148, "silent": 1125})
        self.assertIn("ETABS COM: OpenFile", status)
        self.assertIn("No worker progress for over 2 min", status)
        self.assertIsInstance(status, str)


if __name__ == "__main__":
    unittest.main()
