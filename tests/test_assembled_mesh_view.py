"""Regression tests for the on-demand assembled 3D mesh viewer."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.ui.assembled_mesh_view import build_mesh_lines, render


class AssembledMeshViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {"floor_subdivisions": 4}
        self.source = {
            "nodes": {
                "1": [0, 0, 0], "2": [1, 0, 0], "3": [1, 1, 0],
                "4": [0, 1, 0], "5": [2, 0, 0], "6": [2, 1, 0],
            },
            "shells": [
                {"nodes": [1, 2, 3, 4], "category": "FLOOR"},
                {"nodes": [2, 5, 6, 3], "category": "FLOOR"},
            ],
            "frames": [{"nodes": [1, 2]}],
        }
        config_bytes = json.dumps(self.config).encode("utf-8")
        (self.root / "OpenSees_Complete_Model_Config_V118.json").write_bytes(config_bytes)
        self.source["config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
        (self.root / "OpenSees_Complete_Model_Data_V118.json").write_text(
            json.dumps(self.source), encoding="utf-8"
        )

    def test_shared_shell_edge_rendered_once(self):
        lines = build_mesh_lines(self.source)
        self.assertEqual(len(lines["FLOOR"]), 7)
        self.assertEqual(len(lines["FRAME"]), 1)
        self.assertEqual(len(lines["SHEAR WALL"]), 0)

    def test_view_is_on_demand_and_leaves_sources_unchanged(self):
        before = (self.root / "OpenSees_Complete_Model_Data_V118.json").read_bytes()
        target = render(self.root)
        self.assertTrue(target.is_file())
        self.assertIn("02_MODEL", str(target))
        # Plotly JSON serializes non-ASCII title characters using Unicode
        # escapes; the browser renders the same 4×4 heading.
        self.assertIn(json.dumps("4×4")[1:-1],
                      target.read_text(encoding="utf-8"))
        self.assertTrue((target.parent / "plotly.min.js").is_file())
        self.assertEqual(
            (self.root / "OpenSees_Complete_Model_Data_V118.json").read_bytes(),
            before,
        )

    def test_reject_stale_model_hash(self):
        (self.root / "OpenSees_Complete_Model_Config_V118.json").write_text(
            '{"floor_subdivisions":8}', encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "Stale assembled mesh"):
            render(self.root)
        self.assertFalse((self.root / "02_MODEL").exists())

    def test_reject_missing_shell_corner(self):
        self.source["shells"][0]["nodes"][0] = 999
        with self.assertRaisesRegex(ValueError, "Missing assembled node"):
            build_mesh_lines(self.source)


if __name__ == "__main__":
    unittest.main()
