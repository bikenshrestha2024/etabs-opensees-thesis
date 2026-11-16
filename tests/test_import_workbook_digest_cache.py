"""Source-aware preflight performance and correctness regressions."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from components.inputs import lfs_workbook_recovery as recovery


class WorkbookPreflightHashTests(unittest.TestCase):
    def test_edb_hashed_once_for_four_optional_roles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edb = root / "source.EDB"
            edb.write_bytes(b"original-thesis-model")
            runtime = root / "runtime"
            runtime.mkdir()
            output = root / "output"
            output.mkdir()
            authentic = recovery.digest
            readings = []

            def counted_digest(path):
                readings.append(Path(path).resolve())
                return authentic(path)

            with patch.object(recovery, "digest", side_effect=counted_digest):
                result = recovery.audit_optional_gui_workbooks(
                    runtime, output, edb)
            self.assertEqual(readings.count(edb.resolve()), 1)
            self.assertEqual(result["conversion_blocked"], False)
            self.assertEqual(
                set(result["roles"]),
                {"etabs_full_table", "etabs_assignment",
                 "nbc_calculator", "slab_load_path"})
            self.assertEqual(len(readings), 1)
            self.assertEqual(edb.read_bytes(), b"original-thesis-model")

    def test_registered_sources_remain_digest_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edb = root / "test.EDB"
            edb.write_bytes(b"source")
            runtime = root / "runtime"
            runtime.mkdir()
            output = root / "output"
            output.mkdir()
            workbook = root / "source.xlsx"
            workbook.write_bytes(b"original-data")
            registry = {
                "source_edb_sha256": recovery.digest(edb),
                "sources": {
                    "etabs_full_table": {
                        "path": str(workbook),
                        "sha256": recovery.digest(workbook)
                    }
                }
            }
            (output / "project_sources.private.json").write_text(
                json.dumps(registry), encoding="utf-8")
            good = recovery.audit_optional_gui_workbooks(
                runtime, output, edb)
            self.assertEqual(
                good["roles"]["etabs_full_table"]["status"],
                "SHA256_VERIFIED")
            workbook.write_bytes(b"tampered")
            bad = recovery.audit_optional_gui_workbooks(
                runtime, output, edb)
            self.assertEqual(
                bad["roles"]["etabs_full_table"]["status"],
                "SHA256_MISMATCH_NOT_ACCEPTED")


if __name__ == "__main__":
    unittest.main()
