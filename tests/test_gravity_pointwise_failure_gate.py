"""Pointwise ETABS/OpenSees reaction residual remains visible in every export.

Synthetic ETABS source only. Does not execute or certify a native solver.
"""
import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from components.validation.gravity_etabs_direct import export_direct


class DirectGravityPointwiseGateTests(unittest.TestCase):
    def test_matching_global_force_does_not_hide_3000kn_point_error(self):
        etabs={
            "joint_reactions":[],"base_reactions":[],"support_displacements":[],
            "source_case_base_reactions":[]}
        comp={
            "difference_kN":0.0,
            "opensees_stiffness_basis":"LEGACY_GROSS_SHELL",
            "node_comparison":{
                "valid_one_to_one_global_z_count":2,
                "complete_one_to_one_global_z":True,
                "max_absolute_nodal_difference_kN":3041.266,
                "sum_absolute_nodal_difference_kN":6082.532,
                "rms_nodal_difference_kN":3041.266,
                "pointwise_screening_status":
                    "POINTWISE_RESIDUAL_EXCEEDS_NUMERICAL_SCREEN"},
            "top_node_discrepancies":[
                {"etabs_point":"263","opensees_node":"36",
                 "delta_etabs_minus_opensees_kN":-3041.266,
                 "abs_delta_kN":3041.266}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            out=export_direct(tmp,etabs,comp)
            saved=json.loads((out/"Direct_Gravity_Comparison.json").read_text())
            self.assertEqual(saved["difference_kN"],0.)
            workbook=load_workbook(
                out/"ETABS_OpenSees_Direct_Gravity_Comparison.xlsx",read_only=True)
            self.assertIn("Pointwise reaction gate",workbook.sheetnames)
            self.assertIn("Largest nodal differences",workbook.sheetnames)
            rows=list(workbook["Pointwise reaction gate"].values)
            results={r[0]:r[1] for r in rows[1:]}
            self.assertAlmostEqual(
                results["max_absolute_nodal_difference_kN"],3041.266)
            self.assertEqual(results["ENGINEERING_ACCEPTANCE"],"NOT_CERTIFIED")
            self.assertEqual(results["pointwise_screening_status"],
                             "POINTWISE_RESIDUAL_EXCEEDS_NUMERICAL_SCREEN")
            workbook.close()

    def test_workflow_source_always_refreshes_case_on_tk_thread(self):
        source=(Path(__file__).resolve().parents[1]/"components"/"gravity"/
                "gui_and_reports.py").read_text(encoding="utf-8-sig")
        self.assertIn("self.win.after(0,self._refresh_case_reaction)",source)
        self.assertIn("GRAVITY_POINTWISE_REACTION_MISMATCH",source)
        self.assertIn("GRAVITY POINTWISE MISMATCH",source)


if __name__=="__main__":
    unittest.main()
