"""Reconciled V170 features against modern main (synthetic only)."""
import unittest
from types import SimpleNamespace
from components.linear_time_history.runner_and_gui import select_diagnostic_duration
from components.modal.gui_and_reports import ModalAuditGUI


class DummyVar:
    def __init__(self):self.value=""
    def set(self,v):self.value=v

class DummyButton:
    def __init__(self):self.state=None
    def configure(self,**kwargs):self.state=kwargs.get("state")

class DummyProcess:
    def __init__(self):self.terminated=False
    def poll(self):return None
    def terminate(self):self.terminated=True


class V170CurrentMain(unittest.TestCase):
    def test_short_trial_is_diagnostic_only(self):
        self.assertEqual(select_diagnostic_duration(45,0.005),(.005,True))
        self.assertEqual(select_diagnostic_duration(45,45),(45.,False))
        self.assertEqual(select_diagnostic_duration(45,80),(45.,False))
        self.assertEqual(select_diagnostic_duration(45,None),(45.,False))

    def test_bad_trial_duration_rejected(self):
        for value in (0,-1,float("nan"),float("inf"),"oops"):
            with self.subTest(value=value):
                with self.assertRaises((ValueError,TypeError)):
                    select_diagnostic_duration(45,value)

    def test_user_stop_terminates_child_and_marks_cancelled(self):
        gui=object.__new__(ModalAuditGUI)
        proc=DummyProcess()
        gui.case_board={"cancelled":False,"process":proc}
        gui.status=DummyVar()
        gui.stop_button=DummyButton()
        gui._stop_modal()
        self.assertTrue(gui.case_board["cancelled"])
        self.assertTrue(proc.terminated)
        self.assertEqual(gui.stop_button.state,"disabled")
        self.assertIn("no partial files",gui.status.value)

if __name__=="__main__":
    unittest.main(verbosity=2)
