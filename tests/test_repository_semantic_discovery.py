"""Offline source discovery: immutable inventories and honest acceptance boundaries."""
import pathlib
import subprocess
import tempfile
import unittest

from tools.repository_semantic_discovery import classify, collect, write_report


class DiscoveryTests(unittest.TestCase):
    def test_category_roles(self):
        self.assertEqual(classify("components/model/assembly.py"), "ACTIVE_OR_RESEARCH_SOURCE")
        self.assertEqual(classify("01_MAIN_GUI.py"), "ACTIVE_LAUNCHER_OR_COMPATIBILITY")
        self.assertEqual(classify("tests/test_a.py"), "REGRESSION_AND_CI")
        self.assertEqual(classify("Saved_Project_V156/example.py"), "HISTORICAL_PROVENANCE")
        self.assertEqual(classify("REVIEW_MAIN/a.md"), "DOCUMENTATION_AND_LITERATURE")

    def test_repository_inventory_and_read_only_review_states(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t)/"checkout"
            root.mkdir()
            def run(*args):
                return subprocess.run(
                    ["git", "-C", str(root), *args],
                    check=True, capture_output=True
                )
            run("init", "-q")
            (root/"components").mkdir()
            (root/"components"/"sample.py").write_text(
                "import pathlib\nclass X:\n    def a(self, path):\n        return pathlib.Path(path)\n"
            )
            (root/"01_MAIN_GUI.py").write_text("from components.sample import X\n")
            (root/"README.md").write_text("Public sample fixture\n")
            run("add", ".")
            run("-c", "user.email=audit@example.invalid",
                "-c", "user.name=Test", "commit", "-qm", "fixture")
            results=collect(root)
            self.assertEqual(results["tracked_files"],3)
            self.assertEqual(results["python_files"],2)
            self.assertEqual(results["symbols_discovered"],2)
            self.assertEqual(len(results["ast_issues"]),0)
            self.assertEqual(
                results["acceptance"]["S2_COMPLETE_SEMANTIC_REVIEW"],
                "NOT_VERIFIED"
            )
            self.assertTrue(all(
                symbol["review_status"] == "DISCOVERED_NOT_SEMANTICALLY_REVIEWED"
                for symbol in results["symbols"]
            ))
            output=write_report(results,root/"AUDIT_RUNS")
            self.assertTrue((output/"TRACKED_INVENTORY.csv").is_file())
            self.assertTrue((output/"SYMBOL_DISCOVERY_NOT_REVIEWED.csv").is_file())
            self.assertTrue((output/"READ_ME_FIRST.md").is_file())

    def test_invalid_python_is_not_silently_reviewed(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t)/"repo";root.mkdir()
            subprocess.run(["git","-C",str(root),"init","-q"],check=True)
            (root/"broken.py").write_text("def broken(:\n pass\n")
            subprocess.run(["git","-C",str(root),"add","broken.py"],check=True)
            subprocess.run([
                "git","-C",str(root),"-c","user.email=audit@example.invalid",
                "-c","user.name=Test","commit","-qm","bad syntax fixture"
            ],check=True)
            result=collect(root)
            self.assertEqual(len(result["ast_issues"]),1)
            self.assertEqual(result["ast_issues"][0]["path"],"broken.py")


if __name__=="__main__":
    unittest.main(verbosity=2)
