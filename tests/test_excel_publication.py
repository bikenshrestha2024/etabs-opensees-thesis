"""Byte preservation, portable registry, launcher and historical compatibility."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
from unittest.mock import patch
import pytest
from tools.restore_legacy_excel_paths import restore_legacy_workbooks
from components.inputs.project_workbooks import copy_project_workbooks,registered_project_source

ROOT=Path(__file__).resolve().parents[1]


def test_all_distributed_workbooks_are_catalogued_under_excel():
    entries=json.loads((ROOT/'excel/WORKBOOK_CATALOG.json').read_text())['workbooks']
    assert len(entries)==68
    actual=set(subprocess.check_output(['git','ls-files','*.xlsx','*.xlsm','*.xls','*.xlsb'],cwd=ROOT,text=True).splitlines())
    assert actual=={e['path'] for e in entries}
    for entry in entries:
        path=ROOT/entry['path']
        with path.open('rb') as stream:
            prefix=stream.read(256)
            if prefix.startswith(b'version https://git-lfs.github.com/spec/v1'):
                assert ('oid sha256:'+entry['sha256']).encode() in prefix
                assert ('size '+str(entry['bytes'])).encode() in prefix
            else:
                stream.seek(0)
                assert hashlib.file_digest(stream,'sha256').hexdigest()==entry['sha256']
                assert path.stat().st_size==entry['bytes']


def test_main_launcher_delegates_and_keeps_previous_names():
    from tools.audit_active_repository import CANONICAL
    assert CANONICAL[1]=='01_WORKFLOW_START.py'
    with patch('runpy.run_path') as start:
        exec(compile((ROOT/'01.py').read_text(),'01.py','exec'),{'__name__':'__main__','__file__':str(ROOT/'01.py')})
    start.assert_called_once_with(str(ROOT/'RUN_ETABS_TO_OPENSEES.py'),run_name='__main__')
    assert (ROOT/'01_WORKFLOW_START.py').is_file()
    with patch('runpy.run_path') as ordered_start:
        exec(compile((ROOT/'01_WORKFLOW_START.py').read_text(),
                     '01_WORKFLOW_START.py','exec'),
             {'__name__':'__main__','__file__':str(ROOT/'01_WORKFLOW_START.py')})
    ordered_start.assert_called_once_with(str(ROOT/'01.py'),run_name='__main__')


def test_restore_is_planned_then_byte_exact_and_never_overwrites(tmp_path):
    folder=tmp_path/'excel';folder.mkdir();source=folder/'example.xlsx';source.write_bytes(b'original synthetic fixture')
    catalog={'workbooks':[{'path':'excel/example.xlsx','legacy_path':'old/example.xlsx','sha256':hashlib.sha256(source.read_bytes()).hexdigest()}]}
    (folder/'WORKBOOK_CATALOG.json').write_text(json.dumps(catalog))
    assert restore_legacy_workbooks(tmp_path)[0]['status']=='PLANNED'
    assert not (tmp_path/'old').exists()
    assert restore_legacy_workbooks(tmp_path,apply=True)[0]['status']=='RESTORED'
    assert (tmp_path/'old/example.xlsx').read_bytes()==source.read_bytes()
    (tmp_path/'old/example.xlsx').write_bytes(b'other research output')
    with pytest.raises(ValueError,match='Refusing to overwrite'):
        restore_legacy_workbooks(tmp_path,apply=True)


def test_export_copies_only_small_established_calculators(tmp_path):
    from components.inputs.project_workbooks import CALCULATOR
    source=tmp_path/'runtime';books=source/'excel/source';books.mkdir(parents=True)
    (books/CALCULATOR).write_bytes(b'synthetic calculator')
    (books/'full_table.xlsx').write_bytes(b'should not be copied')
    export=tmp_path/'export';export.mkdir()
    copied=copy_project_workbooks(source,export)
    assert [Path(p).name for p in copied]==[CALCULATOR]
    assert not (export/'excel/source/full_table.xlsx').exists()


def test_relative_registry_paths_and_lfs_pointer_feedback(tmp_path,monkeypatch):
    edb=tmp_path/'model.EDB';edb.write_bytes(b'synthetic model')
    (tmp_path/'OpenSees_Element_Connectivity.json').write_text(json.dumps({'source_edb':str(edb)}))
    source=tmp_path/'input.xlsx';source.write_bytes(b'synthetic workbook')
    registry=tmp_path/'custom.json'
    registry.write_text(json.dumps({'source_edb_sha256':hashlib.sha256(edb.read_bytes()).hexdigest(),
        'sources':{'etabs_full_table':{'path':'input.xlsx','sha256':hashlib.sha256(source.read_bytes()).hexdigest()}}}))
    monkeypatch.setenv('OPENSEES_PROJECT_SOURCES',str(registry))
    assert registered_project_source(tmp_path,'etabs_full_table')==str(source.resolve())
    source.write_text('version https://git-lfs.github.com/spec/v1\noid sha256:abcd\nsize 100\n')
    with pytest.raises(ValueError,match='git lfs pull'):
        registered_project_source(tmp_path,'etabs_full_table')
