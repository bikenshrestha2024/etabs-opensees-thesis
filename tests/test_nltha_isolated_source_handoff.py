"""A complete native NLTHA requires independent XY and YX on-disk evidence.

Tests use fixed synthetic metadata to REJECT false completion. They do not
claim a full building analysis or calibrated E-SFI-MVLEM-3D behavior.
"""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from components.nonlinear_time_history import direct_existing_model as native

DIGEST_MODEL="a"*64
DIGEST_MOTION="b"*64


class CompletedExistingNLTHAEvidence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.config={
            "pair_id":"Kobe","variant_id":"M0","limit_state":"ULS",
            "orientations":["XY","YX"],"diagnostic_excitation":"XY",
            "duration_s":0.,"nonlinear_walls":True
        }
        self.cases=[]
        for orientation in ("XY","YX"):
            folder=self.root/orientation
            folder.mkdir()
            gate={
                "status":"FULL_DURATION_NUMERIC_SCREEN",
                "full_record_completed":True,
                "accepted_states":3,
                "achieved_time_s":0.01,
                "full_record_duration_s":0.01,
            }
            summary={
                "orientation":orientation, "status":"COMPLETED_EXPLORATORY_RECORD",
                "variant_id":"M0","pair_id":"Kobe","limit_state":"ULS",
                "diagnostic_excitation":"XY",
                "model_sha256":DIGEST_MODEL,"record_sha256":DIGEST_MOTION,
                "physical_time_s":0.01,"full_record_duration_s":0.01,
                "completion_gate":gate
            }
            self.cases.append(summary)
            (folder/"Case_Summary.json").write_text(json.dumps(summary),encoding="utf8")
            (folder/"Accepted_History_Completion_Gate.json").write_text(json.dumps(gate),encoding="utf8")
            with (folder/"Building_Nonlinear_history.csv").open("w",newline="",encoding="utf-8") as h:
                w=csv.writer(h);w.writerow(["time_s","Storey_25_UX_m"])
                w.writerows(((0.,0.),(.005,.002),(.01,.003)))

    def test_valid_full_record_has_two_independently_verified_history_files(self):
        result=native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)
        self.assertEqual(set(result),{"XY","YX"})
        self.assertTrue(all(len(result[orientation]["history_sha256"])==64 for orientation in result))
        self.assertEqual(result["XY"]["accepted_states"],3)

    def test_returned_summary_without_history_does_not_count_as_full(self):
        (self.root/"YX"/"Building_Nonlinear_history.csv").unlink()
        with self.assertRaisesRegex((FileNotFoundError,RuntimeError),"YX|history"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)

    def test_missing_gate_must_not_be_accepted_on_status_string_alone(self):
        (self.root/"YX"/"Accepted_History_Completion_Gate.json").unlink()
        with self.assertRaisesRegex((FileNotFoundError,RuntimeError),"YX|Gate"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)

    def test_failed_or_truncated_history_is_not_full(self):
        self.cases[0]["completion_gate"]["full_record_completed"]=False
        with self.assertRaisesRegex(ValueError,"full|FULL"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)

    def test_shortened_last_accepted_state_is_rejected(self):
        path=self.root/"XY"/"Building_Nonlinear_history.csv"
        path.write_text("time_s,Storey_25_UX_m\n0,0\n0.005,0.002\n",encoding="utf8")
        with self.assertRaisesRegex(ValueError,"duration|states|end"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)

    def test_nan_response_is_not_complete_even_with_successful_solver_status(self):
        path=self.root/"XY"/"Building_Nonlinear_history.csv"
        path.write_text("time_s,Storey_25_UX_m\n0,0\n0.005,nan\n0.01,0.003\n",encoding="utf8")
        with self.assertRaisesRegex(ValueError,"Nonfinite|nonfinite|finite"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)

    def test_stale_or_mixed_case_model_sha_is_blocked(self):
        self.cases[1]["model_sha256"]="c"*64
        with self.assertRaisesRegex(ValueError,"model|SHA|identity"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)

    def test_single_direction_probe_cannot_claim_bidirectional_full_record(self):
        self.config["diagnostic_excitation"]="X"
        with self.assertRaisesRegex(ValueError,"XY|excitation"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)

    def test_record_hash_must_agree_in_both_fresh_orientations(self):
        self.cases[1]["record_sha256"]="d"*64
        with self.assertRaisesRegex(ValueError,"record|SHA"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)

    def test_saved_summary_must_match_returned_solver_case(self):
        self.cases[0]["physical_time_s"]=0.02
        with self.assertRaisesRegex(ValueError,"summary|time|duration"):
            native.verify_full_duration_pair_outputs(self.root,self.config,self.cases)


if __name__=="__main__":
    unittest.main()
