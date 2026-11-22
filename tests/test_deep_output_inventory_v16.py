"""Pure Python filesystem tests for active writer inventory and stage hardening."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_live_output_writers import scan_source, save_local_report
from tools.audit_stage_output_migration import audit_stage_migration
from components.inputs.output_layout import write_stage_index
from components.inputs.folder_audit import audit_export_structure, write_folder_audit


class DeepOutputInventoryTests(unittest.TestCase):
    def test_static_scan_is_read_only_and_reports_writers_and_legacy(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            component = repo / "components" / "gravity"
            component.mkdir(parents=True)
            src = component / "runner.py"
            src.write_text(
                "from pathlib import Path\n"
                "LEGACY='OpenSees_Analysis_Results'\n"
                "def run(p):\n"
                "    Path(p).write_text('result')\n", encoding="utf-8")
            old_bytes = src.read_bytes()
            data = scan_source(repo)
            self.assertEqual(data["totals"]["files"], 1)
            self.assertGreaterEqual(data["totals"]["legacy_literal_occurrences"], 1)
            self.assertGreaterEqual(data["totals"]["possible_write_calls"], 1)
            self.assertEqual(data["top_legacy_candidates"][0]["source"],
                             "components/gravity/runner.py")
            self.assertGreaterEqual(
                data["top_legacy_candidates"][0]["potential_write_calls"],1)
            self.assertEqual(data["files"][0]["sha256"],
                             hashlib.sha256(old_bytes).hexdigest())
            self.assertEqual(src.read_bytes(), old_bytes)
            self.assertFalse((repo / "09_SOFTWARE_DIAGNOSTICS").exists())

    def test_legacy_docstring_not_mistaken_for_active_output_migration(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p=root/"components"/"gravity"/"module.py"
            p.parent.mkdir(parents=True)
            p.write_text(
                '"""Prior OpenSees_Analysis_Results folder is historical."""\\n'
                'def helper():\\n'
                '    """Another old OpenSees_Analysis_Results reference."""\\n'
                '    return "02_GRAVITY"\\n'
                'LEGACY="OpenSees_Analysis_Results"\\n',
                encoding="utf-8")
            result=scan_source(root)
            totals=result["totals"]
            self.assertEqual(totals["legacy_docstring_occurrences"],2)
            self.assertEqual(totals["legacy_executable_literal_occurrences"],1)
            self.assertEqual(totals["legacy_literal_occurrences"],3)
            entries=[x for x in result["files"][0]["occurrences"]
                     if x["kind"]=="LITERAL_PATH_MARKER" and x.get("legacy")]
            self.assertEqual(
                {x["literal_context"] for x in entries},
                {"DOCSTRING_REFERENCE","CODE_LITERAL_REVIEW"})
            self.assertEqual(
                result["top_legacy_candidates"][0]["legacy_executable_markers"],1)
            self.assertEqual(
                result["top_legacy_candidates"][0]["legacy_docstring_markers"],2)

    def test_writer_inventory_scans_new_standalone_src_tree(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            pkg=root/"src"/"opensees_engine"
            pkg.mkdir(parents=True)
            (pkg/"standalone.py").write_text(
                "def publish(target):\n    target.write_text('result')\n",
                encoding="utf-8")
            report=scan_source(root)
            self.assertEqual(report["totals"]["files"],1)
            self.assertIn("src/opensees_engine/standalone.py",
                          [x["source"] for x in report["files"]])
            self.assertGreaterEqual(report["totals"]["possible_write_calls"],1)

    def test_builtin_and_path_open_modes_are_detected_by_position(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "runner.py").write_text(
                "from pathlib import Path\n"
                "def run(file_path, mode):\n"
                "    Path(file_path).open('w')\n"
                "    Path(file_path).open('a')\n"
                "    Path(file_path).open('r')\n"
                "    Path(file_path).open()\n"
                "    Path(file_path).open(mode=mode)\n"
                "    open(file_path, 'wb')\n"
                "    open(file_path, 'r')\n"
                "    open(file_path, mode=mode)\n"
                "    open(file_path)\n",
                encoding="utf-8")
            result = scan_source(repo)
            self.assertFalse(result["parse_errors"])
            records = [r for r in result["files"][0]["occurrences"]
                       if r["kind"] == "POTENTIAL_WRITE_CALL"]
            self.assertEqual([r["line"] for r in records], [3, 4, 7, 8, 10])
            self.assertEqual(result["totals"]["possible_write_calls"], 5)
            self.assertEqual(
                sum(r.get("mode_classification") == "DYNAMIC_MODE_REVIEW_REQUIRED"
                    for r in records), 2)
            self.assertTrue(all(r["method"] == "open" for r in records))

    def test_optional_writer_report_is_canonical_and_complete(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            repo=base/"repo"
            repo.mkdir()
            (repo/"runner.py").write_text("open('case.log','w')\n",encoding="utf-8")
            export=base/"export"
            export.mkdir()
            report=scan_source(repo)
            run=save_local_report(report,export)
            self.assertTrue((run/"JSON"/"Writer_Audit.json").is_file())
            self.assertTrue((run/"CSV"/"Writer_References.csv").is_file())
            self.assertTrue((run/"REPORT"/"READ_FIRST.md").is_file())
            recorded=json.loads((run/"JSON"/"Writer_Audit.json").read_text())
            self.assertEqual(recorded["repository"],"<LOCAL_REPOSITORY_PATH>")
            self.assertEqual(recorded["totals"]["files"],1)

    def test_migration_auditor_refuses_symlinked_stage_root(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"project"
            outside=Path(td)/"outside"
            root.mkdir()
            run=outside/"RUNS"/"ULS"/"X"/"run"/"00_INPUT_SOURCE"
            run.mkdir(parents=True)
            (run/"CASE_MANIFEST.json").write_text('{"schema":"different"}')
            try:
                (root/"04_MODAL").symlink_to(outside,target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Host cannot create a directory symlink")
            audit=audit_stage_migration(root)
            modal=next(x for x in audit["stages"] if x["stage"]=="MODAL")
            self.assertFalse(modal["exists"])
            self.assertEqual(modal["run_manifest_count"],0)
            self.assertTrue(modal["symlink_refused"])
            self.assertEqual(modal["unreadable_or_invalid_manifests"][0]["problem"],
                             "SYMLINKED_STAGE_ROOT_REFUSED")

    def test_folder_mirror_symlink_not_hashed_or_followed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"project"
            outside=Path(td)/"outside"
            root.mkdir()
            outside.mkdir()
            source=root/"OpenSees_Element_Connectivity.json"
            source.write_text('{"source":true}')
            try:
                mirror=root/"01_ETABS_EXPORT"/"02_MAPPING"
                mirror.parent.mkdir()
                mirror.symlink_to(outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Host cannot create a directory symlink")
            audit=audit_export_structure(root)
            self.assertEqual(len(audit["unsafe_mirror_paths"]),1)
            self.assertIn("UNSAFE_EXPORT_MIRROR_LINK",
                          {item["id"] for item in audit["findings"]})
            with self.assertRaisesRegex(ValueError,"linked"):
                # The stage writer must never follow an externally redirected manifest.
                (root/"01_ETABS_EXPORT"/"00_MANIFEST").symlink_to(
                    outside,target_is_directory=True)
                write_folder_audit(root)

    def test_stage_index_does_not_count_linked_snapshots(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"export"
            root.mkdir()
            outside=Path(td)/"outside"
            (outside/"run_a").mkdir(parents=True)
            (root/"02_GRAVITY").mkdir()
            try:
                (root/"02_GRAVITY"/"REVIEW_SNAPSHOTS").symlink_to(
                    outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Host cannot create a directory symlink")
            item=write_stage_index(root)
            data=json.loads(item.read_text())
            gravity=next(s for s in data["stages"] if s["stage"]=="GRAVITY")
            self.assertEqual(gravity["review_snapshot_count"],0)
            self.assertTrue(gravity["symlink_refused"])


if __name__=="__main__":
    unittest.main()
