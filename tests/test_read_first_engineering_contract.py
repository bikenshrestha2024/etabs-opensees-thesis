"""Static regression: mandatory agent preflight files and project invariants.

This test checks repository guidance is intact. It cannot prove that any AI
agent read it, or that native ETABS/OpenSees models are physically equivalent.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md"
SKILL = ".agents/skills/etabs-opensees-read-first/SKILL.md"
EXPECTED_TAGS = {
    1, 2, 3, 4, 5, 6, 7, 8,
    13, 14, 23, 24, 25, 26, 35, 36,
    41, 42, 51, 52, 53, 54, 63, 64,
    69, 70, 71, 72, 73, 74, 75, 76,
}


def contents(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ReadFirstEngineeringContractTests(unittest.TestCase):
    def test_canonical_contract_and_full_skill_exist(self) -> None:
        contract = contents(CONTRACT)
        skill = contents(SKILL)
        for required in (
            "32 genuine foundation support",
            "44 shear-wall",
            "GRAVITY_1.0D_1.0L",
            "Table 5-1",
            "LEGACY_GROSS_SHELL",
            "3041.266",
            "768.045",
            "V10_7",
        ):
            self.assertIn(required, contract, msg=required)
        self.assertTrue(skill.startswith("---\nname: etabs-opensees-read-first\n"))
        self.assertIn("## 6. Complete agent/task prompt", skill)
        self.assertIn("BEFORE ANY EDIT", skill)
        self.assertIn("not a source of solver PASS", skill)

    def test_canonical_primary_tags_exactly_32(self) -> None:
        contract = contents(CONTRACT)
        anchor = "The current primary OpenSees base support tag set is:"
        self.assertIn(anchor, contract)
        block = contract.split(anchor, 1)[1].split("```text", 1)[1].split("```", 1)[0]
        tags = [int(t) for t in re.findall(r"\b\d+\b", block)]
        self.assertEqual(len(tags), 32)
        self.assertEqual(len(tags), len(set(tags)))
        self.assertEqual(set(tags), EXPECTED_TAGS)

    def test_load_purpose_firewall_not_ambiguous(self) -> None:
        contract = contents(CONTRACT)
        skill = contents(SKILL)
        for value in (
            "100% dead + 100% live",
            "GRAVITY_1.0D_1.0L",
            "NBC 105:2025",
            "0.60",
            "0.30",
            "0.00",
            "NEVER",
        ):
            self.assertIn(value.lower(), contract.lower(), msg=value)
        self.assertIn("Full gravity benchmark", skill)
        self.assertIn("Seismic weight", skill)

    def test_entry_points_refer_to_contract_and_skill_up_front(self) -> None:
        roots = (
            "AGENTS.md",
            "CLAUDE.md",
            ".github/copilot-instructions.md",
            "engineering/rules/CORE_RULES.md",
            ".agents/skills/token-efficient-thesis/SKILL.md",
            ".claude/skills/token-saving/SKILL.md",
            ".github/pull_request_template.md",
            ".github/agents/etabs-opensees-engineer.agent.md",
            ".claude/skills/etabs-opensees-read-first/SKILL.md",
        )
        for path in roots:
            with self.subTest(path=path):
                data = contents(path)
                # Up-front link matters: a reference hidden in a giant file is
                # not the intended first-read contract.
                initial = data[:2400]
                self.assertIn("READ_FIRST_PHYSICAL_MODEL_CONTRACT.md", initial)
                self.assertIn("etabs-opensees-read-first/SKILL.md", initial)

    def test_new_agent_frontmatter(self) -> None:
        data = contents(".github/agents/etabs-opensees-engineer.agent.md")
        self.assertTrue(data.startswith("---\nname: etabs-opensees-engineer\n"))
        self.assertIn("Actual physical foundation = 32 support joints", data)
        self.assertIn("full gravity", data.lower())


if __name__ == "__main__":
    unittest.main()
