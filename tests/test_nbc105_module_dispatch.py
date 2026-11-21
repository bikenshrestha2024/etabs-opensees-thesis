"""All ten NBC 105:2025 clause modules are callable through a stable JSON API."""
import unittest
from components.nbc105.dispatch import available_operations, run_operation


class ClauseDispatch(unittest.TestCase):
    def test_every_clause_is_registered_and_has_operations(self):
        available=available_operations()
        self.assertEqual(set(available),set(range(1,11)))
        for number in range(1,11):
            self.assertTrue(available[number],f"Clause {number} has no callable APIs")

    def test_clause10_component_factor(self):
        result=run_operation(10,"component_amplification_factor",{
            "building_period_s":1.0,"component_period_s":1.25})
        self.assertEqual(result["clause"],10)
        self.assertAlmostEqual(result["result"],1.75)
        self.assertEqual(result["status"],"CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE")

    def test_clause3_95m_requires_dynamic_analysis(self):
        result=run_operation(3,"esm_applicability",{
            "height_m":95.,"period_s":1.98,"irregular":True,"limit_state":"ULS"})
        self.assertFalse(result["result"]["permitted"])

    def test_invalid_selection_cannot_execute_internal_functions(self):
        for number,operation in [(10,"_positive"),(10,"__import__"),
                                 (11,"component_design_force"),(1,"__class__")]:
            with self.assertRaises(ValueError):
                run_operation(number,operation,{})

    def test_no_provided_data_is_approved_as_engineering_evidence(self):
        for clause,operation,args in [
            (2,"verification_check",{"uls":True,"sls":True,"overturning":True,
               "sliding":True,"foundation":True,"evacuation_components":True}),
            (6,"distribution_exponent",{"period_s":1.5}),
            (9,"history_time_step_limit_s",{"T1":1.5,"Tn":.03,
                                             "record_digitization_dt_s":.02})
        ]:
            response=run_operation(clause,operation,args)
            self.assertEqual(response["status"],"CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE")
            self.assertIn("source_clause",response)


if __name__=="__main__":
    unittest.main()
