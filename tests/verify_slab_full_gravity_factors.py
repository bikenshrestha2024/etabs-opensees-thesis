"""Regression: slab load-path workbook separates full gravity and seismic preload."""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook
from components.gravity.load_path_formulas import add_formula_audit


class SlabProfilesTest(unittest.TestCase):
    def test_full_gravity_live_one_seismic_preload_point_three(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            (folder/'OpenSees_Load_Conversion_Audit.json').write_text(
                json.dumps({
                    'applied_area_loads':[{
                        'object':29,'pattern':'Live','value':4,
                        'direction_code':10,'load_set':'Source ETABS'}],
                    'etabs_load_pattern_self_weight_multipliers':[]
                }),encoding='utf8')
            data={
                'shells':[{
                    'object':29,'category':'FLOOR','nodes':[1,2,3,4],
                    'area':2.25,
                    'properties':{'thickness':.15,'weight':25}}],
                'frames':[],
                'nodes':{'1':[0,0,3],'2':[1.5,0,3],
                         '3':[1.5,1.5,3],'4':[0,1.5,3]}}
            cfg={'gravity_factors':{'Live':.3},'mass_factors':{'Live':.3}}
            audit_module=types.ModuleType('OpenSees_Mapping_Audit_V125')
            audit_module.parameter_sources=lambda:[]
            audit_module.source_parameter_inventory=lambda *_:[]
            wb=Workbook()
            with patch.dict(sys.modules,{'OpenSees_Mapping_Audit_V125':audit_module}):
                add_formula_audit(wb,folder,data,cfg)
            full=wb['Surface load formulas']
            seismic=wb['Surface seismic preload']
            self.assertEqual(full['C2'].value,'Live')
            self.assertEqual(full['G2'].value,1.)
            self.assertEqual(full['H2'].value,.3)
            self.assertEqual(full['I2'].value,'=E2*F2')
            self.assertEqual(full['J2'].value,'=I2*G2')
            self.assertEqual(seismic['G2'].value,.3)
            self.assertEqual(seismic['H2'].value,.3)
            self.assertEqual(seismic['J2'].value,'=I2*G2')
            self.assertEqual(full['E2'].value,2.25)
            self.assertEqual(full['F2'].value,4.)
            self.assertEqual(wb['Loaded node path']['H2'].value,
                "='Surface load formulas'!L2")
            output=folder/'validation.xlsx'
            wb.save(output)
            self.assertTrue(output.is_file())

    def test_missing_seismic_factor_must_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            from unittest.mock import patch
            folder=Path(tmp)
            (folder/'OpenSees_Load_Conversion_Audit.json').write_text(
                json.dumps({'applied_area_loads':[{
                    'object':29,'pattern':'Live','value':4,
                    'direction_code':10}],
                    'etabs_load_pattern_self_weight_multipliers':[]}),encoding='utf8')
            data={'shells':[{'object':29,'category':'FLOOR',
                 'nodes':[1,2,3,4],'area':2.25,
                 'properties':{'thickness':.15,'weight':25}}],
                 'frames':[],
                 'nodes':{'1':[0,0,3],'2':[1.5,0,3],
                          '3':[1.5,1.5,3],'4':[0,1.5,3]}}
            with self.assertRaisesRegex(ValueError,'no gravity factor'):
                add_formula_audit(Workbook(),folder,data,{
                    'gravity_factors':{},'mass_factors':{'Live':.3}})


if __name__=='__main__':
    unittest.main()
