"""Verify numbered short main launcher preserves existing startup chain."""
import ast
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]


class ShortLauncherTests(unittest.TestCase):
    def test_importing_workflow_launchers_does_not_start_the_gui(self):
        for name in ("01.py", "01_MAIN_GUI.py", "01_WORKFLOW_START.py",
                     "01_START_ETABS_TO_OPENSEES.py"):
            with self.subTest(name=name), patch("runpy.run_path") as launch:
                path = ROOT / name
                exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"),
                     {"__name__": "review_import", "__file__": str(path)})
                launch.assert_not_called()

    def test_failed_spawn_retains_startup_log_and_returns_error(self):
        import RUN_ETABS_TO_OPENSEES as launcher
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(launcher, "ROOT", root), \
                 patch.object(launcher.sys, "argv", ["RUN_ETABS_TO_OPENSEES.py"]), \
                 patch.object(launcher.subprocess, "Popen", side_effect=OSError("worker unavailable")), \
                 patch("tkinter.Tk", side_effect=RuntimeError("display unavailable")):
                self.assertEqual(launcher.main(), 1)
            pointer = root / "Startup_Logs" / "LATEST.txt"
            self.assertIn("worker unavailable", Path(pointer.read_text()).read_text())

    def test_main_tk_callback_preserves_original_exception_in_startup_log(self):
        from components.ui import application

        root = object()
        with TemporaryDirectory() as directory:
            log = Path(directory) / "startup.log"
            with log.open("w", encoding="utf-8") as stream, redirect_stderr(stream), \
                 patch.object(application.os, "environ", {"OPENSEES_STARTUP_LOG": str(log)}), \
                 patch.object(application.messagebox, "showerror", create=True) as dialog:
                try:
                    raise ValueError("invalid model selection")
                except ValueError as exc:
                    application._report_gui_error(root, type(exc), exc, exc.__traceback__)
            self.assertIn("ValueError: invalid model selection", log.read_text())
            self.assertIn(str(log), dialog.call_args.args[1])

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
