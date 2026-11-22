"""Physical ETABS joint tag contract for converted shell/frame mesh.

Static synthetic checks only: no ETABS COM, native source EDB or solver.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from components.model.source_node_identity import (
    audit_node_map_identity,
    unique_coordinate_lookup,
)
from components.model.assembly import _mesh_areas
from components.validation.gravity_native_equivalence_preflight import assess
from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32


class SourceNodeIdentityTests(unittest.TestCase):
    def test_ordinary_unique_source_points_are_preserved(self):
        src = {1: [0., 0., 0.], 2: [3., 0., 0.], 3: [3., 3., 0.]}
        lookup = unique_coordinate_lookup(src)
        self.assertEqual(lookup[(0., 0., 0.)], 1)
        self.assertEqual(lookup[(3., 3., 0.)], 3)
        self.assertEqual(len(lookup), len(src))

    def test_distinct_tags_at_same_coordinates_do_not_silently_merge(self):
        points = {1: [0., 0., 0.], 2: [0., 0., 0.],
                  3: [3., 0., 0.], 4: [3., 3., 0.],
                  5: [0., 3., 0.]}
        with self.assertRaisesRegex(ValueError, "Ambiguous coincident ETABS source point tags"):
            unique_coordinate_lookup(points)
        # This is the active source area-assembly path; prior to the fix its
        # comprehension silently overwrote tag 1 with tag 2.
        floor = [{
            "dimension": "area_polygon", "category": "FLOOR",
            "etabs_object": "100", "node_tags": [1, 3, 4, 5],
        }]
        with self.assertRaisesRegex(ValueError, "Ambiguous coincident ETABS source point tags"):
            _mesh_areas(points, floor, {}, {}, floor_subdivisions=4)

    def test_nan_coordinate_rejected_before_assembly(self):
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            unique_coordinate_lookup({8: [0., float("nan"), 0.]})

    def test_audit_distinguishes_source_tag_collisions_from_unique_tags(self):
        rows = [
            {"etabs_point_name": "A", "opensees_node_tag": 1,
             "coordinates_m": [0., 0., 0.]},
            {"etabs_point_name": "B", "opensees_node_tag": 2,
             "coordinates_m": [0., 0., 0.]},
            {"etabs_point_name": "C", "opensees_node_tag": 3,
             "coordinates_m": [6., 0., 0.]},
        ]
        audit = audit_node_map_identity(rows)
        self.assertEqual(audit["status"],
                         "COINCIDENT_DISTINCT_SOURCE_NODES_REQUIRE_NATIVE_REVIEW")
        self.assertEqual(audit["duplicate_coordinate_group_count"], 1)
        self.assertEqual(audit["native_constraint_equivalence"], "NOT_VERIFIED")
        unique = audit_node_map_identity(rows[0::2])
        self.assertEqual(unique["status"],
                         "SOURCE_NODE_IDENTITY_UNIQUE_NOT_NATIVE_VERIFIED")

    def test_audit_never_calls_missing_coordinates_unique(self):
        status = audit_node_map_identity([{
            "etabs_point_name": "A", "opensees_node_tag": 1
        }])
        self.assertEqual(status["status"], "SOURCE_NODE_COORDINATES_INCOMPLETE")
        self.assertEqual(status["missing_rows"], 1)

    def test_saved_export_preflight_reports_risky_joint_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            model = {"supports": {str(n): [1] * 6 for n in PROJECT_PRIMARY_32}}
            rows = [
                {"opensees_node_tag": n, "etabs_point_name": str(n),
                 "coordinates_m": [float(n), 0., 0.]}
                for n in PROJECT_PRIMARY_32
            ]
            rows.append({
                "opensees_node_tag": 999, "etabs_point_name": "mesh_999",
                "coordinates_m": list(rows[0]["coordinates_m"]),
            })
            for name, val in (
                ("OpenSees_Complete_Model_Data_V118.json", model),
                ("OpenSees_Source_Model_Metadata_V118.json",
                 {"frames": {}, "errors": []}),
                ("OpenSees_Element_Connectivity.json", {"node_map": rows}),
            ):
                (root / name).write_text(json.dumps(val), encoding="utf8")
            report = assess(root)
            self.assertEqual(
                report["source_node_identity_audit"]["duplicate_coordinate_group_count"],
                1,
            )
            self.assertIn(
                "ETABS source joint ID / XYZ mapping requires review: "
                "COINCIDENT_DISTINCT_SOURCE_NODES_REQUIRE_NATIVE_REVIEW",
                report["blockers"],
            )
            self.assertEqual(report["engineering_acceptance"], "NOT_VALIDATED")


if __name__ == "__main__":
    unittest.main()
