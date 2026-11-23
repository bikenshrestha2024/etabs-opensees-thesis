"""Saved MRSM run must match selected source, state and actual numeric files.

Synthetic temporary inputs only; no ETABS native EDB, OpenSees execution,
private model files or source workbook contents.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_contract import RUN_SUBFOLDERS, SCHEMA
from components.shared.case_status import CaseLedger
import components.response_spectrum.model_analysis as mrsm

IDS = [state + " " + axis + "_" + ecc
       for state in ("ULS",) for axis in ("X", "Y")
       for ecc in ("E0", "Eplus", "Eminus")]


def selected_fields():
    return {
        "limit_state": "ULS", "soil": "C", "Z": "0.35", "I": "1.0",
        "rmu": "3.5", "omegau": "1.4", "omegas": "1.2",
        "T1_X": "1.9", "T1_Y": "2.0", "nmodes": "40",
        "damping": "0.05", "support_case": "PHYSICAL_32",
        "seismic_mass_policy": "SOURCE_DISTRIBUTED",
        "gravity_profile": "AS_CONFIGURED"
    }


def numeric_cases(model_sha):
    return {
        axis + "_" + ecc: {
            "axis": axis, "limit_state": "ULS", "model_sha256": model_sha,
            "unscaled_modal_base_shear_kN": 100.,
            "reference_ESM_base_shear_kN": 120.,
            "force_scale": 1.2, "scaled_modal_base_shear_kN": 120.,
            "mass_participation_percent": 95.,
            "status": "ANALYSIS COMPLETE / DESIGN COMBINATIONS REQUIRE REVIEW",
            "stories": [{
                "story_number": 1, "height_m": 3.8,
                "design_displacement_m": .01,
                "scaled_story_shear_kN": 120.,
                "design_drift_ratio": .01,
            }]
        }
        for axis in ("X", "Y") for ecc in ("E0", "Eplus", "Eminus")
    }


def build_synthetic_workspace(tmp):
    parent = Path(tmp)
    source = parent / "source"
    source.mkdir()
    model_file = source / "OpenSees_Complete_Model_Data_V118.json"
    model_file.write_text('{"nodes": {}, "model": "A"}', encoding="utf-8")
    model_sha = hashlib.sha256(model_file.read_bytes()).hexdigest()
    stage = parent / "analysis" / "05_MRSM"
    stage.mkdir(parents=True)
    run = stage / "RUNS" / "ULS" / "MRSM_AS_CONFIGURED" / "synthetic_run_001"
    for sub in RUN_SUBFOLDERS:
        (run / sub).mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": SCHEMA, "stage": "05_MRSM", "state": "ULS",
        "case_id": "MRSM_AS_CONFIGURED", "run_id": run.name,
        "units": "kN-m-s", "model_sha256": model_sha,
        "source_edb_sha256": None,
        "solver_status": "COMPLETED_SOLVER_ONLY",
        "structural_acceptance": "NOT_VERIFIED",
        "files": [], "subfolders": list(RUN_SUBFOLDERS),
    }
    (run / "00_INPUT_SOURCE" / "CASE_MANIFEST.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (run / "02_RESULTS" / "MRSM_Results_V132.json").write_text(
        json.dumps(numeric_cases(model_sha)), encoding="utf-8"
    )
    (run / "06_REVIEW" / "SAVED_CASE_COMPLETENESS.json").write_text(
        json.dumps({
            "status": "COMPLETE_SAVED_CASES_ONLY", "model_sha256": model_sha,
            "case_count": 6,
        }), encoding="utf-8"
    )
    return source, stage, run, model_sha


class MRSMReopenSourceGateTests(unittest.TestCase):
    def test_legacy_completed_rows_are_not_current_numeric_completions(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, stage, run, digest = build_synthetic_workspace(tmp)
            status = stage / "MRSM_Batch_Status_V151.json"
            status.write_text(json.dumps({
                "cases": [{"case": case, "status": "COMPLETED"} for case in IDS]
            }), encoding="utf-8")
            result = mrsm.review_saved_mrsm_batch(stage, source, selected_fields())
            self.assertEqual(result["status"], "LEGACY_UNVERIFIED")
            self.assertEqual(result["numerical_cases_verified"], 0)
            self.assertEqual(result["reported_completed"], 6)

    def test_matching_source_and_saved_numeric_reopens_six_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, stage, run, digest = build_synthetic_workspace(tmp)
            fields = selected_fields()
            ledger = CaseLedger(
                stage / "MRSM_Batch_Status_V151.json", IDS,
                provenance={
                    "model_sha256": digest,
                    "state": "ULS",
                    "input_sha256": mrsm.mrsm_input_signature(fields),
                }
            )
            ledger.set_provenance(run_dir=str(run))
            for case in IDS:
                ledger.set(case, "COMPLETED", "Synthetic solver-only result")
            result = mrsm.review_saved_mrsm_batch(stage, source, fields)
            self.assertEqual(result["status"],
                             "SAVED_NUMERICALLY_COMPLETE_SOURCE_MATCHED")
            self.assertEqual(result["numerical_cases_verified"], 6)
            self.assertEqual(result["reported_completed"], 6)
            self.assertEqual(result["engineering_acceptance"], "NOT_VERIFIED")

    def test_changed_model_or_input_or_state_cannot_reuse_saved_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, stage, run, digest = build_synthetic_workspace(tmp)
            fields = selected_fields()
            ledger = CaseLedger(stage / "MRSM_Batch_Status_V151.json", IDS,
                                provenance={
                                    "model_sha256": digest, "state": "ULS",
                                    "input_sha256": mrsm.mrsm_input_signature(fields),
                                    "run_dir": str(run)
                                })
            for case in IDS:ledger.set(case, "COMPLETED", "Stored result")
            model_file = source / "OpenSees_Complete_Model_Data_V118.json"
            model_file.write_text('{"nodes": {}, "model": "B"}', encoding="utf-8")
            mismatch = mrsm.review_saved_mrsm_batch(stage, source, fields)
            self.assertEqual(mismatch["status"], "SOURCE_OR_INPUT_MISMATCH")
            self.assertEqual(mismatch["numerical_cases_verified"], 0)
            model_file.write_text('{"nodes": {}, "model": "A"}', encoding="utf-8")
            altered = dict(fields, support_case="SOURCE_76")
            mismatch = mrsm.review_saved_mrsm_batch(stage, source, altered)
            self.assertEqual(mismatch["status"], "SOURCE_OR_INPUT_MISMATCH")
            altered = dict(fields, limit_state="SLS")
            mismatch = mrsm.review_saved_mrsm_batch(stage, source, altered)
            self.assertEqual(mismatch["status"], "SOURCE_OR_INPUT_MISMATCH")

    def test_missing_numeric_response_or_run_manifest_does_not_certify(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, stage, run, digest = build_synthetic_workspace(tmp)
            fields = selected_fields()
            ledger = CaseLedger(stage / "MRSM_Batch_Status_V151.json", IDS,
                                provenance={
                                    "model_sha256": digest, "state": "ULS",
                                    "input_sha256": mrsm.mrsm_input_signature(fields),
                                    "run_dir": str(run)})
            for case in IDS:ledger.set(case, "COMPLETED", "Stored result")
            (run / "02_RESULTS" / "MRSM_Results_V132.json").unlink()
            result = mrsm.review_saved_mrsm_batch(stage, source, fields)
            self.assertEqual(result["status"], "NUMERIC_EVIDENCE_INCOMPLETE")
            self.assertEqual(result["numerical_cases_verified"], 0)
            (run / "00_INPUT_SOURCE" / "CASE_MANIFEST.json").unlink()
            result = mrsm.review_saved_mrsm_batch(stage, source, fields)
            self.assertEqual(result["status"], "NUMERIC_EVIDENCE_INCOMPLETE")
            self.assertEqual(result["numerical_cases_verified"], 0)

    def test_foreign_run_dir_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, stage, run, digest = build_synthetic_workspace(tmp)
            fields = selected_fields()
            foreign = Path(tmp) / "other" / "05_MRSM" / "RUNS" / "ULS" / "MRSM_AS_CONFIGURED" / run.name
            foreign.parent.mkdir(parents=True)
            ledger = CaseLedger(stage / "MRSM_Batch_Status_V151.json", IDS,
                                provenance={"model_sha256": digest, "state": "ULS",
                                "input_sha256": mrsm.mrsm_input_signature(fields),
                                "run_dir": str(foreign)})
            for case in IDS:ledger.set(case, "COMPLETED", "Stored result")
            result = mrsm.review_saved_mrsm_batch(stage, source, fields)
            self.assertEqual(result["status"], "NUMERIC_EVIDENCE_INCOMPLETE")
            self.assertEqual(result["numerical_cases_verified"], 0)


if __name__ == "__main__":
    unittest.main()
