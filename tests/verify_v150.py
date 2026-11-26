import json
import unittest,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from components.validation.nonlinear_performance import template,assess
class Performance(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).parent);self.file=Path(self.tmp.name)/'NBC105_Nonlinear_Time_History_Summary_V116.json'
  self.c=template();self.c.update(model_sha256='a'*64,performance_objective='ULS project objective',expected_pair_ids=['A','B','C']);self.c['criteria']=self.c['criteria'][:1];self.c['criteria'][0]['reviewed']=True
 def tearDown(self):self.tmp.cleanup()
 def rows(self):
  rows=[]
  records=[]
  for pair in self.c['expected_pair_ids']:
   for orientation in ['XY','YX']:
    filename=f'NBC105_NLTHA_{pair}_{orientation}_history.csv'
    history=self.file.with_name(filename)
    history.write_text('time_s,displacement_m\n0.01,0.0\n10.0,0.01\n',encoding='utf-8')
    history.with_name(filename+'.metadata.json').write_text(json.dumps({
        'status':'completed','limit_state':'ULS','model_data_sha256':'a'*64}),encoding='utf-8')
    records.append(dict(pair_id=pair,orientation=orientation,status='COMPLETED_FULL_RECORD',
        history_csv=filename,duration_s=10.0,full_record_duration_s=10.0))
    rows.append(dict(pair_id=pair,orientation=orientation,status='COMPLETED_FULL_RECORD',model_sha256='a'*64,
        metric='peak_edge_drift_X',demand=.01,unit='ratio',result_file=str(self.file)))
  self.file.write_text(json.dumps(dict(limit_state_context='ULS',records=records)),encoding='utf-8')
  return rows
 def test_existing_file_cannot_substitute_for_matching_full_record(self):
  rows=self.rows()
  self.c['limit_state']='SLS'
  self.assertEqual(assess(self.c,rows)['overall'],'INCOMPLETE')
  self.c['limit_state']='ULS'
  history=self.file.with_name('NBC105_NLTHA_A_XY_history.csv')
  history.write_text('time_s,displacement_m\n0.01,0.0\n0.02,0.01\n',encoding='utf-8')
  self.assertEqual(assess(self.c,rows)['overall'],'INCOMPLETE')
 def test_empty_criteria_are_incomplete(self):
  self.c['criteria']=[]
  self.assertEqual(assess(self.c,self.rows())['overall'],'INCOMPLETE')
 def test_orientation_and_missing(self):
  rows=self.rows();rows[-1]['demand']=.03;self.assertEqual(assess(self.c,rows)['overall'],'FAIL');self.assertEqual(assess(self.c,rows[:-1])['overall'],'INCOMPLETE')
 def test_truncated(self):
  rows=self.rows();rows[0]['status']='COMPLETED_TRUNCATED_TRIAL';self.assertEqual(assess(self.c,rows)['overall'],'INCOMPLETE')
 def test_review_requires_boolean(self):
  self.c['criteria'][0]['reviewed']='false';self.assertEqual(assess(self.c,self.rows())['overall'],'INCOMPLETE')
 def test_mean_and_exact_seven(self):
  self.c['expected_pair_ids']=[str(i) for i in range(8)];rows=self.rows();rows[0]['demand']=.03
  r=assess(self.c,rows)['checks'][0];self.assertAlmostEqual(r['demand'],(.03+7*.01)/8)
  self.c['expected_pair_ids']=self.c['expected_pair_ids'][:7];self.assertEqual(assess(self.c,self.rows())['overall'],'INCOMPLETE')
 def test_units_and_fingerprint(self):
  rows=self.rows();rows[0]['unit']='percent';self.assertEqual(assess(self.c,rows)['overall'],'INCOMPLETE');rows=self.rows();rows[0]['model_sha256']='b'*64;self.assertEqual(assess(self.c,rows)['overall'],'INCOMPLETE')
 def test_small_trial_and_nan(self):
  self.c['expected_pair_ids']=['A'];self.assertEqual(assess(self.c,self.rows())['overall'],'INCOMPLETE');self.c['torsion_sensitive']=False;rows=self.rows();rows[0]['demand']='nan';self.assertEqual(assess(self.c,rows)['overall'],'INCOMPLETE')
if __name__=='__main__':unittest.main()

