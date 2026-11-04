"""Solver-free regression for 8x2 Soil C matched earthquake input policy.

Synthetic fixtures are NOT experimental record or nonlinear building approval.
"""
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from components.nonlinear_time_history.soil_c_nltha_suite import (
    EVENT_ORDER, FIELD_TYPE, register_rows, audit_suite, verify_runner_pair,
    reconcile_loma_runtime_pair
)

class SoilCPreflightTests(unittest.TestCase):
    def _register(self, folder):
        rows=[]
        for event in EVENT_ORDER:
            for comp in ("A","B"):
                name=event.replace(" ","_")+"_"+comp+".txt"
                content=("Time Series matched accelerogram: "+name+"\n"
                         "Time Step: 0.005 s\nTime(sec) Acc(g)\n"
                         "0.000 0.000\n0.005 0.100\n0.010 -0.200\n")
                if event=="Loma Prieta" and comp=="B":
                    content+="0.015 0.000\\n"
                file=Path(folder)/name
                file.write_text(content,encoding="utf-8")
                rows.append(dict(event=event,component=comp,
                    source_filename=name,
                    matched_dt_s="0.005",
                    matched_end_time_s="0.010" if (event!="Loma Prieta" or comp=="A") else "0.015",
                    matched_pga_g="0.2",matched_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                    mean_abs_conditional_psa_error_percent="3.0"))
        path=Path(folder)/"register.csv"
        with path.open("w",newline="",encoding="utf-8") as fh:
            writer=csv.DictWriter(fh,fieldnames=rows[0].keys())
            writer.writeheader();writer.writerows(rows)
        return path,rows

    def test_literal_events(self):
        self.assertEqual(len(EVENT_ORDER),8)
        self.assertEqual(sum(v=="Near-field" for v in FIELD_TYPE.values()),6)
        self.assertEqual(sum(v=="Far-field" for v in FIELD_TYPE.values()),2)

    def test_expected_registered_sources(self):
        found=register_rows()
        self.assertEqual(len(found),16)
        self.assertEqual(found["Kobe","A"]["matched_pga_g"],"0.26518")
        self.assertAlmostEqual(float(found["Gorkha","A"]["matched_end_time_s"]),322.940)

    def test_all_sources_and_loma_end_review(self):
        with tempfile.TemporaryDirectory() as d:
            register,rows=self._register(d)
            report=audit_suite(d,register=register)
            self.assertEqual(report["pair_count"],8)
            self.assertEqual(report["component_source_failures"],[])
            self.assertEqual(report["timing_policy_review_required"],["Loma Prieta"])
            self.assertFalse(report["source_and_pair_synchronization_pass"])
            self.assertEqual(report["nbc_105_9_3_3_response_rule_for_eight_pairs"],"AVERAGE")
            self.assertFalse(report["site_and_earthquake_input_design_approval"])

    def test_hash_change_detected(self):
        with tempfile.TemporaryDirectory() as d:
            reg,rows=self._register(d)
            (Path(d)/rows[0]["source_filename"]).write_text("SOURCE MODIFIED")
            report=audit_suite(d,register=reg)
            self.assertTrue(report["component_source_failures"])

    def test_unknown_modal_periods_not_assumed(self):
        with tempfile.TemporaryDirectory() as d:
            reg,rows=self._register(d)
            report=audit_suite(d,register=reg)
            self.assertEqual(report["current_modal_period_screen"]["status"],
                             "UNKNOWN_NO_VERIFIED_CURRENT_MODAL_INPUTS")
            with self.assertRaisesRegex(ValueError,"ALL"):
                audit_suite(d,register=reg,t1_x_s=3.5)

    def test_out_of_range_6_second_period_marked(self):
        with tempfile.TemporaryDirectory() as d:
            reg,rows=self._register(d)
            report=audit_suite(d,register=reg,t1_x_s=3.526,t1_y_s=3.2,
              tn90_x_s=.13,tn90_y_s=.15,analysis_dt_s=.005)
            self.assertFalse(report["current_modal_period_screen"]["record_fit_range_covered"])
            self.assertGreater(report["current_modal_period_screen"]["fit_window_X_s"][1],6.5)

    def test_no_hidden_source_reuse_or_extra_scale(self):
        with tempfile.TemporaryDirectory() as d:
            reg,rows=self._register(d)
            found=register_rows(reg)
            px=Path(d)/found["Kobe","A"]["source_filename"]
            py=Path(d)/found["Kobe","B"]["source_filename"]
            with patch("components.nonlinear_time_history.soil_c_nltha_suite.register_rows",return_value=found):
                result=verify_runner_pair(px,py,registered_event="Kobe")
                self.assertEqual(result["additional_spectral_scale"],1.)
                self.assertEqual(result["acceleration_source_units"],"g")
                with self.assertRaisesRegex(ValueError,"A/B pair"):
                    verify_runner_pair(py,px)
                with self.assertRaisesRegex(ValueError,"Gorkha"):
                    verify_runner_pair(Path(d)/found["Gorkha","A"]["source_filename"],
                       Path(d)/found["Gorkha","B"]["source_filename"])
                with self.assertRaisesRegex(ValueError,"Loma Prieta"):
                    verify_runner_pair(Path(d)/found["Loma Prieta","A"]["source_filename"],
                       Path(d)/found["Loma Prieta","B"]["source_filename"])

    def test_explicit_single_zero_endpoint_only(self):
        pair=[([0.,.1],.005,"g"),([0.,.2,.1],.005,"g")]
        with self.assertRaisesRegex(ValueError,"ONE zero"):
            reconcile_loma_runtime_pair(pair)
        fixed,meta=reconcile_loma_runtime_pair(pair,policy="append_zero_reviewed",
                                               reviewer="source-reviewer")
        self.assertEqual(meta["added_samples"],1)
        self.assertEqual(fixed[0][0], [0.,.1,0.])
        self.assertEqual(pair[0][0], [0.,.1])
        with self.assertRaisesRegex(ValueError,"ONE zero"):
            reconcile_loma_runtime_pair([([0.],.005,"g"),([0.,.1,.2],.005,"g")],
                                        policy="append_zero_reviewed",reviewer="engineer")

if __name__=="__main__":
    unittest.main()
