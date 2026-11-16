"""Synthetic MRSM case-file checks, no ETABS or OpenSees native solver.

[REF docs/source/components/response_spectrum/model_analysis.py.md]
"""
import json
import tempfile
import unittest
from pathlib import Path

from components.response_spectrum.model_analysis import validate_mrsm_case_output
from components.response_spectrum.reports import saved_cases


def make_cases(digest="a"*64, state="ULS"):
    return {
        axis+ecc:{
            "axis":axis,"limit_state":state,"model_sha256":digest,
            "unscaled_modal_base_shear_kN":100.,
            "reference_ESM_base_shear_kN":120.,
            "force_scale":1.2,
            "scaled_modal_base_shear_kN":120.,
            "mass_participation_percent":95.,
            "status":"ANALYSIS COMPLETE / DESIGN COMBINATIONS REQUIRE REVIEW",
            "stories":[{"story_number":1,"height_m":3.8,
                        "design_displacement_m":.01,
                        "scaled_story_shear_kN":120.,
                        "design_drift_ratio":0.01}]
        } for axis in ("X","Y") for ecc in ("_E0","_Eplus","_Eminus")
    }


class MRSMOutputTests(unittest.TestCase):
    def test_six_cases_and_model_source_match(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"05_MRSM"/"RUNS"/"ULS"/"test"/"run1"/"02_RESULTS"
            root.mkdir(parents=True)
            result=root/"MRSM_Results_V132.json"
            result.write_text(json.dumps(make_cases()),encoding="utf-8")
            gate=validate_mrsm_case_output(root,state="ULS",expected_model_sha256="a"*64)
            self.assertEqual(gate["case_count"],6)
            self.assertEqual(gate["status"],"COMPLETE_SAVED_CASES_ONLY")
            self.assertEqual(len(saved_cases(Path(td))),6)
            with self.assertRaisesRegex(ValueError,"requested model SHA"):
                validate_mrsm_case_output(root,state="ULS",expected_model_sha256="b"*64)
            incomplete=make_cases()
            incomplete.pop("Y_Eminus")
            result.write_text(json.dumps(incomplete))
            with self.assertRaisesRegex(ValueError,"Incomplete"):
                validate_mrsm_case_output(root,state="ULS")
            result.write_text(json.dumps(make_cases(state="SLS")))
            with self.assertRaisesRegex(ValueError,"state mismatch"):
                validate_mrsm_case_output(root,state="ULS")

    def test_latest_same_model_and_reject_other_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            first=root/"05_MRSM"/"RUNS"/"ULS"/"test"/"r1"/"02_RESULTS"
            second=root/"05_MRSM"/"RUNS"/"ULS"/"test"/"r2"/"02_RESULTS"
            first.mkdir(parents=True);second.mkdir(parents=True)
            a=first/"MRSM_Results_V132.json"
            b=second/"MRSM_Results_V132.json"
            a.write_text(json.dumps(make_cases()))
            b.write_text(json.dumps(make_cases()))
            # Latest same-model source wins; no duplicate curves.
            import os
            os.utime(a,(100,100));os.utime(b,(200,200))
            cases=saved_cases(root)
            self.assertEqual(len(cases),6)
            self.assertTrue(all(p==b for p,_,_ in cases))
            b.write_text(json.dumps(make_cases("b"*64)))
            with self.assertRaisesRegex(ValueError,"incompatible MRSM models"):
                saved_cases(root)
            self.assertEqual(len(saved_cases(first)),6)

    def test_nan_and_nonhex_model_sha_rejected_even_with_six_case_files(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            file=root/"MRSM_Results_V132.json"
            broken=make_cases()
            broken["X_E0"]["stories"][0]["design_drift_ratio"]=float("nan")
            file.write_text(json.dumps(broken))
            with self.assertRaisesRegex(ValueError,"nonfinite/negative drift"):
                validate_mrsm_case_output(root,state="ULS")
            broken=make_cases("z"*64)
            file.write_text(json.dumps(broken))
            with self.assertRaisesRegex(ValueError,"fingerprint missing/invalid"):
                validate_mrsm_case_output(root,state="ULS")
            broken=make_cases()
            broken["Y_Eminus"]["stories"][0].pop("design_drift_ratio")
            file.write_text(json.dumps(broken))
            with self.assertRaisesRegex(ValueError,"missing design_drift_ratio"):
                validate_mrsm_case_output(root,state="ULS")

    def test_missing_force_mass_and_inconsistent_scale_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"MRSM_Results_V132.json"
            for field in ("unscaled_modal_base_shear_kN",
                          "scaled_modal_base_shear_kN",
                          "force_scale","mass_participation_percent"):
                rows=make_cases()
                rows["X_E0"].pop(field)
                output.write_text(json.dumps(rows))
                with self.assertRaisesRegex(ValueError,"missing/invalid required numeric"):
                    validate_mrsm_case_output(td,state="ULS")
            for value in (0.0,-1.0,float("nan"),float("inf")):
                rows=make_cases()
                rows["Y_Eplus"]["unscaled_modal_base_shear_kN"]=value
                output.write_text(json.dumps(rows))
                with self.assertRaises(ValueError):
                    validate_mrsm_case_output(td,state="ULS")
            rows=make_cases()
            rows["X_Eminus"]["scaled_modal_base_shear_kN"]=180.
            output.write_text(json.dumps(rows))
            with self.assertRaisesRegex(ValueError,"inconsistent force-scaled"):
                validate_mrsm_case_output(td,state="ULS")
            rows=make_cases()
            rows["X_E0"]["mass_participation_percent"]=42.
            output.write_text(json.dumps(rows))
            with self.assertRaisesRegex(ValueError,"modal mass"):
                validate_mrsm_case_output(td,state="ULS")
            rows=make_cases()
            rows["Y_E0"]["stories"][0].pop("scaled_story_shear_kN")
            output.write_text(json.dumps(rows))
            with self.assertRaisesRegex(ValueError,"missing scaled_story_shear"):
                validate_mrsm_case_output(td,state="ULS")

    def test_snapshots_and_zip_do_not_contribute(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            copy=root/"05_MRSM"/"REVIEW_SNAPSHOTS"/"old"
            copy.mkdir(parents=True)
            (copy/"MRSM_Results_V132.json").write_text(json.dumps(make_cases()))
            self.assertEqual(saved_cases(root),[])
            self.assertFalse((root/"OpenSees_Analysis_Results").exists())


if __name__=="__main__":
    unittest.main()
