"""Pair spectrum audit inputs and scaling; native record spectrum is separate."""
import tempfile
import unittest
from pathlib import Path
from components.response_spectrum.nbc_pair_spectrum_audit import pair_spectrum_audit

class PairScalingTests(unittest.TestCase):
 def factory(self,fx,fy):
    def eval(path,**kw):
        return {"candidate_factor":fx if path.endswith("x.at2") else fy,
                "target_basis":"TEST_INJECTED_NOT_SPECTRAL_EVIDENCE"}
    return eval
 def paths(self,d):
    x=Path(d)/"x.at2";y=Path(d)/"y.at2"
    x.write_text("x original");y.write_text("y original")
    return x,y
 def run(self,x,y,evaluator):
    return pair_spectrum_audit(x,y,soil_type="C",Z=.45,I=1.,omega_u=1.5,
     R_mu=4.,t1_x_s=3.6,t1_y_s=3.2,tn90_x_s=.15,tn90_y_s=.12,
     evaluator=evaluator)
 def test_select_lower_component_factor(self):
    with tempfile.TemporaryDirectory() as d:
        x,y=self.paths(d)
        result=self.run(x,y,self.factory(1.8,1.4))
        self.assertEqual(result["shared_scale_both_components"],1.4)
        self.assertFalse(result["final_nbc_design_approval"])
        self.assertEqual(len(result["components"][0]["source_sha256"]),64)
        self.assertEqual(x.read_text(),"x original")
 def test_reject_out_of_range_and_dont_clip(self):
    with tempfile.TemporaryDirectory() as d:
        x,y=self.paths(d)
        result=self.run(x,y,self.factory(3.1,1.1))
        self.assertEqual(result["status"],"REJECT_PAIR_OUTSIDE_0.33_TO_3")
        self.assertIsNone(result["shared_scale_both_components"])
 def test_same_record_not_a_pair(self):
    with tempfile.TemporaryDirectory() as d:
        x,y=self.paths(d)
        with self.assertRaisesRegex(ValueError,"different"):
            self.run(x,x,self.factory(1.3,1.1))

if __name__=="__main__":unittest.main()
