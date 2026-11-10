"""Synthetic read-only native ETABS EQ exporter tests, no ETABS needed."""
import csv
from contextlib import ExitStack
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from components.validation import etabs_eq_pdelta_native_extract as module

class ETABSEQNativeTests(unittest.TestCase):
    def test_existing_cases_and_all_steps_no_analysis_run(self):
        restore=[]
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            stack.enter_context(patch.object(module,"_snapshot",return_value={"units":6}))
            stack.enter_context(patch.object(module,"_db_display_snapshot",
                return_value={"cases":["Dead"],"combos":[],"combos_available":True}))
            stack.enter_context(patch.object(module,"_db_select_case",
                return_value=None))
            stack.enter_context(patch.object(module,"_db_restore",
                return_value=None))
            stack.enter_context(patch.object(module,"_names",return_value=[
                "Dead","EQX","EQY","EQX+ P Delta Initial",
                "EQX+ P-Delta","EQY+ P Delta Initial","EQY+ P-Delta"]))
            select=stack.enter_context(patch.object(module,"_select"))
            stack.enter_context(patch.object(module,"_base",side_effect=lambda sap,case:[
                dict(LoadCase=case,StepType="Step",StepNum=1,FZ=10.),
                dict(LoadCase=case,StepType="Step",StepNum=2,FZ=20.)]))
            stack.enter_context(patch.object(module,"_table_catalog",return_value=[
                {"key":"Story Shears","name":"Story Shears"}]))
            stack.enter_context(patch.object(module,"_get_native_table",return_value=(
                ["Story","Output Case","Vx"],[["Story1","EQX","10"]])))
            stack.enter_context(patch.object(module,"_restore",
                side_effect=lambda *_:restore.append(True)))
            result=module.export_eq_pdelta_native_evidence(SimpleNamespace(LoadCases=object()),tmp)
            self.assertEqual(result["selected_case_count"],6)
            self.assertEqual(len(restore),1)
            self.assertEqual(select.call_count,6)
            self.assertEqual(result["failed_case_or_table_queries"],0)
            files=list(Path(tmp).glob("base_*.csv"))
            self.assertEqual(len(files),6)
            with files[0].open(encoding="utf-8-sig") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))),2)
            self.assertTrue((Path(tmp)/"ETABS_EQ_PDELTA_NATIVE_INDEX.json").is_file())

    def test_selection_always_restored_on_catalog_failure(self):
        restored=[]
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            stack.enter_context(patch.object(module,"_snapshot",return_value={"units":6}))
            stack.enter_context(patch.object(module,"_names",return_value=["EQX"]))
            stack.enter_context(patch.object(module,"_table_catalog",
                side_effect=RuntimeError("CSI API failed")))
            stack.enter_context(patch.object(module,"_restore",
                side_effect=lambda *_:restored.append(True)))
            with self.assertRaisesRegex(RuntimeError,"CSI API failed"):
                module.export_eq_pdelta_native_evidence(SimpleNamespace(LoadCases=object()),tmp)
            self.assertEqual(restored,[True])

if __name__=="__main__":
    unittest.main()
