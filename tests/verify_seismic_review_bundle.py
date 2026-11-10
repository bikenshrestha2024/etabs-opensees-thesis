"""Local read-only ESM/MRSM ZIP and lossless dedup regression."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from components.validation.seismic_review_bundle import bundle_seismic_review


class SeismicReviewBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.src=self.root/"model";self.src.mkdir()
        self.out=self.root/"output";self.out.mkdir()
        (self.src/"OpenSees_Complete_Model_Config_V118.json").write_text(
            '{"etabs_beam_weight_policy":"ETABS_BEAM_CLEAR_LENGTH"}')
        (self.src/"OpenSees_Complete_Model_Data_V118.json").write_text(
            '{"nodes":{},"supports":{}}')
        (self.src/"OpenSees_Source_Model_Metadata_V118.json").write_text(
            '{"model":"synthetic"}')
        (self.out/"NBC105_ESM_Force_Profile_ULS_X+_E0_V111.json").write_text(
            '{"force_kN":25}')
        (self.out/"NBC105_ESM_Force_Profile_ULS_Y+_E0_V111.json").write_text(
            '{"force_kN":25}')
        (self.out/"ULTIMATE_ETABS_LINKED_ESM.xlsx").write_bytes(b"sample native reference")
        (self.out/"MRSM_ULS").mkdir()
        (self.out/"MRSM_ULS"/"MRSM_Results_V132.json").write_text(
            '{"ULS_X_E0":{"base_shear_kN":22.5}}')

    def test_esm_exact_bytes_deduplicated_restorable(self):
        r=bundle_seismic_review(self.src,self.out,method="ESM")
        assert Path(r["zip"]).is_file()
        with zipfile.ZipFile(r["zip"]) as archive:
            names=archive.namelist()
            self.assertTrue(any(n.startswith("ETABS_Linked/") for n in names))
            self.assertTrue(any(n.startswith("OpenSees_Direct/") for n in names))
            self.assertIn("Comparisons/ETABS_OpenSees_Response_Check_Template.xlsx",names)
            self.assertIn("REVIEW_MANIFEST.json",names)
            manifest=json.loads(archive.read("REVIEW_MANIFEST.json"))
            self.assertEqual(manifest["validation"],"NOT_STRUCTURALLY_CERTIFIED")
            self.assertGreaterEqual(manifest["deduplicated_alias_count"],1)
            for duplicate in manifest["duplicates"]:
                self.assertEqual(duplicate["sha256"],
                    hashlib.sha256(archive.read(duplicate["same_content_as"])).hexdigest())
            self.assertFalse(manifest["independent_ETABS_response_verified"])
        self.assertTrue(Path(r["folder"]).is_dir())

    def test_current_hash_verified_esm_story_and_node_rows_only(self):
        import csv
        from components.validation.etabs_comparison import collect
        model=self.src/"OpenSees_Complete_Model_Data_V118.json"
        digest=hashlib.sha256(model.read_bytes()).hexdigest()
        (self.src/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"source_edb":"D:/Thesis/ULTIMATE LOAD - TEST.EDB",
                        "node_map":[{"opensees_node_tag":1,
                                     "etabs_point_name":"P-1"}]}))
        response=self.out/"NBC105_ESM_OpenSees_Response_ULS_X+_E0.json"
        response.write_text(json.dumps([{"story_number":3,"height_m":11.2,
            "response_case":"ULS_X+_E0","U_design_m":.002,
            "design_drift_ratio":.0003,"story_shear_kN":3000.}]))
        meta=self.out/"NBC105_ESM_OpenSees_Response_META_ULS_X+_E0.json"
        meta.write_text(json.dumps({"model_sha256":digest,
            "limit_state":"ULS","axis":"X","response_case":"ULS_X+_E0"}))
        node=self.out/"NBC105_ESM_All_Node_Displacements_ULS_X+_E0.csv"
        with node.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=["opensees_node_tag",
                "etabs_point_name","model_sha256","limit_state","response_case",
                "du_x_m","design_du_x_m"])
            writer.writeheader()
            writer.writerow({"opensees_node_tag":1,"etabs_point_name":"P-1",
                "model_sha256":digest,"limit_state":"ULS",
                "response_case":"ULS_X+_E0","du_x_m":.001,
                "design_du_x_m":.002})
        issues=[]
        before=collect(self.src,issues,results_root=self.out)
        self.assertTrue(any(x["metric"]=="displacement" and
            x["location"]=="P-1" and x["basis"]=="static_elastic_increment"
            for x in before))
        self.assertTrue(any(x["metric"]=="story_shear" and
            x["basis"]=="applied_floor_force_cumulative_NOT_recovered"
            for x in before))
        self.assertFalse(any(x["metric"]=="story_shear" and
            x["basis"]=="static_design" for x in before))
        bundle_seismic_review(self.src,self.out,method="ESM")
        after=collect(self.src,[],results_root=self.out)
        self.assertEqual(before,after)
        meta.write_text(json.dumps({"model_sha256":"wrong",
            "limit_state":"ULS","axis":"X","response_case":"ULS_X+_E0"}))
        rejected=collect(self.src,[],results_root=self.out)
        self.assertFalse(any(x["location"]=="3" for x in rejected))

    def test_mrsm_no_overwrite_or_archive_recursion(self):
        first=bundle_seismic_review(self.src,self.out,method="MRSM")
        sha=hashlib.sha256(Path(first["zip"]).read_bytes()).hexdigest()
        second=bundle_seismic_review(self.src,self.out,method="MRSM")
        self.assertNotEqual(first["zip"],second["zip"])
        self.assertEqual(sha,hashlib.sha256(Path(first["zip"]).read_bytes()).hexdigest())
        with zipfile.ZipFile(second["zip"]) as archive:
            names=archive.namelist()
            self.assertTrue(any("MRSM_Results_V132.json" in n for n in names))
            self.assertFalse(any("MRSM_Review_" in n for n in names))
            self.assertFalse(any("UPLOAD.zip" in n for n in names))
        self.assertTrue((self.out/"Seismic_Review_Packages"/
                         "LATEST_MRSM_REVIEW.txt").is_file())


if __name__=="__main__":
    unittest.main()
