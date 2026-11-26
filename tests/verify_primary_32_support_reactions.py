"""Regression tests for the project-specific primary 32-point gravity filter.

[REF docs/review/GRAVITY_REACTION_FILTER_DIAGNOSTIC.md]
"""
import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from components.gravity.etabs_reaction_support_filter import (
    PROJECT_PRIMARY_32,classify_supports,export_primary_32_comparison,
    MODE)

class Primary32Tests(unittest.TestCase):
    def test_confirmed_32_tags_unique(self):
        self.assertEqual(len(PROJECT_PRIMARY_32),32)
        self.assertEqual(len(set(PROJECT_PRIMARY_32)),32)
        self.assertEqual(set(PROJECT_PRIMARY_32),
            {1,2,3,4,5,6,7,8,13,14,23,24,25,26,
             35,36,41,42,51,52,53,54,63,64,69,70,71,72,73,74,75,76})

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"source.csv"
        self.mapping={str(i):dict(etabs_unique_name=str(i),etabs_FZ_kN=1000.0)
                      for i in PROJECT_PRIMARY_32}
        self.original={str(i):[1]*6 for i in range(1,77)}
        for i in range(1,77):
            self.mapping.setdefault(str(i),
                dict(etabs_unique_name=str(i),etabs_FZ_kN=0.0))
        self.topology=dict(node_map=[
            dict(etabs_point_name=str(i),opensees_node_tag=i)
            for i in range(1,77)])
        with self.path.open("w",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["Story","Label","Unique Name","Output Case","FZ"])
            for i in range(1,77):
                writer.writerow(["Base",str(i),str(i),"1. DL + LL",
                                 1000 if i in PROJECT_PRIMARY_32 else 0])

    def test_exact_32_filter_from_original_table(self):
        selected,audit=classify_supports(self.path,self.topology,self.original)
        self.assertEqual(set(map(int,selected)),set(PROJECT_PRIMARY_32))
        self.assertEqual(audit["kept_support_count"],32)
        self.assertEqual(audit["released_support_count"],44)

    def test_rejects_table_that_drops_one_requested_support(self):
        with patch("components.gravity.etabs_reaction_support_filter.read_etabs_joint_reactions") as read:
            read.return_value=dict(self.mapping)
            read.return_value["41"]["etabs_FZ_kN"]=0
            with self.assertRaisesRegex(ValueError,"Missing=.*41"):
                classify_supports(self.path,self.topology,self.original)

    def test_32_comparison_refuses_duplicate_mapping_and_nonfinite_source(self):
        import copy
        _,audit=classify_supports(self.path,self.topology,self.original)
        result=dict(ok=True,wall_support_strategy=MODE,
                    support_node_tags=list(PROJECT_PRIMARY_32),
                    reactions=[dict(node_tag=i,rz_kN=1000.)
                               for i in PROJECT_PRIMARY_32],
                    report=dict(support_vertical_reaction_kN=32000.))
        duplicated=copy.deepcopy(audit)
        duplicated["mapping"].append(copy.deepcopy(next(
            row for row in duplicated["mapping"] if row["selected"])))
        with self.assertRaisesRegex(ValueError,"Duplicate selected ETABS"):
            export_primary_32_comparison(result,duplicated,Path(self.tmp.name)/"dup")
        invalid=copy.deepcopy(audit)
        next(row for row in invalid["mapping"] if row["selected"]
             )["etabs_FZ_kN"]=float("nan")
        with self.assertRaisesRegex(ValueError,"Nonfinite original ETABS"):
            export_primary_32_comparison(result,invalid,Path(self.tmp.name)/"nan")
        self.assertFalse((Path(self.tmp.name)/"dup").exists())
        self.assertFalse((Path(self.tmp.name)/"nan").exists())

    def test_export_refuses_linked_destinations_and_preserves_report(self):
        import json
        selected,audit=classify_supports(self.path,self.topology,self.original)
        result=dict(ok=True,wall_support_strategy=MODE,
                    support_node_tags=list(PROJECT_PRIMARY_32),
                    reactions=[dict(node_tag=i,rz_kN=1000.)
                               for i in PROJECT_PRIMARY_32],
                    report=dict(support_vertical_reaction_kN=32000.))
        external=Path(self.tmp.name)/"outside"
        external.mkdir()
        link=Path(self.tmp.name)/"linked_output"
        try:
            link.symlink_to(external,target_is_directory=True)
        except (OSError,NotImplementedError):
            self.skipTest("Host cannot create directory symlink")
        with self.assertRaisesRegex(ValueError,"linked primary-32"):
            export_primary_32_comparison(result,audit,link)
        self.assertEqual(list(external.iterdir()),[])
        output=Path(self.tmp.name)/"safe_output"
        export_primary_32_comparison(result,audit,output)
        self.assertEqual(list(output.glob(".primary32_*")),[])
        self.assertTrue((output/"Primary_32_ETABS_OpenSees_Reactions.csv").is_file())
        self.assertTrue((output/"Primary_32_ETABS_OpenSees_Reactions.xlsx").is_file())
        self.assertEqual(json.loads(
            (output/"Primary_32_ETABS_OpenSees_Reactions.json").read_text()
        )["structural_validation"],"NOT_ESTABLISHED")

    def test_original_six_dof_restraints_must_be_explicit_binary(self):
        for invalid in ([1,1,1], "111111", [1,1,"0",1,1,1],
                        [1,1,2,1,1,1], [1,1,0.5,1,1,1], None):
            with self.subTest(flags=invalid):
                modified=dict(self.original)
                modified["1"]=invalid
                with self.assertRaisesRegex(ValueError,"six-DOF restraint"):
                    classify_supports(self.path,self.topology,modified)
        selected,_=classify_supports(self.path,self.topology,self.original)
        self.assertEqual(len(selected),32)

    def test_global_equilibrium_does_not_hide_pointwise_mismatch(self):
        _,audit=classify_supports(self.path,self.topology,self.original)
        tags=list(PROJECT_PRIMARY_32)
        values={tag:1000. for tag in tags}
        values[tags[0]]+=768.045
        values[tags[1]]-=768.045
        result=dict(ok=True,wall_support_strategy=MODE,
                    support_node_tags=tags,
                    reactions=[dict(node_tag=tag,rz_kN=values[tag]) for tag in tags],
                    report=dict(support_vertical_reaction_kN=32000.))
        summary=export_primary_32_comparison(result,audit,self.tmp.name)
        self.assertAlmostEqual(summary["global_difference_kN"],0.,places=8)
        self.assertEqual(summary["global_screening_status"],"WITHIN_SCREEN_ONLY")
        self.assertEqual(summary["numerical_agreement"],"MISMATCH")
        self.assertEqual(summary["pointwise_screening_status"],"POINTWISE_RESIDUAL_EXCEEDS_NUMERICAL_SCREEN")
        self.assertAlmostEqual(summary["worst_abs_node_difference_kN"],768.045)
        self.assertAlmostEqual(summary["sum_absolute_nodal_difference_kN"],1536.09)
        self.assertAlmostEqual(summary["rms_nodal_difference_kN"],192.01125)
        self.assertEqual(summary["structural_validation"],"NOT_ESTABLISHED")

    def test_export_exact_32_numeric_comparison(self):
        selected,audit=classify_supports(self.path,self.topology,self.original)
        reactions=[dict(node_tag=i,rz_kN=1000.0)
                   for i in PROJECT_PRIMARY_32]
        result=dict(ok=True,wall_support_strategy=MODE,
                    support_node_tags=list(PROJECT_PRIMARY_32),
                    reactions=reactions,
                    report=dict(support_vertical_reaction_kN=32000.0))
        summary=export_primary_32_comparison(result,audit,self.tmp.name)
        self.assertEqual(summary["global_difference_kN"],0)
        self.assertEqual(summary["structural_validation"],"NOT_ESTABLISHED")
        self.assertTrue((Path(self.tmp.name)/"Primary_32_ETABS_OpenSees_Reactions.xlsx").is_file())

if __name__=="__main__":
    unittest.main()
