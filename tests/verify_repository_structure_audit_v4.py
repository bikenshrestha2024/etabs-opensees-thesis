"""Offline, read-only regression tests for the V4 repository inventory."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "audit_repository_structure_v4", ROOT / "tools/audit_repository_structure_v4.py"
)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class RepositoryInventoryTests(unittest.TestCase):
    def test_classifications_are_conservative(self):
        self.assertEqual(
            module.safe_classification("Saved_Project_V156/example.py")[0],
            "historical_candidate",
        )
        self.assertEqual(
            module.safe_classification("10_GRAVITY.py")[0],
            "launcher_or_legacy_review",
        )
        self.assertNotEqual(
            module.safe_classification("components/gravity/main.py")[0],
            "safe_to_delete",
        )

    def test_imports_are_not_executed(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "unsafe.py"
            source.write_text(
                "import os\nfrom pathlib import Path\n"
                "raise RuntimeError('must never execute')\n",
                encoding="utf-8",
            )
            self.assertEqual(module.imports_of(source), ["os", "pathlib"])

    def test_inventory_is_non_destructive_and_marks_dupes_as_candidates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "components").mkdir()
            (root / "components" / "a.py").write_text("import math\n", encoding="utf-8")
            (root / "components" / "b.py").write_text("import math\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(root), "add", "components/a.py", "components/b.py"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "-c", "user.name=Inventory Test",
                 "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"],
                check=True,
            )
            out = root / "REPORTS"
            summary = module.generate(root, out)
            self.assertEqual(summary["tracked_file_count"], 2)
            self.assertEqual(summary["exact_duplicate_groups"], 1)
            dup = json.loads((out / "EXACT_DUPLICATE_CANDIDATES.json").read_text())
            self.assertEqual(dup[0]["classification"], "exact_bytes_only_not_safe_to_delete")
            self.assertEqual((root / "components/a.py").read_text(), "import math\n")
            self.assertEqual((root / "components/b.py").read_text(), "import math\n")


if __name__ == "__main__":
    unittest.main()
