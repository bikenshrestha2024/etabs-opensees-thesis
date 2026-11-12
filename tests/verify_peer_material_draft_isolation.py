"""PEER specimen research draft must be source-derived, isolated, unapproved.

[REF R01 PEER Report 2015/12 Appendix B.3]
[REF docs/source/components/nonlinear_time_history/one_storey_wall_probe.py.md]
"""
import json
import tempfile
import unittest
from pathlib import Path
from components.nonlinear_time_history.material_draft import prepare


class TestPeerMaterialDraft(unittest.TestCase):
    def test_single_source_transition_and_no_source_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=root/'source';src.mkdir()
            files={
                'OpenSees_Complete_Model_Data_V118.json':{
                    'shells':[{'category':'SHEAR WALL',
                               'properties':{'property':'W1','thickness':0.6}}]},
                'OpenSees_Complete_Model_Config_V118.json':{
                    'nonlinear_parameters_reviewed':False,
                    'nonlinear_materials_file':''},
                'OpenSees_Load_Conversion_Audit.json':{},
                'OpenSees_Source_Model_Metadata_V118.json':{},
            }
            for name,content in files.items():
                (src/name).write_text(json.dumps(content))
            old={p.name:p.read_bytes() for p in src.iterdir()}
            target=root/'research_copy'
            card=prepare(src,target,basis='PEER_2015_12_SINGLE_SOURCE')
            self.assertEqual(card['basis'],'PEER_2015_12_SINGLE_SOURCE')
            self.assertAlmostEqual(card['steel']['cR1'],0.925)
            self.assertAlmostEqual(card['steel']['cR2'],0.0015)
            self.assertAlmostEqual(card['concrete']['fpcc'],-55.778586501732036)
            self.assertEqual(card['status'],'RESEARCH DRAFT; NOT PROJECT CALIBRATED OR APPROVED')
            cfg=json.loads((target/'OpenSees_Complete_Model_Config_V118.json').read_text())
            self.assertFalse(cfg['nonlinear_parameters_reviewed'])
            self.assertEqual(cfg['nonlinear_materials_file'],'Research_Wall_Materials.py')
            self.assertEqual(cfg['nonlinear_wall_fsam_tags'],{'W1':962000})
            self.assertTrue((target/'Research_Wall_Materials.py').exists())
            self.assertEqual(old,{p.name:p.read_bytes() for p in src.iterdir()})

    def test_reject_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/'source';src.mkdir()
            dest=Path(tmp)/'exists';dest.mkdir()
            with self.assertRaises(FileExistsError):
                prepare(src,dest)


if __name__=='__main__':
    unittest.main()
