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
            mode_before = stat.S_IMODE(src.stat().st_mode)
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
            self.assertEqual(stat.S_IMODE(src.stat().st_mode), mode_before)  # mode untouched (platform-independent)
            self.assertEqual(src.read_bytes(), b"EDBDATA")
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

    def test_cleanup_retries_until_removed(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "m.edb"
            src.write_bytes(b"x")
            copy = guards.make_edb_working_copy(src, root=d)
            real, calls, sleeps, logs = guards.shutil.rmtree, [], [], []

            def flaky(path, ignore_errors=False):
                calls.append(path)
                if len(calls) > 1:
                    real(path, ignore_errors=True)  # first attempt fails silently
            with mock.patch.object(guards.shutil, "rmtree", flaky):
                self.assertTrue(guards.cleanup_edb_working_copy(copy, log=logs.append, sleep=sleeps.append))
            self.assertEqual((len(calls), len(sleeps)), (2, 1))
            self.assertFalse(copy.parent.exists())
            self.assertTrue(logs[-1].startswith("ETABS working copy removed"))

    def test_cleanup_gives_up_with_warning_and_no_raise(self):
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "m.edb"
            src.write_bytes(b"x")
            copy = guards.make_edb_working_copy(src, root=d)
            logs, sleeps = [], []
            with mock.patch.object(guards.shutil, "rmtree", lambda p, ignore_errors=False: None):
                self.assertFalse(guards.cleanup_edb_working_copy(copy, log=logs.append, attempts=3, sleep=sleeps.append))
            self.assertEqual(len(sleeps), 2)
            self.assertTrue(logs[-1].startswith("WARNING"))

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


def _load_application():
    """Import components.ui.application with stub tkinter modules (tkinter is absent in CI)."""
    import importlib
    import types
    from unittest import mock
    stubs = {n: types.ModuleType(n) for n in ("tkinter", "tkinter.filedialog", "tkinter.messagebox", "tkinter.ttk")}
    for n in ("filedialog", "messagebox", "ttk"):
        setattr(stubs["tkinter"], n, stubs["tkinter." + n])
    root = str(Path(__file__).resolve().parents[1])
    with mock.patch.dict(sys.modules, stubs), mock.patch.object(sys, "path", [root] + sys.path):
        sys.modules.pop("components.ui.application", None)
        return importlib.import_module("components.ui.application")


class FakeFile:
    def __init__(self, owner):
        self.owner = owner

    def OpenFile(self, path):
        self.owner.opened = path
        return 0

    def Close(self, save):
        self.owner.events.append("file_close")
        return 0


class FakeEtabs:
    def __init__(self, units_after=4):
        self.events, self.opened, self.exit_calls = [], None, 0
        self.exists_at_exit = None
        self.units_after = units_after
        self.SapModel = self
        self.File = FakeFile(self)

    def ApplicationStart(self):
        return 0

    def ApplicationExit(self, save):
        self.exit_calls += 1
        self.exists_at_exit = os.path.exists(self.opened) if self.opened else None
        self.events.append("exit")
        return 0

    def SetPresentUnits(self, u):
        return 0

    def GetPresentUnits(self):
        return self.units_after


class FakeComtypes:
    def __init__(self, etabs):
        helper = type("H", (), {"CreateObjectProgID": lambda self_, progid: etabs,
                                "QueryInterface": lambda self_, x: self_})()
        self.client = type("C", (), {"CreateObject": staticmethod(lambda progid: helper)})()
        self.gen = type("G", (), {})()


class TestApplicationWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = _load_application()

    def _edb(self, d):
        edb = Path(d) / "orig.edb"
        edb.write_bytes(b"EDB")
        return edb

    def test_connect_failure_closes_etabs_and_keeps_original_error(self):
        from unittest import mock
        etabs = FakeEtabs(units_after=4)
        with tempfile.TemporaryDirectory() as d:
            holder, logs = [], []
            with mock.patch.object(self.app, "comtypes", FakeComtypes(etabs)):
                with self.assertRaises(RuntimeError) as cm:
                    self.app._connect_etabs(str(self._edb(d)), logs.append, copy_holder=holder)
            self.assertIn("GetPresentUnits", str(cm.exception))
            self.assertEqual(etabs.exit_calls, 1)
            self.assertEqual(etabs.events[:2], ["file_close", "exit"])
            self.assertEqual(Path(etabs.opened).resolve(), holder[0].resolve())
            self.assertNotEqual(Path(etabs.opened).resolve(), (Path(d) / "orig.edb").resolve())
            guards.cleanup_edb_working_copy(holder[0])

    def test_convert_model_exits_etabs_before_removing_copy(self):
        from unittest import mock
        etabs = FakeEtabs(units_after=4)
        with tempfile.TemporaryDirectory() as d:
            edb, out = self._edb(d), Path(d) / "out"
            with mock.patch.object(self.app, "comtypes", FakeComtypes(etabs)), \
                 mock.patch.object(self.app, "ops", object()):
                with self.assertRaises(RuntimeError):
                    self.app.convert_model(str(edb), str(out), lambda *a, **k: None)
            self.assertEqual(etabs.exit_calls, 1)
            self.assertTrue(etabs.exists_at_exit)           # copy still present when ETABS closed
            self.assertFalse(Path(etabs.opened).parent.exists())  # then removed in finally
            self.assertEqual(edb.read_bytes(), b"EDB")

    def test_diaphragm_read_failure_raises_with_point_names(self):
        class Pt:
            def GetDiaphragm(self, name):
                if name == "7":
                    raise OSError("COM")
                return ("None", 0, 0)
        sap = type("S", (), {"PointObj": Pt()})()
        with self.assertRaises(guards.DroppedPointsError) as cm:
            self.app._extract_point_diaphragm_assignments(sap, ["6", "7"], lambda *a: None)
        self.assertEqual(cm.exception.names, ["7"])


class TestAssemblyErrorsAreFatal(unittest.TestCase):
    def test_bad_material_row_reaches_report_and_worker_rejects_it(self):
        from tools.etabs_conversion_worker import validate_converter_report
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            runtime = folder / "runtime_source"
            runtime.mkdir()
            nodes = {1: [0., 0., 0.], 2: [3., 0., 3.], 4: [0., 0., 3.], 5: [3., 3., 3.], 6: [0., 3., 3.]}
            sources = {
                "OpenSees_Element_Connectivity.json": dict(
                    node_map=[dict(etabs_point_name=str(n), opensees_node_tag=n, coordinates_m=xyz)
                              for n, xyz in nodes.items()],
                    elements=[dict(etabs_object="A", category="FLOOR", dimension="area_polygon",
                                   node_tags=[4, 2, 5, 6])],
                    rigid_diaphragm_groups=[dict(storey_number=1, master_xyz=[3., 0., 3.], slave_node_tags=[2])]),
                "OpenSees_Section_Assignment_Audit.json": dict(
                    frame_assignments=[],
                    area_assignments=[dict(etabs_area_object="A", assigned_property="Slab", property_type="slab",
                                           material_name="Concrete", thickness_m=.15,
                                           material_values=dict(E=3e7, poisson_ratio=.2, weight_per_volume=25))],
                    frame_distributed_load_assignments=[]),
                "OpenSees_Load_Conversion_Audit.json": dict(
                    applied_area_loads=[], base_supports=dict(node_tags=[1]),
                    etabs_load_pattern_self_weight_multipliers=[dict(pattern="Self Weight", multiplier=1)]),
                "OpenSees_Source_Model_Metadata_V118.json": dict(present_units=6, pattern_types={}, frames={}),
            }
            for name, value in sources.items():
                (folder / name).write_text(json.dumps(value), encoding="utf-8")
            with (folder / "ETABS_Materials.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["name", "isotropic", "weight_mass"])
                w.writeheader()
                w.writerow(dict(name="BROKEN", isotropic="(((", weight_mass="(1.0, 1.0, 0)"))
            _manifest, report = assembly.prepare_complete_export(folder, runtime_dir=runtime)
            self.assertTrue(any("BROKEN" in e for e in report["assembly_errors"]), report["assembly_errors"])
            report_file = folder / "OpenSees_Complete_Export_Report_V118.json"
            self.assertTrue(report_file.is_file())
            with self.assertRaisesRegex(RuntimeError, "assembly"):
                validate_converter_report(report_file)


if __name__ == "__main__":
    unittest.main()
