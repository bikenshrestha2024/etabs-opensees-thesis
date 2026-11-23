"""Evidence-aware 1–9 workflow summary, synthetic source/manifest fixtures only.

[REF docs/source/OpenSees_Workflow_V144.py.md]
"""
import hashlib
import json
from pathlib import Path

from OpenSees_Workflow_V144 import workflow_evidence_status
from components.inputs.output_contract import create_case_run, record_case_status


def test_esm_review_snapshot_is_not_executed_case(tmp_path):
    root=tmp_path
    snapshot=root/"03_ESM"/"REVIEW_SNAPSHOTS"/"old"/"OpenSees_Direct_Equivalent_Static"/"ULS"/"ULS_Xminus_E0"/"JSON"
    snapshot.mkdir(parents=True)
    (snapshot/"NBC105_ESM_Calculation_ULS_X-_E0_V111.json").write_text(
        '{"calculation_only":true}')
    result=workflow_evidence_status(root)
    assert result[4][0]=="REVIEW SNAPSHOT ONLY - NOT EXECUTED"
    assert "not a solver run" in result[4][1]


def test_manifest_complete_modal_same_selected_model_not_engineering_approved(tmp_path):
    root=tmp_path
    model=root/"OpenSees_Complete_Model_Data_V118.json"
    model.write_text('{"source":"A"}')
    sha=hashlib.sha256(model.read_bytes()).hexdigest()
    run=create_case_run(root,"MODAL","MODAL_X",state="ULS",model_sha256=sha)
    (run/"02_RESULTS"/"NBC105_Modal_V111.json").write_text('{"periods":[2.4]}')
    record_case_status(run,"COMPLETED_SOLVER_ONLY")
    result=workflow_evidence_status(root)
    assert result[3][0]=="MANIFEST COMPLETED - NUMERICAL EVIDENCE UNVERIFIED"
    assert "MODEL SHA MATCHED" in result[3][1]
    assert "structural" in result[3][1].lower()


def test_wrong_model_sha_rejected(tmp_path):
    root=tmp_path
    model=root/"OpenSees_Complete_Model_Data_V118.json"
    model.write_text('{"source":"B"}')
    run=create_case_run(root,"MRSM","X_E0",state="ULS",model_sha256="a"*64)
    (run/"02_RESULTS"/"MRSM_Results_V132.json").write_text("{}")
    record_case_status(run,"COMPLETED_SOLVER_ONLY")
    result=workflow_evidence_status(root)
    assert result[5][0]=="CANDIDATE - MODEL IDENTITY MISMATCH"
    assert "SHA" in result[5][1]


def test_no_file_preserves_absence_uncertainty(tmp_path):
    assert "NO FILE" in workflow_evidence_status(tmp_path)[2][0]


def test_legacy_candidate_remains_not_verified(tmp_path):
    legacy=tmp_path/"OpenSees_Analysis_Results"/"old"
    legacy.mkdir(parents=True)
    (legacy/"NBC105_Modal_V111.json").write_text("{}")
    result=workflow_evidence_status(tmp_path)
    assert "CANDIDATE" in result[3][0]
    assert "NOT checked" in result[3][1]
