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
      # Source-to-result traceability: the native runner defaults to
      # UNASSIGNED/UNSPECIFIED if the generator omits these case keys.
      self.assertEqual(conf["variant_id"],"M0")
      self.assertEqual(conf["pair_id"],"Kobe")
      self.assertEqual(conf["earthquake_event"],"Kobe")
      self.assertEqual(conf["scale"],1.)
      self.assertEqual(conf["analysis_intent"],"RESEARCH_DIAGNOSTIC")
      self.assertTrue(conf["source_records_already_scaled"])
      self.assertFalse(conf["gorkha_processing_reviewed"])
      with self.assertRaises(FileExistsError):
          create_configs(models_json=meta,matched_dir=root,output_dir=dest,source_map=sources)
 def test_duplicate_m0_m6_model_export_is_rejected_without_outputs(self):
    with tempfile.TemporaryDirectory() as d:
      root=Path(d)
      paths={}
      for name in VARIANTS:
        folder=root/"models"/name
        folder.mkdir(parents=True)
        paths[name]=str(folder)
      # M2 could accidentally point to M1 when a converted model
      # directory is reused; without validation, all 224 planned
      # orientations are still generated under misleading labels.
      paths["M2"]=paths["M1"]
      meta=root/"model_dirs.json"
      meta.write_text(json.dumps(paths),encoding="utf-8")
      sources={(evt,c):str(root/(evt.replace(" ","_")+"_"+c+".txt"))
                for evt in EVENT_ORDER for c in ("A","B")}
      out=root/"outputs"
      with self.assertRaisesRegex(ValueError,"distinct model export"):
        create_configs(models_json=meta,matched_dir=root,
                       output_dir=out,source_map=sources)
      self.assertFalse(out.exists())

 def test_explicit_waveform_map_requires_exact_16_distinct_sources(self):
    with tempfile.TemporaryDirectory() as d:
      root=Path(d)
      models={}
      for name in VARIANTS:
        p=root/"models"/name
        p.mkdir(parents=True)
        models[name]=str(p)
      meta=root/"models.json"
      meta.write_text(json.dumps(models),encoding="utf-8")
      sources={(evt,c):str(root/(evt.replace(" ","_")+"_"+c+".txt"))
               for evt in EVENT_ORDER for c in ("A","B")}
      output=root/"out"
      # Reused component would silently give identical excitation data
      # under two different source labels.
      duplicate=dict(sources)
      duplicate[EVENT_ORDER[1],"A"]=duplicate[EVENT_ORDER[0],"A"]
      with self.assertRaisesRegex(ValueError,"distinct waveform"):
        create_configs(models_json=meta,matched_dir=root,
                       output_dir=output,source_map=duplicate)
      self.assertFalse(output.exists())
      # All sixteen event-component assignments must be explicit and exact.
      missing=dict(sources)
      missing.pop((EVENT_ORDER[0],"B"))
      with self.assertRaisesRegex(ValueError,"16.*event/component"):
        create_configs(models_json=meta,matched_dir=root,
                       output_dir=output,source_map=missing)
      extra=dict(sources)
      extra["UNKNOWN","A"]=str(root/"extra.txt")
      with self.assertRaisesRegex(ValueError,"16.*event/component"):
        create_configs(models_json=meta,matched_dir=root,
                       output_dir=output,source_map=extra)
      self.assertFalse(output.exists())

 def test_unknown_model_variant_rejected(self):
    with tempfile.TemporaryDirectory() as d:
      p=Path(d)/"models.json"
      p.write_text(json.dumps({"M0":d}))
      with self.assertRaisesRegex(ValueError,"M0..M6"):
        create_configs(models_json=p,matched_dir=d,output_dir=Path(d)/"out",
          source_map={})
 def test_explicit_empty_source_map_fails_closed_without_scanning_private_files(self):
    with tempfile.TemporaryDirectory() as d:
      root=Path(d)
      models={}
      for name in VARIANTS:
        folder=root/"models"/name
        folder.mkdir(parents=True)
        models[name]=str(folder)
      model_file=root/"model_dirs.json"
      model_file.write_text(json.dumps(models),encoding="utf-8")
      output=root/"generated"
      with patch("components.nonlinear_time_history.soil_c_run_matrix.resolve_sources",
                 side_effect=AssertionError("explicit source_map must not trigger a private directory scan")):
        with self.assertRaisesRegex(ValueError,"source_map must contain"):
          create_configs(models_json=model_file,matched_dir=root,
                         output_dir=output,source_map={})
      self.assertFalse(output.exists())

if __name__=="__main__": unittest.main()
