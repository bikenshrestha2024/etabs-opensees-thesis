"""Ensure legacy ESM/MRSM sources publish NEW review outputs under module folders.

No native ETABS/OpenSees execution; source files are synthetic only.
[REF docs/source/components/inputs/output_layout.py.md]
[REF docs/source/components/validation/seismic_review_bundle.py.md]
"""
import json
from pathlib import Path
from zipfile import ZipFile

from components.inputs.output_layout import stage_review_owner
from components.validation.seismic_review_bundle import bundle_seismic_review


def test_legacy_selected_esms_publish_under_03_esm(tmp_path):
    export=tmp_path/"export"
    legacy=export/"OpenSees_Analysis_Results"/"ULS_Floor_3_long_source_name"
    legacy.mkdir(parents=True)
    (export/"OpenSees_Complete_Model_Config_V118.json").write_text("{}")
    (legacy/"NBC105_ESM_Calculation_ULS_X+_E0_V111.json").write_text(
        json.dumps({"limit_state":"ULS","direction_case":"ULS_X+_E0"}))
    assert stage_review_owner(export,legacy,"ESM")==export/"03_ESM"
    result=bundle_seismic_review(export,legacy,method="ESM",
                                include_comparison_template=False)
    zip_path=Path(result["zip"])
    assert zip_path.parent==export/"03_ESM"/"07_EXPORT_ZIP"
    assert Path(result["folder"]).parent==export/"03_ESM"/"REVIEW_SNAPSHOTS"
    with ZipFile(zip_path) as z:
        assert any("NBC105_ESM_Calculation_ULS_X+_E0_V111.json" in n
                   for n in z.namelist())
    assert (legacy/"NBC105_ESM_Calculation_ULS_X+_E0_V111.json").exists()
    assert not (legacy/"07_EXPORT_ZIP").exists()


def test_canonical_case_preserves_local_review_owner(tmp_path):
    export=tmp_path/"export"
    case=export/"05_MRSM"/"RUNS"/"ULS"/"caseA"
    case.mkdir(parents=True)
    assert stage_review_owner(export,case,"MRSM")==case


def test_wrong_stage_under_same_export_redirects_to_selected_stage(tmp_path):
    export=tmp_path/"export"
    other=export/"02_GRAVITY"/"RUNS"/"sample"
    other.mkdir(parents=True)
    assert stage_review_owner(export,other,"ESM")==export/"03_ESM"


def test_explicit_external_output_is_preserved(tmp_path):
    export=tmp_path/"export";export.mkdir()
    external=tmp_path/"external";external.mkdir()
    assert stage_review_owner(export,external,"ESM")==external
