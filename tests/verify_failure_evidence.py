import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.nonlinear_time_history.runner_and_gui import (
    _advance_nonlinear_interval,
)


class FakeOps:
    def __init__(self, return_codes, nonfinite=False):
        self.return_codes = iter(return_codes)
        self.nonfinite = nonfinite
        self.time = 0.0
        self.algorithms = []

    def analyze(self, _steps, dt):
        code = next(self.return_codes)
        if code == 0:
            self.time += dt
        return code

    def algorithm(self, _name):
        self.algorithms.append(_name)

    def test(self, *_args):
        pass

    def testIter(self):
        return 1

    def getTime(self):
        return self.time

    def getNodeTags(self):
        return [1]

    def nodeDisp(self, _tag):
        return [0.0] * 6

    def getEleTags(self):
        return [110280]

    def eleResponse(self, _tag, *args):
        if self.nonfinite and args == ("localForce",):
            return [math.nan]
        return [0.0]


class FailureEvidenceTests(unittest.TestCase):
    def test_nonfinite_failure_writes_source_mapped_evidence_before_stopping(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            map_path = root / "element_map.json"
            map_path.write_text(
                json.dumps({"AREA:354": [110280]}), encoding="utf-8"
            )
            evidence_path = root / "First_Step_Failure_Evidence.json"
            with self.assertRaisesRegex(RuntimeError, "evidence saved to"):
                _advance_nonlinear_interval(
                    FakeOps([-3], nonfinite=True),
                    0.005,
                    diagnostics={
                        "evidence_output_path": str(evidence_path),
                        "element_map_path": str(map_path),
                    },
                )
            report = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual(report["algorithm"], "Newton")
            self.assertEqual(report["nonfinite_elements"][0]["source"], "AREA:354")
            self.assertEqual(report["nonfinite_elements"][0]["tag"], 110280)
            self.assertTrue(report["warning"].startswith("Post-failure responses"))

    def test_nonfinite_failure_clock_preserves_evidence(self):
        from components.nonlinear_time_history.failure_evidence import (
            snapshot_failed_step, snapshot_selected_state)
        with tempfile.TemporaryDirectory() as td:
            ops=FakeOps([],nonfinite=True)
            ops.time=float("nan")
            path=Path(td)/"failure.json"
            report=snapshot_failed_step(
                ops,path,algorithm="Newton",dt=.005,return_code=-3,
                suspect_tags=[110280])
            self.assertIsNone(report["analysis_time_s"])
            self.assertEqual(report["analysis_time_status"],"NONFINITE_NAN")
            self.assertEqual(json.loads(path.read_text())["nonfinite_elements"][0]["tag"],110280)
            committed=Path(td)/"last_committed.json"
            selected=snapshot_selected_state(
                ops,committed,suspect_tags=[110280])
            self.assertIsNone(selected["time_s"])
            self.assertEqual(selected["time_status"],"NONFINITE_NAN")
            self.assertTrue(committed.is_file())

    def test_failed_step_evidence_survives_corrupt_mapping(self):
        from components.nonlinear_time_history.failure_evidence import (
            snapshot_failed_step)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            mapping=root/"mapping.json"
            output=root/"failure.json"
            for content in ("{invalid-json", '{"AREA:1":[110280],"AREA:2":[110280]}',
                            '["not a source map"]'):
                with self.subTest(content=content):
                    mapping.write_text(content,encoding="utf-8")
                    report=snapshot_failed_step(
                        FakeOps([],nonfinite=True),output,
                        algorithm="Newton",dt=.005,return_code=-3,
                        element_map_path=mapping,suspect_tags=[110280])
                    self.assertEqual(report["element_map_status"],
                                     "INVALID_SOURCE_MAPPING")
                    self.assertTrue(report["element_map_error"])
                    self.assertEqual(
                        json.loads(output.read_text())["nonfinite_elements"][0]["tag"],
                        110280)
            # Physical cause is NOT inferred from unsupported source mapping.
            self.assertIsNone(report["nonfinite_elements"][0]["source"])

    def test_invalid_capture_bounds_are_rejected_before_writing(self):
        from components.nonlinear_time_history.failure_evidence import (
            snapshot_failed_step, snapshot_selected_state)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"evidence.json"
            for count in (0,-1,1.5,True):
                with self.subTest(count=count),self.assertRaises(ValueError):
                    snapshot_failed_step(FakeOps([]),path,algorithm="Newton",
                        dt=.005,return_code=-3,maximum_findings=count)
            with self.assertRaises(ValueError):
                snapshot_selected_state(FakeOps([]),path,
                                        suspect_tags=[110280],max_values=0)
            self.assertFalse(path.exists())

    def test_recovered_fallback_removes_stale_failure_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            evidence_path = Path(folder) / "First_Step_Failure_Evidence.json"
            result = _advance_nonlinear_interval(
                FakeOps([-3, 0]),
                0.005,
                diagnostics={"evidence_output_path": str(evidence_path)},
            )
            self.assertEqual(result, 1)
            self.assertFalse(evidence_path.exists())

    def test_efficient_recovery_subdivides_before_algorithm_fallbacks(self):
        ops = FakeOps([-3, 0, 0])
        diagnostics = {"efficient_recovery": True}
        accepted = _advance_nonlinear_interval(
            ops, 0.01, max_depth=1, diagnostics=diagnostics)
        self.assertEqual(accepted, 2)
        self.assertEqual(ops.algorithms, ["Newton", "Newton", "Newton"])
        self.assertEqual(diagnostics["bisections"], 1)
        self.assertEqual(diagnostics["failed_attempts"], 1)

    def test_efficient_recovery_keeps_algorithm_fallbacks_at_depth_limit(self):
        ops = FakeOps([-3, 0])
        accepted = _advance_nonlinear_interval(
            ops, 0.01, max_depth=0,
            diagnostics={"efficient_recovery": True})
        self.assertEqual(accepted, 1)
        self.assertEqual(ops.algorithms, ["Newton", "NewtonLineSearch"])


if __name__ == "__main__":
    unittest.main()
