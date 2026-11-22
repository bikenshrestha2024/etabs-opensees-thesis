"""TDD for exact-case ESM exports and shared 32/76/97 physical support contract.

No solver, native ETABS or private model required. [REF docs/superpowers/plans/2026-11-22-esm-support-and-storey-mass-audit.md]
"""
import json
import tempfile
import unittest
from pathlib import Path

from components.equivalent_static.organized_exports import build_combined_esm_export
from components.model.support_case_contract import select_support_case, normalize_support_case

PHYSICAL=(1,2,3,4,5,6,7,8,13,14,23,24,25,26,35,36,
          41,42,51,52,53,54,63,64,69,70,71,72,73,74,75,76)


class CaseContractTests(unittest.TestCase):
    def setUp(self):
        self.original={str(i):[1,1,1,1,1,1] for i in range(1,77)}
        self.data={"supports":self.original, "added_wall_mesh_support_tags":[]}
    def test_default_32_preserves_exact_project_supported_tags(self):
        item=select_support_case(self.data,{},None)
        self.assertEqual(item["profile"],"PHYSICAL_32")
        self.assertEqual(set(map(int,item["supports"])),set(PHYSICAL))
        self.assertEqual(len(item["supports"]),32)
        self.assertEqual(len(item["excluded_mesh_point_tags"]),44)
        self.assertEqual(len(self.data["supports"]),76)
        self.assertEqual(item["engineering_acceptance"],"NOT_VERIFIED")
    def test_opt_in_diagnostic_76_source_supports(self):
        item=select_support_case(self.data,{},"SOURCE_76")
        self.assertEqual(item["profile"],"SOURCE_76")
        self.assertEqual(len(item["supports"]),76)
        self.assertIn("DIAGNOSTIC",item["purpose"])
    def test_97_is_explicit_and_requires_native_source_provenance(self):
        with self.assertRaisesRegex(ValueError,"97|extension|topology"):
            select_support_case(self.data,{},"WALL_BASE_97")
    def test_invalid_profile_and_missing_physical_tag_fail_closed(self):
        with self.assertRaises(ValueError):normalize_support_case("default_guess")
        self.data["supports"].pop("76")
        with self.assertRaisesRegex(ValueError,"32|physical|missing"):
            select_support_case(self.data,{},"PHYSICAL_32")


class ESMExportCaseDiscovery(unittest.TestCase):
    def test_exact_project_stage_case_discovered_for_saved_solver(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)
            output=project/"OpenSees_Analysis_Results"/"ULS_Project_ABC"
            output.mkdir(parents=True)
            (output/"NBC105_ESM_Storey_Forces_ULS_X+_E0_V111.csv").write_text(
                "story_number,force\n1,5\n",encoding="utf8")
            source=project/"03_ESM"/"RUNS"/"ULS"/output.name
            source.mkdir(parents=True)
            doc={"response_case":"ULS_X+_E0","limit_state":"ULS",
                 "period_s":1.5,"total_seismic_weight_kN":100.,
                 "base_shear_kN":20.,"period_exponent_k":1.6,
                 "stories":[{"story_name":"1F","story_number":1,"height_m":3.8,
                             "seismic_weight_kN":100.,"lateral_force_kN":20.,
                             "master_node_tag":14511}]}
            (source/"NBC105_ESM_Calculation_ULS_X+_E0_V111.json").write_text(
                json.dumps(doc),encoding="utf8")
            out=build_combined_esm_export(output)
            self.assertEqual(out["cases"],1)
            self.assertEqual(out["calculation_status"],"CALCULATION_JSON_AVAILABLE")
            self.assertTrue(Path(out["zip"]).exists())
    def test_without_calculation_json_explicit_manifest_only_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"NBC105_ESM_Storey_Forces_ULS_X+_E0_V111.csv").write_text(
                "story_number,force\n1,5\n",encoding="utf8")
            with self.assertRaisesRegex(ValueError,"no calculation JSON"):
                build_combined_esm_export(root)
            out=build_combined_esm_export(root,allow_incomplete=True)
            self.assertEqual(out["cases"],0)
            self.assertEqual(out["calculation_status"],"NO_CALCULATION_JSON")
            self.assertTrue(Path(out["zip"]).is_file())
            self.assertTrue(Path(out["workbook"]).is_file())

if __name__=="__main__":
    unittest.main()
