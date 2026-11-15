"""Real-source reaction join regression without executing ETABS/OpenSees."""
import json
import tempfile
import unittest
from pathlib import Path

from components.gravity.three_case_comparison import join_source_etabs_reactions


class FullSourceReactionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.result=self.root/"Gravity_Result_V110.json"
        # Real production contract is 76 source restrained and 32 primary;
        # keep this synthetic fixture physically transparent and no solver.
        self.primary={i: i<=32 for i in range(1,77)}
        self.rows=[]
        for node in range(1,98):
            self.rows.append(dict(
                node_tag=node,
                rz_32_kN=(2. if node<=32 else None),
                rz_76_kN=(1. if node<=76 else None),
                rz_97_kN=1.))
        self.mapping=[dict(
            opensees_node=i,etabs_unique=str(1000+i),
            etabs_FZ_kN=(2. if i<=32 else 0.),
            selected=(i<=32),source_restraints=[1]*6)
            for i in range(1,77)]
        self.audit=dict(mode="ETABS_NONZERO_REACTION_DIAGNOSTIC",
            case="1. DL + LL",original_support_count=76,
            kept_support_count=32,etabs_total_FZ_kN=64.,
            mapping=self.mapping)
        self.available={"32":({"result_path":str(self.result)},
             {"reactions":[{"node_tag":i} for i in range(1,33)]})}
        self.save()

    def save(self):
        (self.root/"ETABS_Nonzero_Reaction_Support_Audit.json").write_text(
            json.dumps(self.audit),encoding="utf-8")

    def test_all_97_join_and_44_zero_etabs_source_reactions(self):
        rows,s=join_source_etabs_reactions(self.available,self.rows)
        self.assertEqual(len(rows),97)
        self.assertEqual(s["source_support_count"],76)
        self.assertEqual(s["source_fixed_released_in_32"],44)
        self.assertEqual(s["opensees_76_reaction_at_source_zero_ETABS_points_kN"],44.)
        self.assertEqual(s["sum_abs_delta_source_76_kN"],76.)
        self.assertEqual(rows[32]["original_ETABS_FZ_kN"],0.)
        self.assertEqual(rows[32]["status"],"SOURCE_RESTRAINED_ZERO_ETABS_REACTION")
        self.assertIsNone(rows[76]["original_ETABS_FZ_kN"])
        self.assertIn("NO_ETABS_NODE",rows[76]["status"])
        self.assertEqual(rows[0]["source_dof"],"111111")

    def test_absent_source_audit_is_explicit_not_fabricated(self):
        (self.root/"ETABS_Nonzero_Reaction_Support_Audit.json").unlink()
        rows,meta=join_source_etabs_reactions(self.available,self.rows)
        self.assertEqual(rows,[])
        self.assertEqual(meta["status"],"SOURCE_ETABS_SUPPORT_AUDIT_NOT_FOUND")

    def test_wrong_source_totals_and_duplicate_node_mapping_fail_closed(self):
        self.audit["etabs_total_FZ_kN"]=100.
        self.save()
        with self.assertRaisesRegex(ValueError,"declared total"):
            join_source_etabs_reactions(self.available,self.rows)
        self.audit["etabs_total_FZ_kN"]=64.
        self.mapping[-1]["opensees_node"]=75
        self.save()
        with self.assertRaisesRegex(ValueError,"Duplicate ETABS"):
            join_source_etabs_reactions(self.available,self.rows)

    def test_wrong_primary_support_identity_fails_closed(self):
        self.audit["kept_support_count"]=31
        self.save()
        with self.assertRaisesRegex(ValueError,"identity/support counts"):
            join_source_etabs_reactions(self.available,self.rows)


if __name__=="__main__":
    unittest.main()
