"""Git-index coverage inventory tests; NOT code semantic/numerical validation."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.audit_tracked_review_coverage import inventory, save_local


class TrackedCoverageTests(unittest.TestCase):
    def test_staged_inventory_covers_all_files_and_never_claims_review(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)/"repo"
            repo.mkdir()
            def git(*args):
                return subprocess.run(["git","-C",str(repo),*args],
                                      check=True,capture_output=True,text=True).stdout
            git("init","-q")
            (repo/"components").mkdir()
            (repo/"src").mkdir()
            (repo/"tests").mkdir()
            (repo/"docs").mkdir()
            (repo/"components"/"assembly.py").write_text("def x(): pass\n")
            (repo/"src"/"neutral.py").write_text("def validate(x): return x\n")
            for historical in ("Verification_V159", "Worked_Example_V132",
                               "Research_Components"):
                folder=repo/historical
                folder.mkdir()
                (folder/"old.py").write_text("historic snapshot\n")
            (repo/"tests"/"test_one.py").write_text("assert True\n")
            (repo/"docs"/"README.md").write_text("# docs\n")
            git("add",".")
            git("-c","user.name=Regression","-c","user.email=regression@example.invalid",
                "commit","-qm","test files")
            report=inventory(repo)
            self.assertEqual(report["tracked_count"],7)
            self.assertEqual(report["review_not_completed_count"],7)
            self.assertEqual(report["reviewed_current_head_count"],0)
            self.assertEqual(report["source_index_status"],"HEAD_CLEAN_TRACKED_FILES")
            self.assertEqual(report["counts_by_category"]["ACTIVE_PYTHON_SOURCE"],2)
            self.assertEqual(next(x["category"] for x in report["entries"]
                                  if x["path"]=="src/neutral.py"),"ACTIVE_PYTHON_SOURCE")
            self.assertEqual(report["counts_by_category"]["HISTORICAL_OR_ARCHIVE"],3)
            self.assertTrue(all(x["category"]=="HISTORICAL_OR_ARCHIVE"
                 for x in report["entries"]
                 if x["path"].startswith(("Verification_V159/",
                                          "Worked_Example_V132/",
                                          "Research_Components/"))))
            self.assertTrue(all(x["review_status"]=="NOT_REVIEWED_CURRENT_HEAD"
                                for x in report["entries"]))
            original=(repo/"components"/"assembly.py").read_bytes()
            export=Path(td)/"export"
            export.mkdir()
            run=save_local(report,export,repo)
            self.assertTrue((run/"JSON"/"Tracked_Review_Coverage.json").is_file())
            self.assertTrue((run/"CSV"/"Tracked_Review_Coverage.csv").is_file())
            self.assertTrue((run/"REPORT"/"READ_FIRST.md").is_file())
            self.assertEqual((repo/"components"/"assembly.py").read_bytes(),original)
            (repo/"components"/"assembly.py").write_text("def x(): return 2\n")
            self.assertEqual(inventory(repo)["source_index_status"],
                             "TRACKED_WORKTREE_DIFFERS_FROM_HEAD")
            with self.assertRaisesRegex(ValueError,"outside the public source checkout"):
                save_local(report,repo,repo)

    def test_linked_register_destination_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"export"
            root.mkdir()
            repo=Path(td)/"repo"
            repo.mkdir()
            outside=Path(td)/"outside"
            outside.mkdir()
            dest=root/"09_SOFTWARE_DIAGNOSTICS"
            try:
                dest.symlink_to(outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Directory symlink unsupported")
            with self.assertRaisesRegex(ValueError,"linked"):
                save_local({"entries":[]},root,repo)
            self.assertEqual(list(outside.iterdir()),[])


if __name__=="__main__":
    unittest.main()
