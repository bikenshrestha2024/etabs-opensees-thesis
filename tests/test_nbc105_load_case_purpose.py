"""Read-only NBC 105 seismic-vs-gravity purpose audit tests."""
import unittest

from components.model.load_case_purpose import (
    audit_load_case_purpose,
    classify_load_pattern,
    GRAVITY_ONLY_FACTORS,
    SEISMIC_FACTORS,
)
from components.gravity.storey_loads import classify as storey_classify


class LoadCasePurposeTests(unittest.TestCase):
    def setUp(self):
        self.names = {
            "Self Weight": "DEAD",
            "Dead": "DEAD",
            "Live": "OTHER_LIVE",
            "Storage Live": "STORAGE_LIVE",
            "Roof Live": "ROOF_LIVE",
        }
        self.mass = {name: SEISMIC_FACTORS[category]
                     for name, category in self.names.items()}

    def test_full_gravity_is_all_dead_live_and_roof_live(self):
        gravity = {name: GRAVITY_ONLY_FACTORS[category]
                   for name, category in self.names.items()}
        audit = audit_load_case_purpose(
            "GRAVITY_1.0D_1.0L", gravity, self.mass)
        self.assertEqual(audit["status"], "MATCHES_DECLARED_PURPOSE_FOR_CLASSIFIED_PATTERNS")
        self.assertEqual(audit["purpose"], "FULL_GRAVITY_COMPARISON")
        roof = next(r for r in audit["rows"] if r["pattern"] == "Roof Live")
        self.assertEqual(roof["gravity_factor"], 1.0)
        self.assertEqual(roof["seismic_mass_factor"], 0.0)
        self.assertEqual(roof["expected_gravity_factor"], 1.0)

    def test_seismic_preload_separate_from_gravity_only_case(self):
        factors = dict(self.mass)
        audit = audit_load_case_purpose(
            "AS_CONFIGURED", factors, self.mass)
        self.assertEqual(audit["status"], "MATCHES_DECLARED_PURPOSE_FOR_CLASSIFIED_PATTERNS")
        self.assertEqual(audit["purpose"], "SEISMIC_PRELOAD_CONFIGURED_REVIEW_REQUIRED")
        self.assertIn("must not", audit["comparison_policy"])

    def test_misclassified_roof_live_fails_without_silent_correction(self):
        bad = dict(self.mass)
        bad["Roof Live"] = 0.3
        audit = audit_load_case_purpose("SEISMIC_SOURCE", bad, self.mass)
        self.assertEqual(audit["status"], "REVIEW_REQUIRED")
        self.assertIn("GRAVITY_FACTOR_MISMATCH", audit["issues"][0]["issues"])
        self.assertEqual(bad["Roof Live"], 0.3)

    def test_storage_requires_storage_factor_not_ordinary_live_factor(self):
        bad = dict(self.mass)
        bad["Storage Live"] = 0.3
        audit = audit_load_case_purpose("SEISMIC_SOURCE", bad, bad)
        self.assertIn("SEISMIC_MASS_FACTOR_MISMATCH",
                      next(x for x in audit["issues"]
                           if x["pattern"] == "Storage Live")["issues"])

    def test_unknown_names_require_review_and_declared_categories_are_supported(self):
        report = audit_load_case_purpose("AS_CONFIGURED",
                                        {"Special A": 0.6},
                                        {"Special A": 0.6})
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        accepted = audit_load_case_purpose(
            "AS_CONFIGURED", {"Special A": 0.6}, {"Special A": 0.6},
            category_overrides={"Special A": "STORAGE_LIVE"})
        self.assertEqual(accepted["status"],
                         "MATCHES_DECLARED_PURPOSE_FOR_CLASSIFIED_PATTERNS")
        self.assertEqual(classify_load_pattern("Roof Live"), "ROOF_LIVE")
        self.assertEqual(classify_load_pattern("Storage"), "STORAGE_LIVE")

    def test_story_load_ledger_uses_separate_storage_column(self):
        self.assertEqual(storey_classify("area_load", "Storage Live"),
                         ("storage_live_kN", "LIVE"))
        self.assertEqual(storey_classify("area_load", "Roof Live"),
                         ("roof_live_kN", "LIVE"))

    def test_nan_and_missing_factors_fail_closed(self):
        report = audit_load_case_purpose("SEISMIC_SOURCE",
                                        {"Live": float("nan")}, {})
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        issues = report["issues"][0]["issues"]
        self.assertIn("INVALID_GRAVITY_FACTOR", issues)
        self.assertIn("MISSING_SEISMIC_MASS_FACTOR", issues)

    def test_explicitly_empty_source_patterns_cannot_pass(self):
        report = audit_load_case_purpose(
            "SEISMIC_SOURCE", {"Dead": 1.0}, {"Dead": 1.0},
            present_patterns={},
        )
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertTrue(any(
            "EMPTY_SOURCE_PATTERN_SET" in issue["issues"]
            for issue in report["issues"]
        ))

    def test_all_empty_maps_fail_closed(self):
        report = audit_load_case_purpose("AS_CONFIGURED", {}, {})
        self.assertEqual(report["status"], "REVIEW_REQUIRED")
        self.assertTrue(any(
            "NO_LOAD_PATTERNS_TO_AUDIT" in issue["issues"]
            for issue in report["issues"]
        ))

    def test_boolean_is_not_valid_numeric_factor(self):
        report = audit_load_case_purpose(
            "SEISMIC_SOURCE", {"Dead": True}, {"Dead": 1.0},
        )
        self.assertIn("INVALID_GRAVITY_FACTOR",
                      report["issues"][0]["issues"])

    def test_profile_and_mass_are_separate(self):
        gravity = {name: GRAVITY_ONLY_FACTORS[category]
                   for name, category in self.names.items()}
        audit = audit_load_case_purpose("GRAVITY_1.0D_1.0L", gravity, self.mass)
        live = next(row for row in audit["rows"] if row["pattern"] == "Live")
        self.assertEqual(live["gravity_factor"], 1.0)
        self.assertEqual(live["seismic_mass_factor"], 0.3)
        self.assertEqual(len(audit["issues"]), 0)


if __name__ == "__main__":
    unittest.main()
