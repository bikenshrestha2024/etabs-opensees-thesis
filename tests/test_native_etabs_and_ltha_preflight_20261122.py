"""Source-first regression for native ETABS preview and linear time history numeric UI.

[REF docs/superpowers/plans/2026-11-22-native-etabs-ltha-preflight.md]
No ETABS COM, OpenSees or private EDB required.
"""
import tempfile
import unittest
from pathlib import Path

from components.linear_time_history.runner_and_gui import parse_linear_gui_numeric_inputs
from components.validation.etabs_direct_api import discover_native_base_reactions
from components.validation.etabs_comparison import compare, source_execution_identity
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_etabs_direct_equivalence import FakeSap


class LinearPreflight(unittest.TestCase):
    def values(self):
        return dict(damping="5.0",p1="3.2",p2="0.4",t1x="1.7",
                    t1y="1.9",tnx="0.2",tny="0.16",nmodes="20",
                    x_scale="1",pair_scale="1",trial_duration="")

    def test_blank_periods_list_missing_names_instead_of_float_error(self):
        values=self.values()
        values["p1"]=""
        values["t1x"]=" "
        values["tny"]=""
        with self.assertRaisesRegex(ValueError,"Rayleigh period 1.*T1 X.*Tn Y"):
            parse_linear_gui_numeric_inputs(values,source_state="ULS",
                                           selected_state="ULS",x_only=False)

    def test_selected_sls_conflicts_with_actual_uls_before_missing_periods(self):
        values=self.values()
        values["p1"]=""
        with self.assertRaisesRegex(ValueError,"Selected SLS.*source.*ULS"):
            parse_linear_gui_numeric_inputs(values,source_state="ULS",
                                           selected_state="SLS",x_only=False)

    def test_x_only_ignores_empty_y_and_validates_finite_positive(self):
        v=self.values();v["t1y"]="";v["tny"]=""
        d=parse_linear_gui_numeric_inputs(v,source_state="ULS",selected_state="ULS",x_only=True)
        self.assertIsNone(d["T1_y_s"])
        self.assertAlmostEqual(d["damping_period_1_s"],3.2)
        self.assertIsNone(d["trial_duration_s"])
        v["tnx"]="NaN"
        with self.assertRaisesRegex(ValueError,"Tn X.*finite"):
            parse_linear_gui_numeric_inputs(v,source_state="ULS",selected_state="ULS",x_only=True)
        v["tnx"]="0.2";v["damping"]="5.1"
        with self.assertRaisesRegex(ValueError,"5%"):
            parse_linear_gui_numeric_inputs(v,source_state="ULS",selected_state="ULS",x_only=True)


class NativeETABSObservations(unittest.TestCase):
    def test_actual_source_case_raw_base_reaction_without_guessing_cqc_basis(self):
        with tempfile.TemporaryDirectory() as tmp:
            edb=Path(tmp)/"correct.edb";edb.write_bytes(b"same model source")
            sap=FakeSap(edb)
            evidence=discover_native_base_reactions(sap,edb,max_cases=20)
            self.assertEqual(evidence["source_edb_sha256"],
                             __import__("hashlib").sha256(edb.read_bytes()).hexdigest())
            self.assertEqual(evidence["analysis_equivalence"],"NOT_VERIFIED")
            self.assertEqual(len(evidence["rows"]),1)
            self.assertEqual(evidence["rows"][0]["etabs_case"],"RSX")
            self.assertEqual(evidence["rows"][0]["Fx_kN"],100.)
            self.assertEqual(sap.GetPresentUnits(),3)
            self.assertEqual(sap.Results.Setup.cases,{"RSX":False,"MODAL":True})
            self.assertEqual(sap.Results.Setup.combos,{"ENVELOPE":True})

    def test_wrong_edb_blocks_native_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.edb";p.write_bytes(b"a")
            other=Path(tmp)/"b.edb";other.write_bytes(b"b")
            with self.assertRaisesRegex(ValueError,"source EDB|active ETABS"):
                discover_native_base_reactions(FakeSap(p),other,max_cases=10)

class MRSMExecutionIdentity(unittest.TestCase):
    def test_historical_same_sha_but_unknown_76_support_must_not_be_verified(self):
        self.assertEqual(source_execution_identity({"model_sha256":"abc"}),
                         "MISSING_EXECUTED_SUPPORT_OR_MASS_POLICY")
        self.assertEqual(source_execution_identity({"model_sha256":"abc",
                 "support_case":"SOURCE_76",
                 "seismic_mass_policy":"SOURCE_DISTRIBUTED"}),
                 "DIAGNOSTIC_SUPPORT_CASE_NOT_PRIMARY_32")
        self.assertEqual(source_execution_identity({"model_sha256":"abc",
                 "support_case":"PHYSICAL_32",
                 "seismic_mass_policy":"SOURCE_DISTRIBUTED",
                 "support_case_evidence":{"status":"MATCHED_SELECTED_CASE_NOT_NATIVE_EQUIVALENT"}}),
                 "SOURCE_IDENTIFIED_NOT_NATIVE_ETABS_APPROVED")

    def test_unverified_legacy_case_never_passes_with_same_number(self):
        source=dict(method="MRSM",limit_state="ULS",case="X_E0",axis="X",
                    location="BASE",metric="base_shear",unit="kN",
                    basis="CQC_force_scaled",value=100.,
                    source_execution_status="MISSING_EXECUTED_SUPPORT_OR_MASS_POLICY")
        ref={k:v for k,v in source.items() if k!="source_execution_status"}
        result=compare([source],[ref],{"assumptions_verified":True})
        self.assertEqual(result[0]["etabs_value"],100.)
        self.assertEqual(result[0]["status"],"NOT_COMPARABLE")
        self.assertIn("support",result[0]["note"].lower())

if __name__=="__main__":
    unittest.main()
