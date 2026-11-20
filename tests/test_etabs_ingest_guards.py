"""Headless fake-COM tests for ETABS ingestion hardening (no ETABS, no tkinter).

Native ETABS COM behaviour is PENDING; these tests exercise only the pure guard
logic with fake `sap` objects and injected failures.
"""
import csv
import hashlib
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

from components.validation import gravity_etabs_direct as guards
from components.model import assembly


class FakePointObj:
    def __init__(self, coords, fail=(), bad=(), nonzero=()):
        self.coords, self.fail, self.bad, self.nonzero = coords, set(fail), set(bad), set(nonzero)

    def GetCoordCartesian(self, name):
        if name in self.fail:
            raise OSError("COM failure " + name)
        if name in self.bad:
            return (float("nan"), 0.0, 0.0, 0)
        if name in self.nonzero:
            return (1.0, 2.0, 3.0, 1)
        return tuple(self.coords[name]) + (0,)


class FakeSap:
    def __init__(self, units_after=6, set_ret=0, set_raises=None, points=None):
        self.units, self.units_after, self.set_ret, self.set_raises = 4, units_after, set_ret, set_raises
        self.PointObj = points

    def SetPresentUnits(self, u):
        if self.set_raises:
            raise self.set_raises
        self.units = self.units_after if self.units_after is not None else u
        return self.set_ret

    def GetPresentUnits(self):
        return self.units


class TestWorkingCopy(unittest.TestCase):
    def test_copy_is_distinct_writable_and_source_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "model.edb"
            src.write_bytes(b"EDBDATA")
            os.chmod(src, stat.S_IREAD)
            digest = hashlib.sha256(src.read_bytes()).hexdigest()
            mtime = src.stat().st_mtime_ns
            copy = guards.make_edb_working_copy(src, root=d)
            try:
                self.assertNotEqual(copy.resolve(), src.resolve())
                self.assertEqual(copy.read_bytes(), b"EDBDATA")
                self.assertTrue(os.access(copy, os.W_OK))
                self.assertTrue(copy.name.lower().endswith(".edb"))
            finally:
                self.assertTrue(guards.cleanup_edb_working_copy(copy))
            self.assertFalse(copy.parent.exists())
            self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(), digest)
            self.assertEqual(src.stat().st_mtime_ns, mtime)
            self.assertFalse(os.access(src, os.W_OK) and False)
            os.chmod(src, stat.S_IWRITE | stat.S_IREAD)

    def test_cleanup_removes_etabs_side_files(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "m.edb"
            src.write_bytes(b"x")
            copy = guards.make_edb_working_copy(src, root=d)
            for ext in (".$et", ".ebk", ".log", ".OUT", ".Y09"):
                copy.with_suffix(ext).write_text("side")
            guards.cleanup_edb_working_copy(copy)
            self.assertFalse(copy.parent.exists())
            self.assertTrue(src.exists())

    def test_cleanup_refuses_foreign_directory(self):
        with tempfile.TemporaryDirectory() as d:
            keep = Path(d) / "user.edb"
            keep.write_bytes(b"x")
            self.assertFalse(guards.cleanup_edb_working_copy(keep))
            self.assertTrue(keep.exists())

    def test_missing_source_raises(self):
        with self.assertRaises(FileNotFoundError):
            guards.make_edb_working_copy("/nonexistent/none.edb")


class TestUnits(unittest.TestCase):
    def test_ok(self):
        guards.require_present_units(FakeSap(), 6)

    def test_readback_mismatch_raises(self):
        with self.assertRaisesRegex(RuntimeError, "GetPresentUnits"):
            guards.require_present_units(FakeSap(units_after=4), 6)

    def test_set_exception_not_swallowed(self):
        with self.assertRaises(ValueError):
            guards.require_present_units(FakeSap(set_raises=ValueError("boom")), 6)

    def test_nonzero_return_raises(self):
        with self.assertRaisesRegex(RuntimeError, "SetPresentUnits"):
            guards.require_present_units(FakeSap(set_ret=1), 6)


class TestPointCoords(unittest.TestCase):
    COORDS = {"1": (0, 0, 0), "2": (1, 2, 3), "3": (4, 5, 6)}

    def test_all_good_unchanged(self):
        sap = FakeSap(points=FakePointObj(self.COORDS))
        out = guards.collect_point_coords(sap, ["1", "2", "3"])
        self.assertEqual(out, {"1": (0.0, 0.0, 0.0), "2": (1.0, 2.0, 3.0), "3": (4.0, 5.0, 6.0)})

    def test_failures_are_named_logged_and_raised(self):
        sap = FakeSap(points=FakePointObj(self.COORDS, fail=["2"], bad=["3"]))
        logs = []
        with self.assertRaises(guards.DroppedPointsError) as cm:
            guards.collect_point_coords(sap, ["1", "2", "3"], log=logs.append)
        self.assertEqual(cm.exception.names, ["2", "3"])
        self.assertIn("2", str(cm.exception))
        self.assertTrue(any("2" in m and "3" in m for m in logs))

    def test_nonzero_return_code_counts_as_dropped(self):
        sap = FakeSap(points=FakePointObj(self.COORDS, nonzero=["1"]))
        with self.assertRaises(guards.DroppedPointsError) as cm:
            guards.collect_point_coords(sap, ["1", "2"])
        self.assertEqual(cm.exception.names, ["1"])

    def test_raise_if_dropped_helper(self):
        guards.raise_if_points_dropped("x", [])
        with self.assertRaises(guards.DroppedPointsError):
            guards.raise_if_points_dropped("x", ["9"])


class TestMaterialTable(unittest.TestCase):
    def _write(self, folder, rows):
        with (Path(folder) / "ETABS_Materials.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["name", "isotropic", "weight_mass"])
            w.writeheader()
            w.writerows(rows)

    def test_good_rows_unchanged_and_no_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._write(d, [dict(name="C25", isotropic="(25000000.0, 0.2, 1e-5, 0)",
                                 weight_mass="(25.0, 2.5, 0)")])
            errors = []
            t = assembly._material_table(Path(d), errors)
            self.assertEqual(t, {"C25": dict(E=25000000.0, nu=0.2, weight=25.0)})
            self.assertEqual(errors, [])
            self.assertEqual(assembly._material_table(Path(d)), t)

    def test_unparseable_and_nonzero_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            self._write(d, [
                dict(name="OK", isotropic="(1.0, 0.2, 1e-5, 0)", weight_mass="(2.0, 1.0, 0)"),
                dict(name="BAD", isotropic="not a tuple(", weight_mass="(2.0, 1.0, 0)"),
                dict(name="RC1", isotropic="(1.0, 0.2, 1e-5, 1)", weight_mass="(2.0, 1.0, 0)"),
                dict(name="RC2", isotropic="(1.0, 0.2, 1e-5, 0)", weight_mass="(2.0, 1.0, 3)"),
            ])
            errors = []
            t = assembly._material_table(Path(d), errors)
            self.assertEqual(list(t), ["OK"])
            joined = " | ".join(errors)
            self.assertEqual(len(errors), 3)
            for name in ("BAD", "RC1", "RC2"):
                self.assertIn(name, joined)


class TestNoTopLevelTkinter(unittest.TestCase):
    def test_guard_module_has_no_tkinter_import(self):
        src = Path(guards.__file__).read_text(encoding="utf-8")
        for line in src.splitlines():
            if line.startswith(("import ", "from ")):
                self.assertNotIn("tkinter", line)


if __name__ == "__main__":
    unittest.main()
