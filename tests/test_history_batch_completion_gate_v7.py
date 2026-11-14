"""Regression tests for recorded LTHA/NLTHA completion, no native solver."""
import tempfile
import unittest
from pathlib import Path

from components.shared.case_status import (
    CaseLedger,update_history_case,history_batch_exit_gate,
)


class HistoryBatchGateTests(unittest.TestCase):
    def test_no_per_case_ok_is_incomplete_even_if_subprocess_exits_zero(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CaseLedger(Path(td)/"cases.json",["Kobe_XY","Kobe_YX"])
            update_history_case(ledger,"[START] Kobe_XY: building model")
            update_history_case(ledger,"[OK] Kobe_XY: complete")
            ledger.finish_pending("No [OK] before child process ended")
            result=history_batch_exit_gate(ledger,0)
            self.assertEqual(result["status"],"INCOMPLETE")
            self.assertEqual(result["completed_cases"],1)
            self.assertIn("Kobe_YX",result["reason"])

    def test_truncated_diagnostic_cannot_pass_full_batch(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CaseLedger(Path(td)/"cases.json",["Gorkha_XY"])
            update_history_case(ledger,"[START] Gorkha_XY: transient")
            update_history_case(ledger,"[TRUNCATED] Gorkha_XY: analyzed 0.1s of 45.29s")
            result=history_batch_exit_gate(ledger,0)
            self.assertEqual(result["status"],"INCOMPLETE")
            self.assertFalse(result["complete"])

    def test_all_structured_ok_is_solver_only_not_engineering_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CaseLedger(Path(td)/"cases.json",["A_XY","A_YX"])
            for case in ("A_XY","A_YX"):
                update_history_case(ledger,f"[START] {case}: started")
                update_history_case(ledger,f"[OK] {case}: completed")
            result=history_batch_exit_gate(ledger,0)
            self.assertEqual(result["status"],"COMPLETED_SOLVER_ONLY")
            self.assertTrue(result["complete"])
            self.assertEqual(result["completed_cases"],2)
            self.assertIn("native review",result["reason"])

    def test_cancel_and_nonzero_exit_are_not_completed(self):
        with tempfile.TemporaryDirectory() as td:
            ledger=CaseLedger(Path(td)/"cases.json",["A_XY"])
            ledger.set("A_XY","COMPLETED","Completed")
            self.assertEqual(history_batch_exit_gate(ledger,1)["status"],"FAILED")
            self.assertEqual(history_batch_exit_gate(ledger,0,cancelled=True)["status"],
                             "INTERRUPTED")
            self.assertEqual(history_batch_exit_gate(None,0)["status"],"INCOMPLETE")


if __name__=="__main__":
    unittest.main()
