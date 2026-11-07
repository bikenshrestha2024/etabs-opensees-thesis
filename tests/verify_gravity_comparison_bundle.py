"""Gravity comparison bundle: missing evidence and upload artifact regression."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from components.gravity.comparison_bundle import export_bundle

class GravityBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.export=self.root/"export"; self.export.mkdir()
        self.gravity=self.root/"gravity";self.gravity.mkdir()
        (self.export/"OpenSees_Complete_Model_Data_V118.json").write_text(
            '{"model":"synthetic"}',encoding="utf8")
        self.sample={"ok":True,"nodes":[{"tag":1,"x_m":0,"y_m":0,"z_m":0,
                    "ux_m":0,"uy_m":0,"uz_m":-0.01,
                    "rx_rad":0,"ry_rad":0,"rz_rad":0}],
                     "reactions":[{"node_tag":1,"rx_kN":0,"ry_kN":0,"rz_kN":100}],
                     "local_forces":[{"tag":200,"N_i_kN":10,"N_j_kN":-10}],
                     "report":{"applied_vertical_load_kN":100}}
        (self.gravity/"Gravity_Result_V110.json").write_text(
            json.dumps(self.sample),encoding="utf8")
    def test_bundle_contains_manifest_and_numeric_exports(self):
        audit,zip_path=export_bundle(self.export,self.gravity,self.root/"out")
        self.assertTrue(zip_path.is_file())
        self.assertEqual(audit["openSees_support_rz_kN"],100)
        self.assertFalse(audit["compare_verified"])
        self.assertTrue(any(x["file"]=="etabs/etabs_gravity.json" for x in audit["missing"]))
        with zipfile.ZipFile(zip_path) as z:
            names=z.namelist()
            self.assertTrue(any(s.endswith("/opensees/nodes.csv") for s in names))
            self.assertTrue(any(s.endswith("/opensees/reactions.csv") for s in names))
            self.assertTrue(any(s.endswith("/opensees/local_forces.csv") for s in names))
            self.assertTrue(any(s.endswith("/EVIDENCE_MANIFEST.json") for s in names))
    def test_preserves_source_and_versions_without_overwrite(self):
        path=self.gravity/"Gravity_Result_V110.json"
        original=hashlib.sha256(path.read_bytes()).hexdigest()
        _,first=export_bundle(self.export,self.gravity,self.root/"out")
        first_hash=hashlib.sha256(first.read_bytes()).hexdigest()
        _,second=export_bundle(self.export,self.gravity,self.root/"out")
        self.assertNotEqual(first,second)
        self.assertTrue(second.name.endswith("_V02.zip"))
        self.assertTrue((self.root/"out"/second.stem/"EVIDENCE_MANIFEST.json").is_file())
        self.assertEqual(first_hash,hashlib.sha256(first.read_bytes()).hexdigest())
        self.assertEqual(original,hashlib.sha256(path.read_bytes()).hexdigest())
    def test_failure_not_mislabeled_as_good_evidence(self):
        self.sample["ok"]=False
        (self.gravity/"Gravity_Result_V110.json").write_text(json.dumps(self.sample))
        with self.assertRaisesRegex(ValueError,"successful solver"):
            export_bundle(self.export,self.gravity,self.root/"failed")
    def test_etabs_source_carried_without_claiming_equivalence(self):
        etabs=self.root/"etabs.json"
        etabs.write_text('{"case":"DEAD+LIVE","status":"UNVERIFIED"}')
        audit,z=export_bundle(self.export,self.gravity,self.root/"with_etabs",etabs_json=etabs)
        self.assertFalse(audit["compare_verified"])
        with zipfile.ZipFile(z) as obj:
            self.assertTrue(any(n.endswith("/etabs/etabs_gravity.json") for n in obj.namelist()))
    def test_oversize_file_is_flagged(self):
        (self.export/"Gravity_Source_Load_Detail_V131.csv").write_text("0123456789"*150)
        audit,_=export_bundle(self.export,self.gravity,self.root/"small",max_file_mb=.0001)
        self.assertTrue(any(x["file"].endswith("Gravity_Source_Load_Detail_V131.csv")
                            for x in audit["oversize_skipped"]))

if __name__=="__main__":
    unittest.main()
