"""TDD regression for actual per-run 07_EXPORT_ZIP ownership (no ETABS/OpenSees)."""
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile

from components.inputs.review_zip_paths import review_zip_directory
from components.ui.organized_results import publish_mrsm_review
from components.ui.history_review_tools import export_review_zip
from components.validation.seismic_review_bundle import bundle_seismic_review


def _run(tmp_path, stage="05_MRSM"):
    project=tmp_path/"export";project.mkdir(exist_ok=True)
    run=project/stage/"RUNS"/"ULS"/"example"/"20261122T164706_test"
    for child in ("00_INPUT_SOURCE","02_RESULTS","06_REVIEW","07_EXPORT_ZIP"):
        (run/child).mkdir(parents=True,exist_ok=True)
    (run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").write_text(
        '{"schema":"ETABS_OPENSEES_OUTPUT_CASE_V1","stage":"'+stage+'"}',
        encoding="utf8")
    return project,run


def test_resolves_existing_run_zip_from_nested_solver_folder(tmp_path):
    _project,run=_run(tmp_path)
    assert review_zip_directory(run/"02_RESULTS")==run/"07_EXPORT_ZIP"
    assert review_zip_directory(run/"02_RESULTS"/"Seismic_Review_Packages")==run/"07_EXPORT_ZIP"
    assert review_zip_directory(run/"06_REVIEW"/"Organized_Results")==run/"07_EXPORT_ZIP"


def test_mrsm_seismic_bundle_zip_goes_to_run_owned_zip_folder(tmp_path):
    project,run=_run(tmp_path)
    (project/"OpenSees_Complete_Model_Config_V118.json").write_text("{}",encoding="utf8")
    (run/"02_RESULTS"/"MRSM_Results_V132.json").write_text(
        '{"X_E0":{"force_scale":1.0}}',encoding="utf8")
    (run/'02_RESULTS'/'ULS_X_E0_Support_Reactions_V132.csv').write_text('tag,rz\n1,2',encoding='utf8')
    (run/'06_REVIEW'/'SAVED_CASE_COMPLETENESS.json').write_text('{"verified":6}',encoding='utf8')
    (run/'01_LOGS').mkdir()
    (run/'01_LOGS'/'MRSM_worker.log').write_text('saved solver log',encoding='utf8')
    metadata=run/'02_RESULTS'/'00_PROCESSING_METADATA'
    metadata.mkdir()
    (metadata/'MRSM_Results.processing.json').write_text('{}',encoding='utf8')
    foreign=project/'02_MODEL'/'REBUILDS'/'OTHER'
    foreign.mkdir(parents=True)
    (foreign/'OpenSees_Complete_Model_Config_V118.json').write_text('{"other": true}',encoding='utf8')
    result=bundle_seismic_review(project,run/"02_RESULTS",method="MRSM",
                                include_comparison_template=False)
    path=Path(result["zip"])
    assert path.parent==run/"07_EXPORT_ZIP"
    assert path.is_file()
    assert Path(result["folder"]).parent==run/"06_REVIEW"/"Seismic_Review_Packages"
    with ZipFile(path) as z:
        assert "REVIEW_MANIFEST.json" in z.namelist()
        assert any(name.endswith('/MRSM_worker.log') for name in z.namelist())
        assert 'OpenSees_Direct/ULS_X_E0_Support_Reactions_V132.csv' in z.namelist()
        assert '06_REVIEW/SAVED_CASE_COMPLETENESS.json' in z.namelist()
        assert not any('processing.json' in name or '/OTHER/' in name for name in z.namelist())


def test_mrsm_organized_zip_goes_to_seventh_run_folder(tmp_path):
    _project,run=_run(tmp_path)
    (run/"02_RESULTS"/"MRSM_Results_V132.json").write_text(
        '{"X_E0":{"force_scale":1.0}}',encoding="utf8")
    result=publish_mrsm_review(run/"02_RESULTS")
    path=Path(result["zip_files"]["MRSM_RUN"])
    assert path.parent==run/"07_EXPORT_ZIP"
    assert path.exists()
    assert Path(result["folder"]).parent==run/"06_REVIEW"/"Organized_Results"
    with ZipFile(path) as z:
        assert "MRSM/02_RESULTS/MRSM_Results_V132.json" in z.namelist()


def test_history_manual_zip_goes_to_sibling_seventh_run_folder(tmp_path):
    _project,run=_run(tmp_path,"07_NONLINEAR_TIME_HISTORY")
    (run/"02_RESULTS"/"Nonlinear_Time_History_RunConfig.json").write_text(
        '{"trial_duration_s":0}',encoding="utf8")
    result,manifest=export_review_zip(run/"02_RESULTS","nonlinear")
    assert Path(result).parent==run/"07_EXPORT_ZIP"
    assert manifest["status"]=="REVIEW_EVIDENCE_NOT_ENGINEERING_ACCEPTANCE"


def test_legacy_noncanonical_root_gets_local_seventh_folder(tmp_path):
    root=tmp_path/"legacy_results";root.mkdir()
    assert review_zip_directory(root)==root/"07_EXPORT_ZIP"
