"""TDD contract: NLTHA retains source topology, literature assignments and real 32-support reactions.

These tests are deliberately solver-free: native E-SFI wall time histories remain separate
from source/step orchestration and require the user's local OpenSeesPy/XARA.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.nonlinear_time_history.source_model_handoff import (
    stage_existing_model_sources, solver_reaction_support_tags, literature_section_inventory
)
from components.nonlinear_time_history.direct_existing_model import (
    make_research_nltha_config, preflight_existing_model
)
from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32

REQUIRED = (
    "OpenSees_Complete_Model_Data_V118.json",
    "OpenSees_Complete_Model_Config_V118.json",
    "OpenSees_Complete_Export_Report_V118.json",
    "OpenSees_Load_Conversion_Audit.json",
    "OpenSees_Source_Model_Metadata_V118.json",
    "OpenSees_Element_Connectivity.json",
)


class ExistingModelNLTHATests(unittest.TestCase):
    def _source(self,root):
        root.mkdir(parents=True,exist_ok=True)
        for p in REQUIRED:
            (root/p).write_bytes(("EXACT SOURCE "+p+"\\n").encode())
        return root

    def test_stage_retains_connectivity_and_bytewise_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);src=self._source(p/"source");dst=p/"run"/"isolated_model"
            fingerprints=stage_existing_model_sources(src,dst)
            self.assertEqual(set(fingerprints),set(REQUIRED))
            for filename in REQUIRED:
                self.assertEqual((src/filename).read_bytes(),(dst/filename).read_bytes())
                self.assertEqual(fingerprints[filename],hashlib.sha256((src/filename).read_bytes()).hexdigest())

    def test_missing_connectivity_fails_before_running_any_solver(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);src=self._source(p/"source")
            (src/"OpenSees_Element_Connectivity.json").unlink()
            with self.assertRaisesRegex(FileNotFoundError,"OpenSees_Element_Connectivity"):
                stage_existing_model_sources(src,p/"out")
            self.assertFalse((p/"out").exists())

    def test_real_reaction_set_is_from_live_solver_not_76_source_rows(self):
        primary=sorted(PROJECT_PRIMARY_32)
        report={"gravity_base_support_tags":primary,
                "support_case_evidence":{"profile":"PHYSICAL_32"}}
        source=[*primary,*range(200,244)]
        self.assertEqual(len(source),76)
        got=solver_reaction_support_tags(report,"PHYSICAL_32")
        self.assertEqual(got,primary)
        self.assertEqual(len(got),32)

    def test_wrong_solver_support_case_is_rejected_before_reaction_recording(self):
        report={"gravity_base_support_tags":[*PROJECT_PRIMARY_32,*range(200,244)],
                "support_case_evidence":{"profile":"SOURCE_76"}}
        with self.assertRaisesRegex(ValueError,"PHYSICAL_32"):
            solver_reaction_support_tags(report,"PHYSICAL_32")

    def test_section_inventory_reports_actual_geometry_and_noncalibrated_literature(self):
        data={"frames":[
            {"category":"BEAM","properties":{"section":"Beam 600*800"}},
            {"category":"COLUMN","properties":{"section":"Col 1100*1100"}}],
            "shells":[{"category":"SHEAR WALL","properties":{
                "property":"Wall 600","material":"M45","thickness":0.6}}]}
        cfg={"frame_section_mapping":{
            "Beam 600*800":"RC_BEAM_600x800_FIBER",
            "Col 1100*1100":"RC_COLUMN_1100x1100_FIBER"},
            "nonlinear_parameters_reviewed":False,
            "nonlinear_materials_file":"",
            "nonlinear_wall_fsam_tags":{}}
        result=literature_section_inventory(data,cfg)
        self.assertEqual(result["status"],"RESEARCH_TEMPLATE_UNCALIBRATED")
        self.assertEqual(result["frame_sections"]["Beam 600*800"]["member_count"],1)
        self.assertEqual(result["wall_properties"]["Wall 600"]["thickness_m"],0.6)
        self.assertFalse(result["project_materials_calibrated"])

    def test_nonexistent_source_frame_mapping_fails_closed(self):
        data={"frames":[{"category":"BEAM","properties":{"section":"UNKNOWN RC"}}],"shells":[]}
        with self.assertRaisesRegex(ValueError,"UNKNOWN RC"):
            literature_section_inventory(data,{"frame_section_mapping":{}})

    def test_direct_config_is_xy_yx_nonlinear_walls_source_supports_and_full_record(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);src=p/"model";out=p/"output"
            cfg=make_research_nltha_config(
                model_folder=src,x_path=p/"Kobe_A.txt",
                y_path=p/"Kobe_B.txt",output_dir=out,
                event="Kobe",variant_id="M4")
            self.assertEqual(cfg["orientations"],["XY","YX"])
            self.assertTrue(cfg["nonlinear_walls"])
            self.assertEqual(cfg["material_basis"],"PEER_2015_12_SINGLE_SOURCE")
            self.assertEqual(cfg["support_case"],"PHYSICAL_32")
            self.assertEqual(cfg["diagnostic_excitation"],"XY")
            self.assertEqual(cfg["analysis_intent"],"RESEARCH_DIAGNOSTIC")
            self.assertEqual(cfg["duration_s"],0.)
            self.assertEqual(cfg["scale"],1.)
            self.assertTrue(cfg["soil_c_primary_nltha"], "Direct primary thesis run must verify registered Soil-C pair by SHA256")
            self.assertFalse(cfg.get("approved_for_thesis",False))

    def test_missing_waveforms_cannot_be_reported_as_run_completion(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);src=self._source(p/"source")
            cfg=make_research_nltha_config(model_folder=src,
                x_path=p/"missingA.txt",y_path=p/"missingB.txt",
                output_dir=p/"results",event="Kobe",variant_id="UNVERIFIED")
            with self.assertRaisesRegex(FileNotFoundError,"missingA"):
                preflight_existing_model(cfg)


if __name__=="__main__":
    unittest.main()
