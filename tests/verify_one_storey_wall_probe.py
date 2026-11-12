"""Offline structure and source-provenance test for first-storey quad probe.

[REF docs/source/components/nonlinear_time_history/one_storey_wall_probe.py.md]
Does not claim native OpenSees E-SFI convergence.
"""
import json
import tempfile
import unittest
from pathlib import Path

from components.nonlinear_time_history.one_storey_wall_probe import (
    select_first_storey_panel,prepare,
)


def _fixture():
    return {
        'nodes':{
            '1':[0,0,0],'2':[1,0,0],'3':[1,0,3.5],'4':[0,0,3.5],
            '5':[0,0,3.5],'6':[1,0,3.5],'7':[1,0,7.0],'8':[0,0,7.0],
        },
        'shells':[
            {'category':'SHEAR WALL','nodes':[4,3,2,1],
             'properties':{'property':'W-600','thickness':0.6}},
            {'category':'SHEAR WALL','nodes':[5,6,7,8],
             'properties':{'property':'W-600','thickness':0.6}},
        ]
    }


class TestOneStoreyPanel(unittest.TestCase):
    def test_bottom_wall_selected_and_ccw(self):
        panel=select_first_storey_panel(_fixture())
        self.assertEqual(panel['tags'],[1,2,3,4])
        self.assertEqual(panel['base_elevation_m'],0.0)
        self.assertEqual(panel['upper_elevation_m'],3.5)
        self.assertEqual(panel['width_m'],1.0)
        self.assertEqual(panel['thickness_m'],0.6)

    def test_nonrectangular_quad_fails_closed(self):
        source=_fixture()
        source['nodes']['3']=[0.8,0,3.5]
        source['shells']=source['shells'][:1]
        with self.assertRaises(ValueError):
            select_first_storey_panel(source)

    def test_prepare_no_source_modification(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'assembled';source.mkdir()
            data=source/'OpenSees_Complete_Model_Data_V118.json'
            data.write_text(json.dumps(_fixture()),encoding='utf-8')
            original=data.read_bytes()
            target=Path(tmp)/'one-storey'
            path=prepare(source,target)
            report=json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(data.read_bytes(),original)
            self.assertEqual(report['status'],'PREPARED_NOT_RUN')
            self.assertAlmostEqual(report['steel']['cR1'],0.925)
            self.assertAlmostEqual(report['element_poisson_assumed'],0.25)
            self.assertAlmostEqual(report['fsam']['nu'],0.8)
            self.assertEqual(report['panel']['height_m'],3.5)

    def test_reject_nonempty_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'assembled';source.mkdir()
            (source/'OpenSees_Complete_Model_Data_V118.json').write_text(
                json.dumps(_fixture()))
            target=Path(tmp)/'test';target.mkdir()
            (target/'already.txt').write_text('do not overwrite')
            with self.assertRaises(FileExistsError):
                prepare(source,target)


if __name__=='__main__':
    unittest.main()
