"""Regression checks for new ESM stage writers and non-destructive repair."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.project_workbooks import analysis_output_folder
from components.inputs.output_layout import canonical_stage_folder


def _load_tool():
    root=Path(__file__).resolve().parents[1]
    file=root/"tools"/"repair_project_output_layout.py"
    spec=importlib.util.spec_from_file_location("repair_project_output_layout",file)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StageOwnedESMTests(unittest.TestCase):
    def test_default_legacy_is_preserved_explicit_esm_is_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            old=analysis_output_folder(root,"ULS")
            new=analysis_output_folder(root,"ULS",stage="ESM")
            self.assertEqual(old.parent,root/"OpenSees_Analysis_Results")
            self.assertEqual(new.parent,root/"03_ESM"/"RUNS")
            self.assertEqual(old.name,new.name)
            self.assertEqual(canonical_stage_folder("ESM"),"03_ESM")
            self.assertEqual(analysis_output_folder(root,"ULS",stage="LEGACY"),old)
            self.assertEqual(analysis_output_folder(root,"Both",stage="ESM").parent,
                             root/"03_ESM"/"RUNS")
            with self.assertRaisesRegex(ValueError,"stage"):
                analysis_output_folder(root,"ULS",stage="UNKNOWN")

    def test_legacy_mirror_is_hash_verified_and_non_destructive(self):
        tool=_load_tool()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            folder=root/"OpenSees_Analysis_Results"/"ULS_Floor_3_Test"
            folder.mkdir(parents=True)
            esm=folder/"NBC105_ESM_Calculation_ULS_X_E0_V111.json"
            esm.write_text('{"period_s": 2.0}',encoding="utf-8")
            ray=folder/"NBC105_Rayleigh_Preliminary_V127.json"
            ray.write_text('{"X": 1, "Y": 2}',encoding="utf-8")
            other=folder/"Gravity_Standards.json"
            other.write_text('{"gravity": true}',encoding="utf-8")
            loose=root/"OpenSees_Complete_Model_Data_V118.json"
            loose.write_text('{"source": 1}',encoding="utf-8")
            planned=tool.repair_layout(root)
            self.assertEqual(planned["status"],"DRY_RUN_NO_CHANGES")
            self.assertEqual(planned["historical_esm_mirror_files"],2)
            self.assertFalse((root/"03_ESM").exists())
            actual=tool.repair_layout(root,apply=True)
            self.assertEqual(actual["status"],"APPLIED_SAFE_COPIES_NO_SOURCE_MOVE")
            mirror=root/"03_ESM"/"REVIEW_SNAPSHOTS"/"HISTORICAL_ULS_Floor_3_Test"
            self.assertEqual((mirror/esm.name).read_bytes(),esm.read_bytes())
            self.assertEqual((mirror/ray.name).read_bytes(),ray.read_bytes())
            self.assertFalse((mirror/other.name).exists())
            self.assertTrue(esm.is_file())
            self.assertTrue(other.is_file())
            self.assertTrue(loose.is_file())
            self.assertTrue((root/"01_ETABS_EXPORT").is_dir())
            self.assertTrue((root/"03_ESM"/"REVIEW_SNAPSHOTS"/"LAYOUT_REPAIR_MANIFEST.json").is_file())
            again=tool.repair_layout(root,apply=True)
            self.assertEqual(again["historical_esm_mirror_files"],2)
            self.assertTrue(all(x.get("copy_status")=="EXISTING_IDENTICAL" for x in again["items"]))

    def test_hash_conflict_refuses_second_copy_without_replacing_source(self):
        tool=_load_tool()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            folder=root/"OpenSees_Analysis_Results"/"ULS_Floor_3_Test"
            folder.mkdir(parents=True)
            item=folder/"NBC105_ESM_test.json"
            item.write_text('{"a":1}',encoding="utf-8")
            tool.repair_layout(root,apply=True)
            target=root/"03_ESM"/"REVIEW_SNAPSHOTS"/"HISTORICAL_ULS_Floor_3_Test"/item.name
            target.write_text('{"a":9}',encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"collision"):
                tool.repair_layout(root,apply=True)
            self.assertEqual(item.read_text(encoding="utf-8"),'{"a":1}')
            self.assertEqual(target.read_text(encoding="utf-8"),'{"a":9}')


if __name__=="__main__":
    unittest.main()
