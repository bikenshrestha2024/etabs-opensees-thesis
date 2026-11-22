"""Component README links must reflect actual current code, not V134 snapshots.

[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]
"""
import tempfile
import unittest
from pathlib import Path

from tools.audit_component_readmes import audit


class ComponentReadmeCatalogTests(unittest.TestCase):
    def test_missing_and_stale_module_links_fail_closed_without_rewriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            folder=root/"components"/"gravity";folder.mkdir(parents=True)
            (folder/"new_case.py").write_text("pass\n")
            readme=folder/"README.md"
            readme.write_text("# Gravity\n[old.py](old.py)\n")
            found=audit(root)
            self.assertEqual(found["packaging_status"],"INCOMPLETE")
            self.assertEqual(found["issues"][0]["missing_links"],["new_case.py"])
            self.assertEqual(found["issues"][0]["stale_links"],["old.py"])
            self.assertTrue((folder/"new_case.py").exists())
            readme.write_text("# Gravity\n[new_case.py](new_case.py)\n")
            self.assertEqual(audit(root)["packaging_status"],"CURRENT")

    def test_all_live_component_folders_have_current_module_catalog(self):
        repo=Path(__file__).resolve().parents[1]
        result=audit(repo)
        self.assertEqual(result["issues"],[],result["issues"])
        self.assertGreaterEqual(len(result["packages"]),13)
        self.assertTrue(any(x["module"]=="nbc105" for x in result["packages"]))
        self.assertFalse(result["source_files_moved"])


if __name__=="__main__":
    unittest.main()
