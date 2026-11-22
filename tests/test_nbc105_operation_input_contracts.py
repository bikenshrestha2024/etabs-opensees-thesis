"""Every exported NBC 105 operation must offer a truthful editable JSON signature.

This software-layer suite does not certify NBC provision coverage, ETABS
structural equivalence, or building detailing and demands.
"""
import json
import unittest

from components.nbc105.dispatch import (
    available_operations, available_annex_operations,
    operation_input_spec, annex_operation_input_spec, run_operation,
)


class NBCOperationInputContractTests(unittest.TestCase):
    def test_all_ten_clauses_have_json_input_templates(self):
        for clause, names in available_operations().items():
            self.assertTrue(names, f"Clause {clause} exposes no operations")
            for operation in names:
                with self.subTest(clause=clause, operation=operation):
                    spec=operation_input_spec(clause, operation)
                    self.assertEqual(set(spec["template"]),
                                     {p["name"] for p in spec["parameters"]})
                    self.assertEqual(set(spec["required"]) |
                                     set(spec["optional"]),
                                     set(spec["template"]))
                    self.assertFalse(set(spec["required"]) &
                                     set(spec["optional"]))
                    self.assertEqual(json.loads(json.dumps(spec["template"])),
                                     spec["template"])

    def test_every_annex_rule_has_explicit_json_template(self):
        for annex, names in available_annex_operations().items():
            for operation in names:
                with self.subTest(annex=annex, operation=operation):
                    spec=annex_operation_input_spec(annex, operation)
                    self.assertIsInstance(spec["template"],dict)
                    json.dumps(spec,allow_nan=False)

    def test_screenshot_accidental_eccentricity_no_longer_has_opaque_error(self):
        spec=operation_input_spec(5,"accidental_eccentricities_m")
        self.assertEqual(spec["required"],["building_width_m"])
        self.assertEqual(spec["template"]["building_width_m"],None)
        with self.assertRaisesRegex(ValueError,"building_width_m"):
            run_operation(5,"accidental_eccentricities_m",{})
        with self.assertRaisesRegex(ValueError,"building_width_m"):
            run_operation(5,"accidental_eccentricities_m",spec["template"])
        response=run_operation(5,"accidental_eccentricities_m",
                               {"building_width_m":24.})
        self.assertAlmostEqual(response["result"][0],-1.2)
        self.assertAlmostEqual(response["result"][1],1.2)
        self.assertEqual(response["status"],
                         "CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE")

    def test_unknown_and_extra_parameter_names_are_not_silently_ignored(self):
        with self.assertRaisesRegex(ValueError,"unexpected keyword"):
            run_operation(5,"accidental_eccentricities_m",
                          {"building_width_m":24.,"other":123})

    def test_gui_uses_schema_on_operation_switch(self):
        from pathlib import Path
        gui=Path(__file__).resolve().parents[1]/"components"/"ui"/"nbc105_settings_panel.py"
        source=gui.read_text(encoding="utf-8-sig")
        self.assertIn('op_box.bind("<<ComboboxSelected>>",load_operation_template)',source)
        self.assertIn("operation_input_spec",source)
        self.assertIn("annex_operation_input_spec",source)
        self.assertIn("entry_cache",source)
        self.assertIn("Source coverage (open gates)",source)
        self.assertIn("audit_source_index(records)",source)


if __name__ == "__main__":
    unittest.main()
