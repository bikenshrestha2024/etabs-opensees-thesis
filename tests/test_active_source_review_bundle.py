"""Non-native code-only GitHub source snapshot safety/coverage tests."""
from __future__ import annotations
import hashlib
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.build_active_source_review_bundle import build, select_paths


class SourceReviewBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/"repo"
        self.root.mkdir()
        subprocess.run(["git","init","-q",str(self.root)],check=True)
        files={
            "01_COMPAT.py":"print('compat')\n",
            "components/model/assembly.py":"def assemble(): return 1\n",
            "src/thesis_core/neutral.py":"def validate(): return True\n",
            "tools/check.py":"def check(): return False\n",
            "tests/test_one.py":"assert 1\n",
            "AGENTS.md":"# engineering rules\n",
            "engineering/rules/CORE_RULES.md":"# preserved rules\n",
            "data/source_model.edb":"SENSITIVE MODEL DATA",
            "archive/old.py":"print('archived snapshot')\n",
            "docs/report.md":"unrelated\n",
        }
        for rel,content in files.items():
            path=self.root/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf-8")
        subprocess.run(["git","-C",str(self.root),"add","-A"],check=True)
        subprocess.run(["git","-C",str(self.root),
                        "-c","user.name=Regression",
                        "-c","user.email=regression@example.invalid",
                        "commit","-qm","fixture"],check=True)

    def test_code_only_snapshot_and_exact_current_git_identity(self):
        selected=select_paths(self.root)
        self.assertIn("src/thesis_core/neutral.py",selected)
        self.assertIn("01_COMPAT.py",selected)
        self.assertNotIn("archive/old.py",selected)
        self.assertNotIn("data/source_model.edb",selected)
        target=Path(self.temp.name)/"review"/"source.zip"
        manifest=build(self.root,target)
        self.assertEqual(manifest["file_count"],len(selected))
        self.assertFalse(manifest["semantic_review_completed"])
        self.assertFalse(manifest["non_code_data_included"])
        with zipfile.ZipFile(target) as z:
            names=set(z.namelist())
            self.assertIn("SOURCE/components/model/assembly.py",names)
            self.assertNotIn("SOURCE/data/source_model.edb",names)
            self.assertNotIn("SOURCE/archive/old.py",names)
            self.assertEqual(json.loads(z.read("REVIEW_MANIFEST.json"))["git_head"],
                             manifest["git_head"])
            row=next(x for x in manifest["files"]
                     if x["path"]=="src/thesis_core/neutral.py")
            self.assertEqual(row["sha256"],hashlib.sha256(
                z.read("SOURCE/src/thesis_core/neutral.py")).hexdigest())
        with self.assertRaises(FileExistsError):
            build(self.root,target)

    def test_linked_tracked_code_is_refused(self):
        original=self.root/"components"/"model"/"assembly.py"
        external=Path(self.temp.name)/"external.py"
        external.write_text("PRIVATE_SOURCE_CONTENT",encoding="utf-8")
        original.unlink()
        try:
            original.symlink_to(external)
        except (OSError,NotImplementedError):
            self.skipTest("Host cannot create file symlinks")
        with self.assertRaisesRegex(ValueError,"Linked source"):
            select_paths(self.root)
        self.assertEqual(external.read_text(),"PRIVATE_SOURCE_CONTENT")


if __name__ == "__main__":
    unittest.main()
