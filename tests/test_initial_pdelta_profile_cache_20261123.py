"""Regressions for case-specific initial signed P-Delta cache and supports.

Synthetic inputs only; no native ETABS/OpenSees run or physical approval.
[REF docs/source/components/model/initial_pdelta.py.md]
"""
import inspect
import os
import tempfile
import unittest
from pathlib import Path

from components.model import initial_pdelta
from components.model.support_case_contract import solver_reaction_support_tags
from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32


class InitialPDeltaIdentityTests(unittest.TestCase):
    def _fixture(self, root):
        files=[]
        for name, text in (
            ("OpenSees_Complete_Model_Data_V118.json",'{"nodes":{}}'),
            ("OpenSees_Complete_Model_Config_V118.json",'{"mass_factors":{}}'),
            ("OpenSees_Initial_PDelta_Input_V124.json",'{"X":{},"Y":{}}'),
            ("initial_pdelta.py","module a"),
            ("assembly.py","module b"),
            ("analysis.py","module c"),
        ):
            path=root/name
            path.write_text(text,encoding="utf-8")
            files.append(path)
        return files[:3], files[3:]

    def _digest(self, inputs, sources, **overrides):
        cfg=dict(support_case="PHYSICAL_32",
                 mass_policy="SOURCE_DISTRIBUTED", limit_state="ULS")
        cfg.update(overrides)
        return initial_pdelta._initial_pdelta_fingerprint(
            inputs,sources,**cfg)

    def test_cache_key_is_isolated_by_support_mass_and_limit_state(self):
        with tempfile.TemporaryDirectory() as td:
            inp,src=self._fixture(Path(td))
            base=self._digest(inp,src)
            self.assertEqual(base,self._digest(inp,src))
            self.assertNotEqual(base,self._digest(inp,src,support_case="SOURCE_76"))
            self.assertNotEqual(base,self._digest(inp,src,support_case="WALL_BASE_97"))
            self.assertNotEqual(base,self._digest(inp,src,mass_policy="STORY_LUMPED_NBC"))
            self.assertNotEqual(base,self._digest(inp,src,limit_state="SLS"))

    def test_cache_key_changes_for_each_source_and_refuses_invalid_policy(self):
        with tempfile.TemporaryDirectory() as td:
            inp,src=self._fixture(Path(td))
            baseline=self._digest(inp,src)
            for candidate in (*inp,*src):
                original=candidate.read_bytes()
                candidate.write_bytes(original+b"x")
                self.assertNotEqual(baseline,self._digest(inp,src),candidate.name)
                candidate.write_bytes(original)
            with self.assertRaises(ValueError):
                self._digest(inp,src,mass_policy="UNKNOWN")
            with self.assertRaises(ValueError):
                self._digest(inp,src,support_case="UNKNOWN")
            with self.assertRaises(ValueError):
                self._digest(inp,src,limit_state="UNKNOWN")

    def test_initial_signed_check_basis_is_explicitly_separate_from_sls_modal_state(self):
        # Initial signed IS16700 reference uses ULS by default; SLS modal
        # environment must not silently alter the initial combination basis.
        source=inspect.getsource(initial_pdelta.ensure_initial_checks)
        self.assertIn("OPENSEES_INITIAL_PDELTA_LIMIT_STATE",source)
        self.assertNotIn("os.environ.get('OPENSEES_LIMIT_STATE'",source)

    def test_signed_checks_use_built_32_reaction_tags_not_raw_76_source(self):
        original={str(x):[1]*6 for x in range(1,77)}
        actual=sorted(PROJECT_PRIMARY_32)
        report={"gravity_base_support_tags":actual,
                "support_case_evidence":{"profile":"PHYSICAL_32"}}
        self.assertEqual(len(original),76)
        self.assertEqual(solver_reaction_support_tags(report,"PHYSICAL_32"),actual)
        source=inspect.getsource(initial_pdelta.ensure_initial_checks)
        self.assertIn("solver_reaction_support_tags(built, selected_case)",source)
        self.assertIn("support_nodes",source)
        self.assertNotIn("for n,v in data['supports'].items()",source)
        self.assertNotIn("for n,flags in data['supports'].items()",source)
        self.assertIn("atomic_json(output, outcomes)",source)
        self.assertIn("_initial_pdelta_fingerprint(",source)


if __name__=="__main__":
    unittest.main()
