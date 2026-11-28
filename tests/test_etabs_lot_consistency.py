"""Regression tests for ETABS analysis-lot consistency diagnostics.

[REF docs/source/components/validation/etabs_lot_consistency.py.md]
Logic tests use tiny hand-built tables. The pinned-evidence tests read the
audit that was produced from the real six-lot export (see the report JSON) and
fail if its measured invariants drift. Neither is native ETABS/OpenSees
acceptance.
"""
import json
import math
import unittest
from pathlib import Path

from components.validation.etabs_lot_consistency import (
    CONTRACT_EVENTS, base_reaction_equilibrium, classify_lot_overlap, classify_time_history_cases,
    derive_primary_support_tags, modal_participation_diagnostics, seismic_mass_source_identity,
    table_data_identity, time_history_step_availability)

EVIDENCE = Path(__file__).resolve().parents[1] / "docs" / "validation" / "20261128_ETABS_LOT_CONSISTENCY_AUDIT.json"


def _joints():
    rows = [("Base", n, x, y, 0.0) for n, (x, y) in enumerate(
        [(0, 6), (0, 12), (6, 0), (6, 6)], 1)]
    rows += [("Story1", 10, 12.0, 9.0, 3.8)]
    return [{"Story": s, "Element Name": str(n), "Global X": x, "Global Y": y, "Global Z": z}
            for s, n, x, y, z in rows]


def _reaction(name, fz=0.0, **extra):
    row = {"Unique Name": str(name), "FX": 0.0, "FY": 0.0, "FZ": fz, "MX": 0.0, "MY": 0.0, "MZ": 0.0}
    row.update(extra)
    return row


class SupportTagTests(unittest.TestCase):
    def test_ordering_rule_reproduces_tags_and_leaves_mesh_points_inert(self):
        # Base joints 1..4 sort by (X,Y) to ranks: (0,6)=1,(0,12)=2,(6,0)=3,(6,6)=4
        reactions = [_reaction(1, 5.0), _reaction(2, 0.0), _reaction(3, 7.0), _reaction(4, 0.0)]
        got = derive_primary_support_tags(_joints(), reactions, expected_tags=(1, 3))
        self.assertEqual(got["derived_support_tags"], [1, 3])
        self.assertEqual(got["support_count"], 2)
        self.assertEqual(got["zero_reaction_count"], 2)
        self.assertEqual(got["status"], "DERIVED_TAGS_MATCH_EXPECTED")
        self.assertEqual(got["physical_support_mapping"], "NOT_VERIFIED")

    def test_wrong_expected_set_is_reported_not_forced(self):
        reactions = [_reaction(1, 5.0), _reaction(2), _reaction(3, 7.0), _reaction(4)]
        got = derive_primary_support_tags(_joints(), reactions, expected_tags=(1, 2))
        self.assertEqual(got["status"], "DERIVED_TAGS_DIFFER_FROM_EXPECTED")
        self.assertEqual(got["missing_from_derived"], [2])
        self.assertEqual(got["unexpected_in_derived"], [3])

    def test_zero_fz_row_with_moment_is_flagged_as_not_inert(self):
        reactions = [_reaction(1, 5.0), _reaction(2, 0.0, MX=3.0), _reaction(3, 7.0), _reaction(4)]
        got = derive_primary_support_tags(_joints(), reactions, expected_tags=(1, 3))
        self.assertEqual(got["zero_reaction_rows_with_nonzero_other_component"], [2])
        self.assertEqual(got["status"], "DERIVED_TAGS_DIFFER_FROM_EXPECTED")

    def test_missing_duplicate_and_ambiguous_inputs_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Reaction joints differ"):
            derive_primary_support_tags(_joints(), [_reaction(1, 1.0)])
        with self.assertRaisesRegex(ValueError, "Duplicate joint reaction"):
            derive_primary_support_tags(_joints(), [_reaction(1, 1.0), _reaction(1, 1.0)])
        twin = _joints() + [{"Story": "Base", "Element Name": "99", "Global X": 0.0, "Global Y": 6.0, "Global Z": 0.0}]
        with self.assertRaisesRegex(ValueError, "share a coordinate"):
            derive_primary_support_tags(twin, [])
        with self.assertRaisesRegex(ValueError, "Missing numeric"):
            derive_primary_support_tags(_joints(), [_reaction(1, ""), _reaction(2), _reaction(3), _reaction(4)])


class MassSourceTests(unittest.TestCase):
    def test_g_is_identified_from_dead_plus_fractional_live(self):
        joints = _joints()
        g = 9.80665
        dead, live = 1000.0, 200.0
        weight_kN = dead + 0.3 * live
        total_kg = weight_kN * 1000.0 / g
        masses = [{"Point Element": "10", "UX": 700.0, "UZ": 0.0},
                  {"Point Element": "1", "UX": 5.0, "UZ": total_kg}]
        got = seismic_mass_source_identity(masses, joints, dead_fz_kN=dead, live_fz_kN=live)
        self.assertEqual(got["best_g_m_s2"], g)
        self.assertAlmostEqual(got["implied_live_fraction_at_best_g"], 0.3, places=9)
        self.assertEqual(got["sum_UX_base_kg"], 5.0)
        self.assertEqual(got["sum_UX_nonbase_kg"], 700.0)
        self.assertGreater(got["g_discrimination_kN"], 0.1)
        self.assertAlmostEqual(got["mass_ratio_if_weight_divided_by_project_g"], g / 9.81)

    def test_duplicate_or_unknown_mass_joint_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate assembled-mass"):
            seismic_mass_source_identity([{"Point Element": "1", "UX": 0, "UZ": 1}] * 2, _joints(),
                                         dead_fz_kN=1.0, live_fz_kN=1.0)
        with self.assertRaisesRegex(ValueError, "absent from joint table"):
            seismic_mass_source_identity([{"Point Element": "77", "UX": 0, "UZ": 1}], _joints(),
                                         dead_fz_kN=1.0, live_fz_kN=1.0)


class TimeHistoryTests(unittest.TestCase):
    def test_max_min_only_is_envelope_only(self):
        rows = [{"Case Type": "NonModHist", "Step Type": s, "Output Case": "Time History A"} for s in ("Max", "Min")]
        rows.append({"Case Type": "LinStatic", "Step Type": "", "Output Case": "Dead"})
        got = time_history_step_availability(rows)
        self.assertEqual(got["status"], "ENVELOPE_ONLY_NO_STEP_SERIES")
        self.assertEqual(got["cases"], 1)

    def test_step_by_step_history_is_recognised(self):
        rows = [{"Case Type": "NonModHist", "Step Type": "Step By Step", "Output Case": "Time History A"}]
        self.assertEqual(time_history_step_availability(rows)["status"], "STEP_SERIES_PRESENT")
        self.assertEqual(time_history_step_availability([])["status"], "NO_NONMODAL_HISTORY_ROWS")

    def test_pairs_extra_events_and_missing_contract_events(self):
        names = {f"Time History {e}" for e in CONTRACT_EVENTS} | {f"Time History {e}-1" for e in CONTRACT_EVENTS}
        names |= {"Time History Tabas", "Time History Tabas-1", "EQX+ P-Delta", "EQX- P Delta"}
        got = classify_time_history_cases(names)
        self.assertEqual(got["events_not_in_contract"], ["Tabas"])
        self.assertEqual(got["contract_events_missing"], [])
        self.assertEqual(got["total_time_history_cases"], 18)
        self.assertTrue(got["p_delta_case_names_mixed_hyphenation"])
        self.assertEqual(got["status"], "CONTRACT_EVENTS_COMPLETE_EXTRA_EVENTS_PRESENT")
        short = classify_time_history_cases({"Time History Gorkha", "Time History Gorkha-1", "Time History Kobe"})
        self.assertEqual(short["unpaired_events"], ["Kobe"])
        self.assertEqual(short["status"], "CONTRACT_EVENTS_INCOMPLETE")
        self.assertIn("Chi Chi", short["contract_events_missing"])


class ModalAndIdentityTests(unittest.TestCase):
    def test_zero_rz_participation_and_rounded_periods_are_flagged(self):
        omega = 2 * math.pi / 0.0343  # exported T=0.034 is the rounded value
        periods = [{"Period": 0.034, "CircFreq": omega * 1.0}, {"Period": 2.427, "CircFreq": 2.5884}]
        ratios = [{"UX": 0.5, "UY": 0.0, "UZ": 0, "RX": 0, "RY": 0, "RZ": 0},
                  {"UX": 0.45, "UY": 0.95, "UZ": 0, "RX": 0, "RY": 0, "RZ": 0}]
        got = modal_participation_diagnostics(periods, ratios)
        self.assertTrue(got["no_torsional_participation"])
        self.assertEqual(got["first_mode_reaching_target"]["UX"], 2)
        self.assertEqual(got["first_mode_reaching_target"]["UY"], 2)
        self.assertNotIn("RZ", got["first_mode_reaching_target"])
        self.assertTrue(got["use_circular_frequency_not_rounded_period"])

    def test_table_identity_ignores_worksheet_row_and_order(self):
        a = [{"worksheet_row": 4, "k": 1, "v": 2.0}, {"worksheet_row": 5, "k": 2, "v": 3.0}]
        b = [{"worksheet_row": 9, "k": 2, "v": 3.0}, {"worksheet_row": 8, "k": 1, "v": 2.0}]
        self.assertTrue(table_data_identity(a, b)["identical"])
        b[0]["v"] = 3.5
        self.assertFalse(table_data_identity(a, b)["identical"])

    def test_combined_lot_that_repeats_its_parts_is_detected(self):
        def lot(*sheets):
            return {"worksheets": [{"sheet": n, "content_sha256": h} for n, h in sheets]}
        audit = {"files": [lot(("A", "h1"), ("B", "h2")), lot(("A", "h1")), lot(("B", "h2")), lot(("C", "h3"))]}
        got = classify_lot_overlap(audit)
        self.assertEqual(got["status"], "COMBINED_LOT_DUPLICATES_PARTS")
        self.assertEqual(got["duplicate_groups"][0]["combined_lot"], 1)
        self.assertEqual(got["duplicate_groups"][0]["duplicated_by_lots"], [2, 3])
        clean = classify_lot_overlap({"files": [lot(("A", "h1")), lot(("A", "other"))]})
        self.assertEqual(clean["status"], "NO_FULL_LOT_OVERLAP")


class EquilibriumTests(unittest.TestCase):
    def test_additive_rows_balance_with_moment_transfer_and_envelopes_are_skipped(self):
        joints = [{"Element Name": "1", "Global X": 2.0, "Global Y": 0.0, "Global Z": 0.0},
                  {"Element Name": "2", "Global X": 0.0, "Global Y": 3.0, "Global Z": 0.0}]
        reactions = [
            {"Unique Name": "1", "Output Case": "Dead", "Case Type": "LinStatic", "Step Type": "", "Step Number": None,
             "FX": 0, "FY": 0, "FZ": 10.0, "MX": 0, "MY": 0, "MZ": 0},
            {"Unique Name": "2", "Output Case": "Dead", "Case Type": "LinStatic", "Step Type": "", "Step Number": None,
             "FX": 0, "FY": 0, "FZ": 4.0, "MX": 0, "MY": 0, "MZ": 0}]
        # about origin: MX = y*FZ = 3*4 = 12 ; MY = -x*FZ = -2*10 = -20
        base = [
            {"Output Case": "Dead", "Case Type": "LinStatic", "Step Type": "", "Step Number": None,
             "FX": 0, "FY": 0, "FZ": 14.0, "MX": 12.0, "MY": -20.0, "MZ": 0, "X": 0, "Y": 0, "Z": 0},
            {"Output Case": "Env", "Case Type": "NonModHist", "Step Type": "Max", "Step Number": None,
             "FX": 99, "FY": 0, "FZ": 0, "MX": 0, "MY": 0, "MZ": 0, "X": 0, "Y": 0, "Z": 0}]
        got = base_reaction_equilibrium(base, reactions, joints)
        self.assertEqual(got["additive_rows_compared"], 1)
        self.assertEqual(got["envelope_rows_not_additive"], 1)
        self.assertLess(got["max_force_residual_kN"], 1e-12)
        self.assertLess(got["max_moment_residual_kNm"], 1e-12)
        base[0]["MY"] = -19.0
        self.assertAlmostEqual(base_reaction_equilibrium(base, reactions, joints)["max_moment_residual_kNm"], 1.0)

    def test_reference_point_shift_is_applied(self):
        joints = [{"Element Name": "1", "Global X": 2.0, "Global Y": 0.0, "Global Z": 0.0}]
        reactions = [{"Unique Name": "1", "Output Case": "D", "Case Type": "LinStatic", "Step Type": "",
                      "Step Number": None, "FX": 0, "FY": 0, "FZ": 10.0, "MX": 0, "MY": 0, "MZ": 0}]
        # about (2,0,0) the load passes through the reference point: zero moment
        base = [{"Output Case": "D", "Case Type": "LinStatic", "Step Type": "", "Step Number": None,
                 "FX": 0, "FY": 0, "FZ": 10.0, "MX": 0, "MY": 0, "MZ": 0, "X": 2.0, "Y": 0, "Z": 0}]
        self.assertLess(base_reaction_equilibrium(base, reactions, joints)["max_moment_residual_kNm"], 1e-12)


@unittest.skipUnless(EVIDENCE.is_file(), "audit evidence JSON not generated yet")
class PinnedRealExportEvidenceTests(unittest.TestCase):
    """Invariants measured on the real six-lot export; update only with a new audit run."""

    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_report_is_reference_only_and_has_no_local_paths(self):
        self.assertEqual(self.doc["engineering_acceptance"], "NOT_VERIFIED")
        text = EVIDENCE.read_text(encoding="utf-8")
        for marker in ("/mnt/", "/home/", "C:\\\\", "D:\\\\", "Users\\\\"):
            self.assertNotIn(marker, text)

    def test_32_physical_supports_and_44_inert_mesh_points(self):
        tags = self.doc["consistency"]["support_tags"]
        self.assertEqual(tags["status"], "DERIVED_TAGS_MATCH_EXPECTED")
        self.assertEqual((tags["base_joint_count"], tags["support_count"], tags["zero_reaction_count"]), (76, 32, 44))
        self.assertEqual(tags["zero_reaction_rows_with_nonzero_other_component"], [])

    def test_mass_source_is_dead_plus_0p3_live_with_etabs_g(self):
        mass = self.doc["consistency"]["seismic_mass_source"]
        self.assertEqual(mass["best_g_m_s2"], 9.80665)
        self.assertLess(abs(mass["best_residual_kN"]), 0.05)
        self.assertAlmostEqual(mass["implied_live_fraction_at_best_g"], 0.3, places=5)
        self.assertEqual(mass["joints_without_mass"], 44)

    def test_base_reactions_equal_joint_reaction_sums_for_additive_rows(self):
        eq = self.doc["base_reaction_equilibrium"]
        self.assertEqual(eq["additive_rows_compared"], 55)
        self.assertEqual((eq["base_rows_without_joint_rows"], eq["joint_rows_without_base_row"]), (0, 0))
        self.assertLess(eq["max_force_residual_kN"], 0.01)
        self.assertLess(eq["max_moment_residual_kNm"], 0.5)

    def test_time_history_is_envelope_only_with_three_extra_events(self):
        cons = self.doc["consistency"]
        self.assertTrue(cons["time_history_step_availability"])
        self.assertEqual(set(cons["time_history_step_availability"].values()), {"ENVELOPE_ONLY_NO_STEP_SERIES"})
        self.assertEqual(cons["time_history_cases"]["events_not_in_contract"], ["Darfield", "San Fernando", "Tabas"])
        self.assertEqual(cons["time_history_cases"]["contract_events_missing"], [])
        self.assertEqual(len(self.doc["time_history_reference_envelopes"]["cases"]), 22)

    def test_combined_fourth_lot_duplicates_its_three_parts(self):
        overlap = self.doc["consistency"]["lot_overlap"]
        self.assertEqual(overlap["status"], "COMBINED_LOT_DUPLICATES_PARTS")
        self.assertEqual(overlap["duplicate_groups"][0]["combined_lot"], 4)
        self.assertEqual(overlap["duplicate_groups"][0]["duplicated_by_lots"], [7, 8, 9])

    def test_modal_ritz_has_no_torsional_participation(self):
        modal = self.doc["consistency"]["modal"]
        self.assertTrue(modal["no_torsional_participation"])
        self.assertEqual(modal["modes"], 15)


if __name__ == "__main__":
    unittest.main()
