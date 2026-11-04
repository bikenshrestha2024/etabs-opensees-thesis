"""No extra spectral multiplier on ALREADY SeismoMatch matched sources."""
import tempfile
import unittest
from pathlib import Path
from components.inputs.records import _enforce_matched_scale, _requires_unit_only_path_scale

class RecordScalePolicy(unittest.TestCase):
 def test_matched_pair_is_unit_only(self):
    with tempfile.TemporaryDirectory() as d:
      a=Path(d)/"A.txt";b=Path(d)/"B.txt"
      for p in (a,b):p.write_text("Time Series matched accelerogram: X\nTime Step: .005 s\nTime(sec) Acc(g)\n")
      self.assertTrue(_requires_unit_only_path_scale(a,b))
      self.assertEqual(_enforce_matched_scale(1.0,a,b),1.0)
      with self.assertRaisesRegex(ValueError,"extra scale=1.0"):
        _enforce_matched_scale(1.8,a,b)

 def test_original_pair_can_have_initial_scale(self):
    with tempfile.TemporaryDirectory() as d:
      a=Path(d)/"A.AT2";b=Path(d)/"B.AT2"
      for p in (a,b):p.write_text("PEER acceleration in units of g\nNPTS=3, DT=.005\n0 1 0\n")
      self.assertFalse(_requires_unit_only_path_scale(a,b))
      self.assertEqual(_enforce_matched_scale(1.4,a,b),1.4)

 def test_mixed_provenance_is_rejected(self):
    with tempfile.TemporaryDirectory() as d:
      a=Path(d)/"A.txt";b=Path(d)/"B.AT2"
      a.write_text("Time Series matched accelerogram: X\nTime Step: .005 s\n")
      b.write_text("PEER raw\n")
      with self.assertRaisesRegex(ValueError,"Mixed original"):
        _enforce_matched_scale(1.,a,b)

if __name__=="__main__": unittest.main()
