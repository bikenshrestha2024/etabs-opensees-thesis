"""Matrix completeness is deliberately stricter than an optimum claim."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from tools.audit_soil_c_case_completion import audit_matrix, inspect_case


class MatrixAuditTests(unittest.TestCase):
    def test_empty_112_matrix_never_claims_optimum(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            manifest=root/"matrix.csv"
            with manifest.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=[
                    "variant","limit_state","earthquake","output_directory"])
                w.writeheader()
                for i in range(7):
                    for state in ("ULS","SLS"):
                        for event in ("Gorkha","Landers","Northridge","Kobe",
                                      "Kocaeli","Chi-Chi","Hector Mine","Loma Prieta"):
                            w.writerow(dict(variant=f"M{i}",limit_state=state,
                                            earthquake=event,
                                            output_directory=str(root/f"M{i}"/state/event)))
            report=audit_matrix(manifest)
            self.assertEqual(report["expected_analyses"],224)
            self.assertEqual(report["state_counts"]["NOT_RUN"],224)
            self.assertFalse(report["optimum_selected"])
    def test_exploratory_full_record_not_design_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            d=Path(folder)/"XY";d.mkdir()
            source=dict(variant_id="M0",limit_state="ULS",pair_id="Kobe",orientation="XY",
                        record_sha256="a"*64,model_sha256="b"*64,
                        diagnostic_excitation="XY",
                        peak_roof_UX_m=1,peak_roof_UY_m=1,
                        max_story_drift_X=.01,max_story_drift_Y=.01,
                        peak_base_shear_X_kN=1,peak_base_shear_Y_kN=1,
                        peak_roof_torsion_rad=0.01)
            (d/"Case_Summary.json").write_text(json.dumps(source))
            (d/"Accepted_History_Completion_Gate.json").write_text(json.dumps({
                "status":"FULL_DURATION_NUMERIC_SCREEN",
                "full_record_completed":True,"accepted_channels_finite":True}))
            result=inspect_case(d.parent,"M0","ULS","Kobe","XY")
            self.assertEqual(result["status"],"RESEARCH_ONLY_FULL_RECORD")
            source["orientation"]="YX"
            (d/"Case_Summary.json").write_text(json.dumps(source))
            result=inspect_case(d.parent,"M0","ULS","Kobe","XY")
            self.assertEqual(result["status"],"INCOMPLETE")

if __name__=="__main__":
    unittest.main()
