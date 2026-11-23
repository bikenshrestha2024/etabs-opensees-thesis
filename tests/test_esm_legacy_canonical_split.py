"""Regression: legacy ESM UI output and canonical stage writers must agree.

Synthetic filesystem only; no ETABS, OpenSees, EDB or private workbook.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from components.equivalent_static.organized_exports import (
    _exact_calculation_roots,
    _latest_batch_status,
    _source_files,
    build_combined_esm_export,
)

CASE = "ULS_X+_E0"
RUNNER = f"OpenSees_Direct_NBC105_ESM_Load_And_Static_Analysis_{CASE}_V111.py"


def _make_split_case(tmp):
    source = Path(tmp)
    legacy = source / "OpenSees_Analysis_Results" / "ULS_Floor_3_MODEL_A"
    canonical = source / "03_ESM" / "RUNS" / "ULS" / "ULS_Floor_3_MODEL_A"
    legacy.mkdir(parents=True)
    canonical.mkdir(parents=True)
    payload = {
        "response_case": CASE, "limit_state": "ULS", "period_s": 1.9,
        "period_exponent_k": 1.7, "stories": [], "code_eligible": False,
        "esm_eligibility": "ULS high-rise comparison only",
        "site_subsoil_status": "NOT VERIFIED",
    }
    names = (
        f"NBC105_ESM_Calculation_{CASE}_V111.json",
        f"NBC105_ESM_Storey_Forces_{CASE}_V111.csv",
        RUNNER,
        f"NBC105_ESM_Force_Profile_{CASE}_V111.png",
        f"NBC105_ESM_OpenSees_Response_{CASE}.csv",
    )
    (canonical / names[0]).write_text(json.dumps(payload), encoding="utf-8")
    (canonical / names[1]).write_text("story_number,floor_force_kN\n1,100\n", encoding="utf-8")
    (canonical / names[2]).write_text("# synthetic only\n", encoding="utf-8")
    (canonical / names[3]).write_bytes(b"synthetic plot")
    (canonical / names[4]).write_text("response_case,U_elastic_m\n", encoding="utf-8")
    # A prior or unrelated model must NEVER be picked merely by its filename.
    sibling = source / "03_ESM" / "RUNS" / "ULS" / "ULS_Floor_3_OTHER_MODEL"
    sibling.mkdir(parents=True)
    (sibling / f"NBC105_ESM_Calculation_{CASE}_V111.json").write_text(
        json.dumps({"response_case": CASE, "period_s": 900}), encoding="utf-8"
    )
    return legacy, canonical, names


class ESMCanonicalLegacySplitTests(unittest.TestCase):
    def test_legacy_selected_root_copies_all_exact_case_artifacts(self):
        with TemporaryDirectory() as tmp:
            legacy, canonical, names = _make_split_case(tmp)
            roots = _exact_calculation_roots(legacy)
            self.assertIn(canonical, roots)
            selected = {path.name for _role, path in _source_files(legacy, roots)}
            self.assertTrue(set(names).issubset(selected), set(names) - selected)
            report = build_combined_esm_export(legacy)
            manifest = json.loads(Path(report["manifest"]).read_text(encoding="utf-8"))
            sources = {Path(row["source_path"]).resolve() for row in manifest["files"]}
            self.assertTrue(
                {canonical / name for name in names}.issubset(sources),
                "The review ZIP must include calculation, runner, plot and response"
            )
            self.assertEqual(report["cases"], 1)

    def test_status_matched_to_runner_in_canonical_case_root(self):
        with TemporaryDirectory() as tmp:
            legacy, canonical, names = _make_split_case(tmp)
            batch = legacy / "ESM_Runner_Status" / "20261123_075000"
            batch.mkdir(parents=True)
            status = batch / "CASE_STATUS.json"
            row = {"case": RUNNER, "runner_path": str(canonical / RUNNER),
                   "status": "SUCCESS", "return_code": 0, "elapsed_s": 90}
            status.write_text(json.dumps([row]), encoding="utf-8")
            roots = _exact_calculation_roots(legacy)
            actual = _latest_batch_status(legacy, roots)
            self.assertEqual(actual["status"], "COMPLETE_SOLVER_ONLY")
            self.assertEqual(actual["expected_scripts"], 1)
            # A missing second runner cannot be hidden by the older success.
            second = canonical / "OpenSees_Direct_NBC105_ESM_Load_And_Static_Analysis_ULS_Y+_E0_V111.py"
            second.write_text("# not executed\n", encoding="utf-8")
            actual = _latest_batch_status(legacy, roots)
            self.assertEqual(actual["status"], "PARTIAL_OR_FAILED")
            self.assertIn(second.name, actual["missing_cases"])


if __name__ == "__main__":
    unittest.main()
