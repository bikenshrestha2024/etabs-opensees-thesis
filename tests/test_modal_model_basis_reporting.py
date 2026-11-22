"""Modal reporting must not call 76 mesh/restraint records foundations or accept
unverified GUI Rayleigh values as values measured in the modal solve.

Synthetic provenance tests only. No structural solver is run.
[REF docs/source/components/modal/analysis.py.md modal model basis]
"""
import unittest
from components.modal.analysis import modal_model_basis_report
from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32
from components.modal.gui_and_reports import _runner_source


class ModalPhysicalBasisEvidenceTests(unittest.TestCase):
    def test_76_mapped_source_restraints_are_not_76_physical_foundations(self):
        supports={str(i):[1,1,1,1,1,1] for i in PROJECT_PRIMARY_32}
        supports.update({str(1000+i):[1,1,1,1,1,1] for i in range(44)})
        audit=modal_model_basis_report(
            {"supports": supports},
            {"linear_shell_stiffness_policy":"LEGACY_GROSS_SHELL"},
            "ULS",
            {"rayleigh_x_s":1.661965934952554,
             "rayleigh_y_s":2.383340567406627})
        self.assertEqual(audit["exported_restraint_point_count"],76)
        self.assertEqual(audit["user_confirmed_physical_foundation_count"],32)
        self.assertEqual(audit["extra_exported_restrained_point_count"],44)
        self.assertEqual(audit["case_stiffness_basis"],"LEGACY_GROSS_SHELL")
        self.assertEqual(audit["physical_model_equivalence"],"NOT_VERIFIED")
        self.assertEqual(audit["rayleigh_period_provenance"],"EXTERNAL_GUI_INPUT_NOT_COMPUTED_BY_MODAL_SOLVER")
        self.assertIn("76",audit["warnings"][0])

    def test_32_compatible_export_still_cannot_claim_native_model_equivalence(self):
        support={str(i):[1,1,1,1,1,1] for i in PROJECT_PRIMARY_32}
        result=modal_model_basis_report(
            {"supports":support}, {"elastic_etabs_comparison":{"ULS":{}}},
            "ULS", {})
        self.assertEqual(result["exported_restraint_point_count"],32)
        self.assertEqual(result["extra_exported_restrained_point_count"],0)
        self.assertEqual(result["case_stiffness_basis"],"ETABS_ELASTIC_COMPARISON")
        self.assertEqual(result["physical_model_equivalence"],"NOT_VERIFIED")
        self.assertIsNone(result["external_rayleigh_X_s"])

    def test_missing_source_model_and_stiffness_fails_visible(self):
        result=modal_model_basis_report({}, {}, "SLS",
                                        {"rayleigh_y_s":2.4})
        self.assertEqual(result["physical_model_equivalence"],"NOT_VERIFIED")
        self.assertEqual(result["source_support_identity_status"],"UNAVAILABLE")
        self.assertEqual(result["case_stiffness_basis"],"LEGACY_GROSS_SHELL")

    def test_modal_generated_runner_persists_model_basis_and_provenance(self):
        code=_runner_source("C:/temp/model.py","C:/temp/out",40,
                            "PythonSparse",{"rayleigh_x_s":1.8},
                            None,None,"ULS")
        self.assertIn("modal_model_basis_report",code)
        self.assertIn("modal_model_basis_audit",code)
        self.assertIn("MODAL MODEL BASIS",code)
        self.assertIn("GUI_INPUT",code)


if __name__=="__main__":
    unittest.main()
