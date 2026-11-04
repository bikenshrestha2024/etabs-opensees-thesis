"""Synthetic component metrics only; never substitutes for measured curves."""
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.audit_component_experiments import inspect_input, compare


class ComponentExperiments(unittest.TestCase):
    def test_missing_data_not_approved(self):
        r=inspect_input({"component_type":"FVD"})
        self.assertEqual(r["status"],"REQUIRES_PROJECT_EVIDENCE")
        self.assertFalse(r["experimentally_validated"])

    def test_brb_comparison_is_not_validation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/"measured.csv";q=root/"sim.csv"
            for path,delta in ((p,0),(q,1)):
                with path.open("w",newline="") as f:
                    w=csv.writer(f);w.writerow(("time_s","disp_m","force_kN"))
                    for i in range(12):
                        w.writerow((i/10,i*.001, i+delta))
            m=dict(component_type="BRB",units="kN-m-s",
                   source_doi_or_primary_report="SPECIMEN_SOURCE",
                   specimen_id="synthetic_test_only",loading_protocol="synthetic",
                   experiment_csv=str(p),simulation_csv=str(q),
                   parameter_card_sha256="a"*64,
                   experiment_input_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                   model_command="uniaxialMaterial Steel02")
            r=compare(m)
            self.assertAlmostEqual(r["metrics"]["X"]["force_rmse_kN"],1.)
            self.assertFalse(r["experimentally_validated"])
            self.assertEqual(r["status"],"COMPARISON_COMPUTED_NO_ACCEPTANCE_THRESHOLD")
            m["experiment_input_sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"SHA256"):
                compare(m)

    def test_three_dimensional_wall_requires_actual_axial_and_rebar(self):
        m=dict(component_type="CORE_3D",units="kN-m-s",
               source_doi_or_primary_report="source",specimen_id="wall",
               loading_protocol="biaxial",experiment_csv="a.csv",
               simulation_csv="b.csv",model_command="E_SFI_MVLEM_3D",
               parameter_card_sha256="a"*64,experiment_input_sha256="b"*64)
        with self.assertRaisesRegex(ValueError,"axial_load"):
            compare(m)

if __name__=="__main__":
    unittest.main()
