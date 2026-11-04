"""Modal GUI cancellation is not a native eigenanalysis failure or PASS."""
import unittest
from components.shared.case_status import modal_exit_status

class ModalStopStatusTests(unittest.TestCase):
 def test_cancelled_even_if_solver_terminates_with_nonzero_exit(self):
  self.assertEqual(modal_exit_status(True,-15),"CANCELLED")
  self.assertEqual(modal_exit_status(True,1),"CANCELLED")
  self.assertEqual(modal_exit_status(True,0),"CANCELLED")
 def test_uncancelled_failure_and_completion_distinct(self):
  self.assertEqual(modal_exit_status(False,1),"FAILED")
  self.assertEqual(modal_exit_status(False,0),"COMPLETED")

if __name__=="__main__":
 unittest.main()
