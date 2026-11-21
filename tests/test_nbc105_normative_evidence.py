"""Pins that tie normative-register rows to printed NBC 105:2025 values.

[REF NBC105-2025 normative register] Each test holds an independent printed
value (read from the user's PDF page images, printed page cited) and compares
it with the reference module. These are unit tests of code-versus-print
transcription. They are not engineering acceptance of any building.
"""
import unittest

from components.nbc105.clause_02_general_principles import RETURN_PERIOD_YEARS
from components.nbc105.clause_03_scope_of_analysis import load_combination_coefficients


def _rows(**kw):
    return {r["name"]: r for r in load_combination_coefficients(**kw)}


class Clause2And3Pins(unittest.TestCase):
    def test_return_periods_475_and_20(self):
        # printed p.10: 475 years (life safety), 20 years (damage limitation)
        self.assertEqual(RETURN_PERIOD_YEARS, {"ULS": 475, "SLS": 20})

    def test_parallel_lsm_rows_match_printed_equations(self):
        # printed p.19, Eq. 3.6(1)
        rows = _rows(system="parallel", method="LSM", occupancy="other", additional_kind="snow")
        self.assertEqual((rows["ULS_GRAVITY"]["DL"], rows["ULS_GRAVITY"]["LL"]), (1.2, 1.5))
        a = rows["ULS_GRAVITY_ADDITIONAL"]
        self.assertEqual((a["DL"], a["LL"], a["S"]), (1.2, 0.5, 1.2))
        for lead, key in (("X", "Ex"), ("Y", "Ey")):
            for sign, tag in ((1, "POS"), (-1, "NEG")):
                e = rows[f"ULS_E_{lead}_{tag}"]
                self.assertEqual((e["DL"], e["LL"], e[key]), (1.0, 0.3, float(sign)))
                s = rows[f"ULS_STABILITY_{lead}_{tag}"]
                self.assertEqual((s["DL"], s["LL"], s[key]), (0.9, 0.0, float(sign)))
        self.assertEqual(len(rows), 2 + 8)

    def test_nonparallel_lsm_rows_match_printed_equations(self):
        # printed p.20, Eq. 3.6(2): +/-(Ex +/- 0.3Ey) and +/-(Ey +/- 0.3Ex)
        rows = _rows(system="nonparallel", method="LSM", occupancy="storage")
        e = rows["ULS_E_XNEG_YPOS"]
        self.assertEqual((e["DL"], e["LL"], e["Ex"], e["Ey"]), (1.0, 0.6, -1.0, 0.3))
        s = rows["ULS_STABILITY_YPOS_XNEG"]
        self.assertEqual((s["DL"], s["LL"], s["Ex"], s["Ey"]), (0.9, 0.0, -0.3, 1.0))
        self.assertEqual(len([n for n in rows if n.startswith("ULS_E_")]), 8)
        self.assertEqual(len([n for n in rows if n.startswith("ULS_STABILITY_")]), 8)

    def test_additional_load_multipliers_lsm_and_wsm(self):
        # printed pp.19-21: S = 1.2 snow, 1.2 static liquid, 1.5 earth (LSM); 1.0 each (WSM)
        for kind, lsm in (("snow", 1.2), ("static liquid", 1.2), ("earth pressure", 1.5)):
            self.assertEqual(_rows(system="parallel", method="LSM", occupancy="other",
                                   additional_kind=kind)["ULS_GRAVITY_ADDITIONAL"]["S"], lsm)
            w = _rows(system="parallel", method="WSM", occupancy="other", additional_kind=kind)
            self.assertEqual(w["WSM_GRAVITY_ADDITIONAL"]["S"], 1.0)
            self.assertEqual((w["WSM_GRAVITY_ADDITIONAL"]["DL"], w["WSM_GRAVITY_ADDITIONAL"]["LL"]), (1.0, 1.0))
        w = _rows(system="parallel", method="WSM", occupancy="storage")
        self.assertEqual((w["WSM_STABILITY_X_POS"]["DL"], w["WSM_STABILITY_X_POS"]["Ex"]), (0.7, 0.7))
        self.assertEqual((w["WSM_E_Y_NEG"]["LL"], w["WSM_E_Y_NEG"]["Ey"]), (0.6, -0.7))
        with self.assertRaises(ValueError):
            load_combination_coefficients(system="parallel", method="LSM", occupancy="other",
                                          additional_kind="wind")


class Clause5Pins(unittest.TestCase):
    def test_serviceability_ductility_is_one_for_every_table_5_2_row(self):
        # printed 5.3.2.2 (p.31): Rs = 1 for the serviceability limit state
        from components.nbc105.clause_05_dynamic_characteristics import table_5_2_system_factors
        for row in range(1, 22):
            self.assertEqual(table_5_2_system_factors(row)["Rs"], 1.0)

    def test_printed_table_5_2_independent_values(self):
        # printed p.32 (text and layout compared by script on 2026-11-21): (Rmu, Omega_u, Omega_s)
        from components.nbc105.clause_05_dynamic_characteristics import table_5_2_system_factors
        printed = {1: (4, 1.5, 1.25), 2: (4, 1.5, 1.25), 3: (4, 1.5, 1.25), 4: (4, 1.5, 1.25),
                   5: (4, 1.5, 1.25), 6: (3, 1.3, 1.15), 7: (3, 1.3, 1.15), 8: (4, 1.5, 1.25),
                   9: (3, 1.3, 1.15), 10: (3, 1.3, 1.15), 11: (2.5, 1.2, 1.1), 12: (2.5, 1.2, 1.1),
                   13: (2.0, 1.2, 1.1), 14: (4, 1.5, 1.25), 15: (4, 1.5, 1.25), 16: (3.5, 1.4, 1.2),
                   17: (3.5, 1.4, 1.2), 18: (4, 1.5, 1.25), 19: (3.5, 1.4, 1.2), 20: (3.5, 1.4, 1.2),
                   21: (2.5, 1.2, 1.1)}
        self.assertEqual(len(printed), 21)
        for row, vals in printed.items():
            e = table_5_2_system_factors(row)
            self.assertEqual((e["Rmu"], e["Omega_u"], e["Omega_s"]), tuple(float(v) for v in vals), row)


class ProductionIrregularityPins(unittest.TestCase):
    """components.validation.response_checks.irregularity: 5.4.1.1, 5.4.1.3 and 5.4.1.5."""

    @staticmethod
    def _data(masses, widths):
        nodes, mass, frames, diaphragms = {}, {}, [], []
        k = 0
        for i, (m, (wx, wy)) in enumerate(zip(masses, widths)):
            z = 3.0 * (i + 1)
            ids = []
            for xyz in ((0.0, 0.0, z), (wx, 0.0, z), (0.0, wy, z)):
                k += 1
                nodes[str(k)] = list(xyz)
                ids.append(k)
            mass[str(ids[0])] = m
            frames.append({"category": "COLUMN", "nodes": ids})
            diaphragms.append({"master_xyz": [0.0, 0.0, z], "storey_number": i + 1})
        return {"base_z_m": 0.0, "diaphragms": diaphragms, "nodes": nodes,
                "nodal_mass": mass, "frames": frames, "shells": []}

    def _checks(self, data, **kw):
        from components.validation import response_checks
        return response_checks.irregularity(data, **kw)["checks"]

    def test_mass_irregularity_strictly_more_than_50_percent_of_lighter_storey(self):
        # printed 5.4.1.5 (p.34): difference of more than 50 percent between consecutive storey masses
        checks = self._checks(self._data([100.0, 150.0, 150.0], [(10, 10)] * 3))
        mass = [c for c in checks if c["clause"] == "5.4.1.5"]
        self.assertEqual([c["status"] for c in mass], ["PASS", "PASS"])
        checks = self._checks(self._data([100.0, 150.1, 150.1], [(10, 10)] * 3))
        mass = [c for c in checks if c["clause"] == "5.4.1.5"]
        self.assertEqual([c["status"] for c in mass], ["IRREGULAR", "PASS"])

    def test_vertical_geometric_irregularity_strictly_more_than_130_percent(self):
        # printed 5.4.1.3 (p.33): horizontal dimension more than 130 percent of the adjacent storey
        checks = self._checks(self._data([100.0] * 3, [(10, 10), (13.0, 10), (13.0, 10)]))
        geo = [c for c in checks if c["clause"] == "5.4.1.3" and c["check"].endswith("X")]
        self.assertEqual([c["status"] for c in geo], ["PASS", "PASS"])
        checks = self._checks(self._data([100.0] * 3, [(10, 10), (13.1, 10), (13.1, 10)]))
        geo = [c for c in checks if c["clause"] == "5.4.1.3" and c["check"].endswith("X")]
        self.assertEqual([c["status"] for c in geo], ["IRREGULAR", "PASS"])

    def test_weak_story_strictly_below_80_percent_of_story_above(self):
        # printed 5.4.1.1 (p.33)
        data = self._data([100.0, 100.0], [(10, 10)] * 2)
        rows = lambda a: [{"storey_number": 1, "lateral_strength_kN": a},
                          {"storey_number": 2, "lateral_strength_kN": 100.0}]
        weak = lambda a: [c for c in self._checks(data, capacity_rows=rows(a)) if c["clause"] == "5.4.1.1"][0]
        self.assertEqual(weak(80.0)["status"], "PASS")
        self.assertEqual(weak(79.9)["status"], "IRREGULAR")


class Clause8And7Pins(unittest.TestCase):
    def test_elastic_member_action_divided_by_reviewed_uls_ductility(self):
        # printed 8.1.3.2 (p.43): member actions divided by the ULS ductility factor
        from components.nbc105.clause_08_elastic_time_history import elastic_member_action_for_design
        self.assertAlmostEqual(elastic_member_action_for_design(120.0, 4.0), 30.0)
        self.assertAlmostEqual(elastic_member_action_for_design(-120.0, 4.0), -30.0)
        for bad in (0.0, -1.0, float("nan")):
            with self.assertRaises(ValueError):
                elastic_member_action_for_design(10.0, bad)

    def test_modal_mass_coverage_returns_sum_not_acceptance(self):
        # printed 7.3 (p.40): the 90 percent comparison is a separate project check
        from components.nbc105.clause_07_modal_response_spectrum import modal_mass_coverage
        self.assertAlmostEqual(modal_mass_coverage([60.0, 25.0]), 85.0)
        self.assertAlmostEqual(modal_mass_coverage([60.0, 30.0]), 90.0)


class Clause10Pins(unittest.TestCase):
    def test_table_10_3_every_printed_row(self):
        # printed Table 10-3 (p.51): four 1.5 classes and 'all other components' 1.0
        from components.nbc105.clause_10_parts_and_components import component_importance_factor
        for key in ("hazardous", "life safety", "public storage", "emergency"):
            self.assertEqual(component_importance_factor(key), 1.5)
        self.assertEqual(component_importance_factor("other"), 1.0)
        with self.assertRaises(ValueError):
            component_importance_factor("unlisted class")

    def test_table_10_1_boundary_at_half_second_is_continuous(self):
        # printed Table 10-1 (p.50) gives ap = 1.0 for |T1-Tp| > 0.5 and a linear
        # interpolation between 2.5 (0) and 1.0 (0.5): both readings give 1.0 at 0.5
        from components.nbc105.clause_10_parts_and_components import component_amplification_factor
        just_inside = component_amplification_factor(1.0, 1.0 + 0.5 - 1e-9)
        self.assertAlmostEqual(just_inside, 1.0, places=6)
        self.assertEqual(component_amplification_factor(1.0, 1.5), 1.0)
        self.assertEqual(component_amplification_factor(1.5, 1.0), 1.0)

    def test_service_cutoff_never_above_0_2g(self):
        # printed 10.2 (p.49)
        from components.nbc105.clause_10_parts_and_components import shutdown_threshold_g
        self.assertEqual(shutdown_threshold_g(0.2), 0.2)
        with self.assertRaises(ValueError):
            shutdown_threshold_g(0.2001)

    def test_ductility_table_does_not_auto_accept_higher_value(self):
        # printed 10.3.2 (p.50): up to 3.5 only if supported by research
        from components.nbc105.clause_10_parts_and_components import component_ductility_factor
        with self.assertRaises(ValueError):
            component_ductility_factor("high")

    def test_fp_equation_printed_form_independent_arithmetic(self):
        # printed Eq. 10.3(1): Fp = Z (1 + hp/H) (ap/mu_p) Ip Wp (page image p.49)
        from components.nbc105.clause_10_parts_and_components import component_design_force
        z, hp, H, ap, mu, ip, wp = 0.35, 20.0, 95.0, 1.0, 1.5, 1.0, 10.0
        expected = z * (1 + hp / H) * (ap / mu) * ip * wp
        self.assertAlmostEqual(component_design_force(z=z, hp=hp, H=H, ap=ap, mu_p=mu, Ip=ip, Wp=wp), expected)


if __name__ == "__main__":
    unittest.main()
