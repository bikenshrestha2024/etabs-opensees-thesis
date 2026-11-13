"""Verify numbered short main launcher preserves existing startup chain."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class ShortLauncherTests(unittest.TestCase):
    def test_main_alias_runs_numbered_entry_only(self):
        src=(ROOT/"01_MAIN_GUI.py").read_text(encoding="utf-8")
        ast.parse(src)
        self.assertIn('with_name("01.py")',src)
        self.assertIn('run_name="__main__"',src)

    def test_original_startup_chain_unchanged(self):
        self.assertIn("RUN_ETABS_TO_OPENSEES.py",(ROOT/"01.py").read_text(encoding="utf-8"))
        startup=(ROOT/"RUN_ETABS_TO_OPENSEES.py").read_text(encoding="utf-8")
        self.assertIn("ETABS_to_OpenSeesPy_Section_Review_V116_NBC105_Area_NLTHA.py",startup)
        self.assertIn("Startup_Logs",startup)
        self.assertTrue((ROOT/"01_WORKFLOW_START.py").is_file())
        self.assertTrue((ROOT/"docs/programs/01_MAIN_GUI.md").is_file())


if __name__=="__main__":
    unittest.main()
