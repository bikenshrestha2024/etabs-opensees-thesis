"""Stage 36: seven model variants x eight events x two states configuration test."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from components.nonlinear_time_history.soil_c_run_matrix import (
    create_configs, VARIANTS, STATES
)
from components.nonlinear_time_history.soil_c_nltha_suite import EVENT_ORDER

class RunMatrixTests(unittest.TestCase):
 def test_unexecuted_matrix_and_case_order(self):
    with tempfile.TemporaryDirectory() as d:
      root=Path(d)
      models={}
      for name in VARIANTS:
        p=root/"models"/name
        p.mkdir(parents=True)
        models[name]=str(p)
      meta=root/"model_dirs.json"
      meta.write_text(json.dumps(models),encoding="utf-8")
      sources={(evt,c):str(root/(evt.replace(" ","_")+"_"+c+".txt"))
                for evt in EVENT_ORDER for c in ("A","B")}
      dest=root/"generated"
      r=create_configs(models_json=meta,matched_dir=root,
                       output_dir=dest,source_map=sources)
      self.assertEqual(r["configs_generated"],112)
      self.assertEqual(r["intended_total_analyses"],224)
      self.assertFalse(r["all_materials_and_wall_geometry_approved"])
      p=dest/"configs"/"M0"/"ULS"/"Kobe.json"
      conf=json.loads(p.read_text())
      self.assertEqual(conf["orientations"],["XY","YX"])
      self.assertEqual(conf["scale"],1.)
      self.assertEqual(conf["analysis_intent"],"RESEARCH_DIAGNOSTIC")
      self.assertTrue(conf["source_records_already_scaled"])
      self.assertFalse(conf["gorkha_processing_reviewed"])
      with self.assertRaises(FileExistsError):
          create_configs(models_json=meta,matched_dir=root,output_dir=dest,source_map=sources)
 def test_unknown_model_variant_rejected(self):
    with tempfile.TemporaryDirectory() as d:
      p=Path(d)/"models.json"
      p.write_text(json.dumps({"M0":d}))
      with self.assertRaisesRegex(ValueError,"M0..M6"):
        create_configs(models_json=p,matched_dir=d,output_dir=Path(d)/"out",
          source_map={})
if __name__=="__main__": unittest.main()
