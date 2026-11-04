"""Horizontal three-dimensional OpenSees input mapping / NBC vertical scope."""
import unittest
from components.nonlinear_time_history.nbc105_horizontal_input import (
 vertical_acceleration_review,component_direction_mapping,unit_and_scale,
 applied_motion_manifest)
class EarthquakeInputTests(unittest.TestCase):
 def test_vertical_not_automatically_waived(self):
    r=vertical_acceleration_review({"horizontal_cantilever_gt_5m":False})
    self.assertEqual(r["status"],"INCOMPLETE_REVIEW_NO_VERTICAL_EXCLUSION")
    self.assertEqual(len(r["unknown"]),4)
 def test_all_negative_review_is_not_blanket_approval(self):
    features={k:False for k in (
      "unsupported_horizontal_span_ge_20m","horizontal_cantilever_gt_5m",
      "prestressed_horizontal_component","beam_supporting_column",
      "base_isolation")}
    r=vertical_acceleration_review(features)
    self.assertEqual(r["status"],"NO_CLAUSE_4_3_TRIGGER_DECLARED_REVIEW_REQUIRED")
 def test_transfer_beam_triggers(self):
    r=vertical_acceleration_review({"horizontal_cantilever_gt_5m":False,
                                   "beam_supporting_column":True})
    self.assertEqual(r["status"],"VERTICAL_ACTION_CONSIDERATION_TRIGGERED")
 def test_xy_yx_swaps_not_simultaneous_x_only(self):
    self.assertEqual(component_direction_mapping("XY"),(("A",1),("B",2)))
    self.assertEqual(component_direction_mapping("YX"),(("B",1),("A",2)))
    with self.assertRaises(ValueError):component_direction_mapping("XZ")
 def test_conversion_exactly_once(self):
    self.assertAlmostEqual(unit_and_scale("g",1.45),9.80665*1.45)
    self.assertAlmostEqual(unit_and_scale("m/s2",1.45),1.45)
    with self.assertRaisesRegex(ValueError,"must be 1.0"):unit_and_scale("g",1.45,already_scaled=True)
    self.assertAlmostEqual(unit_and_scale("g",1.0,already_scaled=True),9.80665)
 def test_two_horizontal_and_same_scale(self):
    base=dict(record_a="a.at2",record_b="b.at2",dt_s=.005,
              units_a="g",units_b="m/s2",pair_scale=1.45)
    x=applied_motion_manifest(orientation="XY",**base)
    y=applied_motion_manifest(orientation="YX",**base)
    self.assertEqual(x["directions"],[1,2])
    self.assertFalse(x["vertical_dof_3_used"])
    self.assertEqual([r["source_component"] for r in x["commands"]],["A","B"])
    self.assertEqual([r["source_component"] for r in y["commands"]],["B","A"])
    self.assertAlmostEqual(y["commands"][0]["path_factor_m_s2"],1.45)
if __name__=="__main__":unittest.main()
