"""Stage 06 matched research-suite smoke tests. Not a solved building."""
import unittest
from components.nonlinear_time_history.variant_comparison import (
    VARIANTS,INVARIANTS,METRICS,validate_variant_manifest,compare_completed_cases)
def manifest():
    return {"variants":[dict(variant=m,model_export_path=m,
            model_file_sha256="a"*64,outrigger_floors=[] if m=="M0" else [7],
            **{k:"b"*64 for k in INVARIANTS}) for m in VARIANTS]}
def suite():
    data={}
    for model in VARIANTS:
        cases=[]
        for limit in ("ULS","SLS"):
            for pair in ("P1","P2","P3"):
                for axis in ("XY","YX"):
                    cases.append(dict(variant_id=model,model_sha256="a"*64,
                        limit_state=limit,pair_id=pair,
                        orientation=axis,record_sha256=pair,
                        completion_gate=dict(status="FULL_DURATION_NUMERIC_SCREEN",
                            full_record_completed=True,accepted_channels_finite=True),
                        **{k:.01 if "drift" in k else 1. for k in METRICS}))
        data[model]=cases
    return data
class CompareTests(unittest.TestCase):
    def test_complete_same_suite(self):
        result=compare_completed_cases(manifest(),suite())
        self.assertEqual(result["paired_case_keys"],12)
        self.assertEqual(result["status"],"RESEARCH_SCREEN_ONLY_NOT_THESIS_VALIDATION")
    def test_uls_sls_separated_and_seven_pairs_not_decided(self):
        data=suite()
        for c in data["M1"]:
            if c["limit_state"]=="SLS":
                c["peak_roof_UX_m"]=3.0
        result=compare_completed_cases(manifest(),data)
        self.assertEqual(result["by_limit_state"]["SLS"]["M1"]["peak_roof_UX_m"]["maximum"],3.0)
        self.assertEqual(result["by_limit_state"]["ULS"]["M1"]["peak_roof_UX_m"]["maximum"],1.0)
        self.assertEqual(result["nbc105_2025_response_aggregation_by_limit_state"]["ULS"],"MAXIMUM")
        for variant in data:
            for limit in ("ULS","SLS"):
                for orientation in ("XY","YX"):
                    data[variant].extend([
                        dict(data[variant][0],pair_id=pair,
                             limit_state=limit,orientation=orientation)
                        for pair in ("P4","P5","P6","P7")])
        # Seven-pair result remains research screening and requests clause interpretation.
        seven=compare_completed_cases(manifest(),data)
        self.assertTrue(seven["exactly_seven_rule_requires_interpretation"])
        self.assertIn("REVIEW_REQUIRED",
            seven["nbc105_2025_response_aggregation_by_limit_state"]["ULS"])

    def test_eight_pair_mean_differs_from_worst_case(self):
        data=suite()
        for variant in data:
            for limit in ("ULS","SLS"):
                for orientation in ("XY","YX"):
                    for pair in ("P4","P5","P6","P7","P8"):
                        template=next(x for x in data[variant]
                           if x["limit_state"]==limit and x["orientation"]==orientation)
                        fresh=dict(template,pair_id=pair,record_sha256=pair)
                        data[variant].append(fresh)
        # One huge pair P8 should influence the AVERAGE but not replace it
        # with an unlabelled pooled maximum.
        for case in data["M1"]:
            if case["limit_state"]=="ULS" and case["pair_id"]=="P8":
                case["peak_roof_UX_m"]=17.
        report=compare_completed_cases(manifest(),data)
        u=report["by_limit_state"]["ULS"]["M1"]["peak_roof_UX_m"]
        self.assertEqual(report["nbc105_2025_response_aggregation_by_limit_state"]["ULS"],"AVERAGE")
        self.assertAlmostEqual(u["maximum"],17.)
        self.assertAlmostEqual(u["nbc105_aggregate"],3.)
        self.assertAlmostEqual(u["M0_nbc105_aggregate"],1.)
        self.assertAlmostEqual(u["nbc105_aggregate_reduction_percent"],-200.)
        self.assertFalse(u["aggregate_is_code_approval"])

    def test_reject_changed_mass(self):
        p=manifest();p["variants"][3]["mass_basis_sha256"]="c"*64
        with self.assertRaisesRegex(ValueError,"mass_basis"):
            validate_variant_manifest(p)
    def test_reject_missing_motion(self):
        data=suite();data["M2"].pop()
        with self.assertRaisesRegex(ValueError,"missing/extra"):
            compare_completed_cases(manifest(),data)
    def test_reject_wrong_variant_source(self):
        data=suite()
        data["M2"][0]["variant_id"]="M1"
        with self.assertRaisesRegex(ValueError,"variant ID"):
            compare_completed_cases(manifest(),data)
    def test_reject_trial(self):
        data=suite();data["M3"][0]["completion_gate"]["full_record_completed"]=False
        with self.assertRaisesRegex(ValueError,"full-duration"):
            compare_completed_cases(manifest(),data)
if __name__=="__main__":unittest.main()
