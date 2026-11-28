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

    def test_97_mapped_ids_report_actual_extra_mesh_count(self):
        supports={str(i):[1,1,1,1,1,1] for i in PROJECT_PRIMARY_32}
        supports.update({str(2000+i):[1,1,1,1,1,1] for i in range(65)})
        audit=modal_model_basis_report(
            {"supports": supports}, {"linear_shell_stiffness_policy":"LEGACY_GROSS_SHELL"},
            "ULS", {})
        self.assertEqual(audit['exported_restraint_point_count'],97)
        self.assertEqual(audit['extra_exported_restrained_point_count'],65)
        self.assertIn('65 nonprimary',audit['warnings'][0])
        self.assertNotIn('plus 44',audit['warnings'][0])
        self.assertNotIn('768.045','\n'.join(audit['warnings']))

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


class ModalReferenceShapeTests(unittest.TestCase):
    def test_scale_sign_invariance_and_missing_shape_reporting(self):
        from components.modal.analysis import compare_reference_mode_shapes
        centers=[{"Story":"Story1","Diaphragm":"D1","Mass X":1000,"Mass Y":1000,"XCM":0,"YCM":0}]
        shape={"Story":"Story1","Diaphragm":"D1","Diaphragm Mass X":1000,"Diaphragm Mass Y":1000,
               "Diaphragm MMI RZ":2,"X":0,"Y":0,"Z":3,"Output Case":"Modal Ritz","Step Type":"Mode",
               "Step Number":1,"UX":1,"UY":0,"RZ":0}
        periods=[{"Case":"Modal Ritz","Mode":m,"Period":float(m)} for m in (1,2,3,4)]
        master={"node_role":"master","story_name":"Storey_1","node_tag":"9","x_m":"0","y_m":"0","z_m":"3",
                "period_s":"1.1","mode":"1","ux_raw":"-4","uy_raw":"0","rz_raw":"0"}
        ref=[shape,dict(shape,**{"Step Number":2,"UX":0}),dict(shape,**{"Step Number":3,"UX":2})]
        native=[master,dict(master,mode="2",ux_raw="0",uy_raw="2")]
        result=compare_reference_mode_shapes(ref,periods,centers,native,case="Modal Ritz")
        rows=result["rows"]
        self.assertAlmostEqual(rows[0]["mac"],1.)
        self.assertTrue(rows[0]["shared_best_candidate"])
        self.assertEqual(rows[1]["status"],"ZERO_REFERENCE_HORIZONTAL_NORM")
        self.assertEqual(rows[3]["status"],"REFERENCE_SHAPE_NOT_EXPORTED")
        self.assertEqual(rows[0]["runner_up_mac"],0.)
        self.assertEqual(result["native_etabs_opensees_equivalence"],"NOT_VERIFIED")
        for bad in ([dict(master,z_m="4")],native+[master],[dict(master,ux_raw="nan")]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                compare_reference_mode_shapes(ref,periods,centers,bad,case="Modal Ritz")
        with self.assertRaises(ValueError):
            compare_reference_mode_shapes(ref+[shape],periods,centers,native,case="Modal Ritz")


if __name__=="__main__":
    unittest.main()
