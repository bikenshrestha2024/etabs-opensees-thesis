"""ESM GUI input completeness with no fabricated seismic/period parameters."""
import tempfile
import unittest
from pathlib import Path
from components.equivalent_static.calculation_and_gui import ESMGui

class Value:
 def __init__(self,value=""):self.value=value
 def get(self):return self.value
 def set(self,x):self.value=str(x)

class ESMValuesTest(unittest.TestCase):
 def test_missing_aw_is_pending_not_crash(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"weights.csv"
   file.write_text("story_number,height_m,dead_load_kN,storage_live_load_kN,other_live_load_kN\\n1,95,100,0,0\\n")
   g=object.__new__(ESMGui)
   g.path=Value(str(file));g.awx=Value("");g.awy=Value("2")
   g.period_factor=Value("1.25");g.rayleigh_tx=Value("");g.rayleigh_ty=Value("")
   g.computed_x=Value("");g.computed_y=Value("");g.period_note=Value("")
   g._show_empirical()
   self.assertEqual(g.computed_x.get(),"")
   self.assertIn("pending",g.computed_y.get())
   self.assertIn("needs reviewed wall Aw",g.period_note.get())
 def test_two_valid_indices_compute_without_inventing_rayleigh(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/"weights.csv"
   file.write_text("story_number,height_m,dead_load_kN,storage_live_load_kN,other_live_load_kN\\n1,95,100,0,0\\n")
   g=object.__new__(ESMGui)
   g.path=Value(str(file));g.awx=Value("3.6779");g.awy=Value("0.8019")
   g.period_factor=Value("1.25");g.rayleigh_tx=Value("");g.rayleigh_ty=Value("")
   g.computed_x=Value("");g.computed_y=Value("");g.period_note=Value("")
   g._show_empirical()
   self.assertIn("pending Rayleigh run",g.computed_x.get())
   self.assertIn("pending Rayleigh run",g.computed_y.get())

if __name__=="__main__":unittest.main()
