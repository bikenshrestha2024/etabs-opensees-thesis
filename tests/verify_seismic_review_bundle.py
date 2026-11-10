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
