"""Tests for the ETABS beam-force shard audit.

[REF docs/source/tests/test_etabs_beam_force_shards.py.md]
Logic tests use tiny hand-built shards. ``PinnedRealBeamEvidenceTests`` reads the
audit produced from the real three beam workbooks. Neither is native acceptance.
"""
import json
import unittest
from pathlib import Path

from components.validation.etabs_beam_force_shards import audit_beam_force_shards

EVIDENCE = Path(__file__).resolve().parents[1] / "docs" / "validation" / "20261128_ETABS_BEAM_FORCE_SHARDS_AUDIT.json"


def rows(element, story="Story1", cases=("A", "B"), stations=(0.5, 1.0), skip=(), bump=0.0):
    out = []
    for case in cases:
        for st in stations:
            if (case, st) in skip:
                continue
            out.append({"Story": story, "Unique Name": element, "Output Case": case, "Step Type": "Max",
                        "Step Number": None, "Station": st, "P": 0, "V2": 1.0 + bump, "V3": 0, "T": 0, "M2": 0, "M3": 2.0})
    return out


class ShardLogicTests(unittest.TestCase):
    def test_cut_element_recovered_by_next_shard_is_complete(self):
        first = rows("0") + rows("1") + rows("2", skip={("B", 1.0)})  # element 2 cut inside shard 1
        second = rows("2") + rows("3")                              # shard 2 repeats and completes it
        doc = audit_beam_force_shards([("s1", first), ("s2", second)], excel_row_limit=len(first) + 3)
        self.assertTrue(doc["shards"][0]["at_excel_row_limit"])
        self.assertFalse(doc["shards"][1]["at_excel_row_limit"])
        self.assertEqual(doc["union"]["elements"], 4)
        self.assertEqual(doc["union"]["unique_rows"], 16)
        self.assertEqual(doc["rows_repeated_in_later_shard"], 3)
        self.assertEqual(doc["repeated_rows_with_different_values"], 0)
        self.assertEqual(doc["union_status"], "UNION_COMPLETE_AND_CONSISTENT")
        self.assertIn("SHARD_AT_EXCEL_ROW_LIMIT", [f["id"] for f in doc["findings"]])

    def test_unrecovered_cut_is_an_error(self):
        doc = audit_beam_force_shards([("s1", rows("1") + rows("2", skip={("B", 1.0)}))])
        self.assertEqual(doc["union_status"], "UNION_HAS_ERRORS")
        self.assertEqual(doc["union"]["elements_with_incomplete_case_station_grid"], 1)
        self.assertIn("BEAM_GRID_INCOMPLETE", [f["id"] for f in doc["findings"]])

    def test_conflicting_repeat_and_inside_shard_duplicate_are_errors(self):
        doc = audit_beam_force_shards([("s1", rows("1")), ("s2", rows("1", bump=0.5))])
        self.assertEqual(doc["repeated_rows_with_different_values"], 4)
        self.assertIn("SHARD_REPEAT_CONFLICT", [f["id"] for f in doc["findings"]])
        dup = audit_beam_force_shards([("s1", rows("1") + rows("1")[:1])])
        self.assertEqual(dup["shards"][0]["duplicate_key_rows_inside_shard"], 1)
        self.assertEqual(dup["union_status"], "UNION_HAS_ERRORS")

    def test_missing_force_value_and_frame_table_mismatch(self):
        bad = rows("1")
        bad[0]["V2"] = None
        got = audit_beam_force_shards([("s", bad)])
        self.assertIn("NONFINITE_FORCE_VALUES", [f["id"] for f in got["findings"]])
        self.assertEqual(got["nonfinite_values"], 1)  # one row, counted once
        doc = audit_beam_force_shards([("s", rows("1") + rows("2"))], frame_elements={"1": "Story9"})
        self.assertEqual(doc["frame_table_match"], {"beam_elements_missing_from_frame_table": 1, "story_disagreements": 1})
        self.assertEqual(doc["union_status"], "UNION_HAS_ERRORS")

    def test_numeric_text_and_float_station_keys_agree_across_shards(self):
        a = rows("7"); b = rows("7")
        for r in b:
            r["Station"] = float(r["Station"]); r["Step Number"] = None
        self.assertEqual(audit_beam_force_shards([("a", a), ("b", b)])["repeated_rows_with_different_values"], 0)


@unittest.skipUnless(EVIDENCE.is_file(), "beam shard evidence not generated yet")
class PinnedRealBeamEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = EVIDENCE.read_text(encoding="utf-8")
        cls.doc = json.loads(cls.text)

    def test_reference_only_without_local_paths(self):
        self.assertEqual(self.doc["engineering_acceptance"], "NOT_VERIFIED")
        for marker in ("/mnt/", "/home/", "C:\\\\", "Users\\\\"):
            self.assertNotIn(marker, self.text)

    def test_three_shards_form_one_complete_table(self):
        d = self.doc
        self.assertEqual([s["data_rows"] for s in d["shards"]], [1048573, 1048573, 477700])
        self.assertEqual([s["at_excel_row_limit"] for s in d["shards"]], [True, True, False])
        self.assertEqual(d["union"]["elements"], 750)
        self.assertEqual(d["union"]["unique_rows"], 2388500)
        self.assertEqual(d["union"]["elements_with_incomplete_case_station_grid"], 0)
        self.assertEqual(d["union_status"], "UNION_COMPLETE_AND_CONSISTENT")

    def test_overlaps_between_neighbouring_shards_agree_exactly(self):
        d = self.doc
        self.assertEqual(d["shared_elements_between_shards"],
                         {"beam_1&beam_2": 30, "beam_1&beam_3": 0, "beam_2&beam_3": 30})
        self.assertEqual(d["rows_repeated_in_later_shard"], 186346)  # 2 x 93,173
        self.assertEqual(d["repeated_rows_with_different_values"], 0)

    def test_every_beam_matches_the_frame_table(self):
        self.assertEqual(self.doc["frame_table_match"],
                         {"beam_elements_missing_from_frame_table": 0, "story_disagreements": 0})


if __name__ == "__main__":
    unittest.main()
