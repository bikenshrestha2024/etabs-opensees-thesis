"""Source identity and adopted-period regression tests, with synthetic inputs."""
import hashlib
import json
from pathlib import Path
import pytest
from components.inputs.project_workbooks import registered_project_source, _calculator_sync_summary


def test_registry_checks_current_edb_and_source_hash(tmp_path, monkeypatch):
    edb=tmp_path/'ULS.EDB';edb.write_bytes(b'synthetic model')
    source=tmp_path/'assignment.xlsx';source.write_bytes(b'synthetic source')
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    (tmp_path/'OpenSees_Element_Connectivity.json').write_text(json.dumps({'source_edb':str(edb)}))
    registry=tmp_path/'project_sources.private.json'
    registry.write_text(json.dumps({'source_edb_sha256':digest(edb),'sources':{'etabs_assignment':{'path':str(source),'sha256':digest(source)}}}))
    monkeypatch.setenv('OPENSEES_PROJECT_SOURCES',str(registry))
    assert registered_project_source(tmp_path,'etabs_assignment')==str(source.resolve())
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed or missing'):
        registered_project_source(tmp_path,'etabs_assignment')
    edb.write_bytes(b'other model')
    assert registered_project_source(tmp_path,'etabs_assignment') is None


def test_original_engine_sync_layout_keeps_adopted_periods_separate():
    # Lightweight sheet doubles; the original engine writes these labels.
    class Cell:
        def __init__(self,value,coordinate):self.value=value;self.coordinate=coordinate
    class Sheet:
        def __init__(self,rows):self.rows=rows
        def iter_rows(self,**unused):return iter(self.rows)
    wb={'ETABS Sync':Sheet([[Cell('X DIRECTION','A22'),Cell(None,'B22')],
        [Cell('Aw (m²)','A23'),Cell(1.95,'B23')],
        [Cell('Adopted T1 (s)','A27'),Cell(2.03,'B27')],
        [Cell('Y DIRECTION','A34'),Cell(None,'B34')],
        [Cell('Aw (m²)','A35'),Cell(2.20,'B35')],
        [Cell('Adopted T1 (s)','A39'),Cell(1.92,'B39')]]),
        'ETABS_Summary':Sheet([[Cell('Source EDB','A2'),Cell('ULS.EDB','B2')]])}
    source,fields=_calculator_sync_summary(wb)
    assert source=='ULS.EDB'
    assert fields['workbook_adopted_tx']==(2.03,'ETABS Sync!B27')
    assert fields['workbook_adopted_ty']==(1.92,'ETABS Sync!B39')
    assert not any('rayleigh' in k or 'modal' in k for k in fields)


def test_recovered_floor_transfer_uses_actual_frame_and_shell_vectors():
    from components.gravity.load_path_formulas import recovered_vertical_transfers
    p={'nodes':[{'tag':1,'z_m':0},{'tag':2,'z_m':3}],
       'elements':[{'tag':1,'nodes':[1,2]}],
       'global_end_forces':[{'tag':1,'nodes':[1,2],'forces':[0,0,10,0,0,0,0,0,-10,0,0,0]}]}
    rows=recovered_vertical_transfers(p,[0,3])
    assert rows[0]['lower_face_resisting_Fz_kN']==10
    assert rows[1]['crossing_elements']==0
    p['global_end_forces']=[]
    with pytest.raises(ValueError,match='Complete frame and shell'):
        recovered_vertical_transfers(p,[0])


def test_joint_balance_distinguishes_free_joint_and_support():
    from components.gravity.load_path_formulas import vertical_joint_balance
    p={'nodes':[{'tag':1,'z_m':0},{'tag':2,'z_m':3}],
       'elements':[{'tag':1,'nodes':[1,2]}],
       'global_end_forces':[{'tag':1,'nodes':[1,2],'forces':[0,0,10,0,0,0,0,0,-10,0,0,0]}],
       'reactions':[{'node_tag':1,'rz_kN':10}]}
    rows=vertical_joint_balance(p,{2:-10})
    assert rows[0]['is_support'] and not rows[1]['is_support']
    assert all(r['residual_Fz_kN']==0 for r in rows)


def test_mrsm_reuses_attributed_adopted_reference_without_inventing_rayleigh(tmp_path,monkeypatch):
    from components.response_spectrum.model_analysis import mrsm_period_defaults
    import components.inputs.aw_sources as sources
    (tmp_path/'OpenSees_Complete_Model_Data_V118.json').write_text('{}')
    reference={'values':{'workbook_adopted_tx':2.03856740011866,
                         'workbook_adopted_ty':1.9219797767063125},
               'source_workbook':'synthetic reviewed calculator.xlsx'}
    monkeypatch.setattr(sources,'latest_linked_reference',lambda *args:(reference,'OK'))
    values,note=mrsm_period_defaults(tmp_path,{'awx':1.95,'awy':2.20},'ULS')
    assert values=={'T1_X':2.03856740011866,'T1_Y':1.9219797767063125}
    assert 'Research comparison only' in note


def test_same_edb_path_with_changed_content_is_rejected(tmp_path):
    from components.inputs.aw_sources import edb_identity
    edb=tmp_path/'ULS.EDB';edb.write_bytes(b'old')
    audit={'source_edb':str(edb),'source_edb_sha256':hashlib.sha256(edb.read_bytes()).hexdigest()}
    edb.write_bytes(b'new')
    assert edb_identity(str(edb),audit)=='DIFFERENT_EDB'
