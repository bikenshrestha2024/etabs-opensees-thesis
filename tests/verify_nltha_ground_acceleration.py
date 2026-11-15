"""Pure-function relative versus absolute acceleration and orientation checks."""
import unittest
from components.nonlinear_time_history.ground_acceleration import (
 applied_ground_acceleration,relative_to_absolute_floor_acceleration
)

class GroundAccelerationTests(unittest.TestCase):
 def setUp(self):
    self.records=[([0.,.1,.2],.01,"g"),([0.,-.3,-.1],.01,"g")]

 def test_xy_interpolation_and_unit_conversion(self):
    ax,ay=applied_ground_acceleration(self.records,time_s=.015,orientation="XY")
    self.assertAlmostEqual(ax,.15*9.80665)
    self.assertAlmostEqual(ay,-.2*9.80665)

 def test_yx_swaps_only_axis_not_factor(self):
    ax,ay=applied_ground_acceleration(self.records,time_s=.015,orientation="YX")
    self.assertAlmostEqual(ax,-.2*9.80665)
    self.assertAlmostEqual(ay,.15*9.80665)

 def test_diagnostics_zero_and_end(self):
    self.assertEqual(applied_ground_acceleration(self.records,time_s=.005,
                            orientation="XY",excitation="ZERO"),(0.,0.))
    self.assertEqual(applied_ground_acceleration(self.records,time_s=.03,
                            orientation="XY"),(0.,0.))
    ax,ay=applied_ground_acceleration(self.records,time_s=.01,orientation="XY",
                              excitation="X")
    self.assertAlmostEqual(ax,.1*9.80665)
    self.assertEqual(ay,0)

 def test_relative_absolute_distinction(self):
    self.assertEqual(relative_to_absolute_floor_acceleration((2.,-1.,.1),(3.,4.)),(5.,3.))

 def test_nonfinite_path_ordinates_and_floor_acceleration_rejected(self):
    for invalid in (float("nan"), float("inf"), -float("inf")):
       with self.subTest(value=str(invalid)):
          bad=[([0.,invalid,.2],.01,"g"),self.records[1]]
          with self.assertRaisesRegex(ValueError,"Nonfinite ground-motion"):
             applied_ground_acceleration(bad,time_s=.015,orientation="XY")
          with self.assertRaisesRegex(ValueError,"Nonfinite relative"):
             relative_to_absolute_floor_acceleration((invalid,0.),(0.,0.))
          with self.assertRaisesRegex(ValueError,"Nonfinite relative"):
             relative_to_absolute_floor_acceleration((0.,0.),(invalid,0.))

 def test_acceleration_overflow_after_conversion_or_addition_rejected(self):
    huge=[([1e308,1e308],.01,"g"),self.records[1]]
    with self.assertRaisesRegex(ValueError,"Nonfinite converted ground"):
       applied_ground_acceleration(huge,time_s=.005,orientation="XY")
    with self.assertRaisesRegex(ValueError,"Nonfinite reconstructed absolute"):
       relative_to_absolute_floor_acceleration((1e308,0.),(1e308,0.))

 def test_unsupported_units_and_orientation(self):
    with self.assertRaises(ValueError):
       applied_ground_acceleration(self.records,time_s=.01,orientation="XZ")
    with self.assertRaises(ValueError):
       applied_ground_acceleration([([0,1],.01,"cm/s2"),self.records[1]],
                                   time_s=.01,orientation="XY")

if __name__=="__main__":unittest.main()
