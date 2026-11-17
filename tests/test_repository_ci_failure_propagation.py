"""CI must not report green when any individual test command fails."""
from pathlib import Path
import re
import unittest


class RepositoryCheckFailurePropagationTests(unittest.TestCase):
    def test_each_quality_command_is_guarded_and_failure_count_fails_job(self):
        path=Path(__file__).resolve().parents[1]/".github/workflows/repository-integrity.yml"
        source=path.read_text(encoding="utf-8")
        commands=[line.strip() for line in source.splitlines()
                  if line.strip().startswith(("python ", "check python "))]
        self.assertGreater(len(commands),20)
        self.assertTrue(all(line.startswith("check python ") for line in commands),
                        "A bare Python invocation can silently mask prior failures")
        self.assertIn('failed=$((failed+1))',source)
        self.assertIn('if [ "$failed" -ne 0 ]; then',source)
        self.assertIn('exit 1',source)
        self.assertIn("audit/active_inventory.json",source)
        self.assertIn("--fail-on-missing-canonical",source)
        integrated=(Path(__file__).resolve().parents[1]/
                    ".github/workflows/integrated-repository-audit.yml").read_text()
        self.assertIn("audit_repository_integrated.py",integrated)
        self.assertIn("--fail-on-static-blockers",integrated)


if __name__=="__main__":
    unittest.main()
