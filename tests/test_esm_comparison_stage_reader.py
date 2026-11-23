"""Follow new ESM comparison folder without cross-model contamination.

[REF docs/source/components/equivalent_static/organized_exports.py.md]
Synthetic EDB and workbook bytes; no COM/ETABS process.
"""
from pathlib import Path
import hashlib
import json

from components.equivalent_static.organized_exports import _stage_comparison_sources


def test_legacy_combined_reader_accepts_only_matching_source_and_cases(tmp_path):
    export=tmp_path/"export";export.mkdir()
    edb=tmp_path/"source.edb";edb.write_bytes(b"model A")
    (export/"OpenSees_Element_Connectivity.json").write_text(json.dumps({
        "source_edb":str(edb)}))
    case="ULS_X+_E0"
    legacy=export/"OpenSees_Analysis_Results"/"ULS_Floor_3_old";legacy.mkdir(parents=True)
    (legacy/("NBC105_ESM_Calculation_"+case+"_V111.json")).write_text(json.dumps({
        "direction_case":case,"limit_state":"ULS","stories":[]}))
    folder=export/"03_ESM"/"COMPARISONS";folder.mkdir(parents=True)
    x=folder/"ETABS_Linked_vs_OpenSees_Direct_ESM_20261123_123456.json"
    x.write_text(json.dumps({"source_edb_sha256":hashlib.sha256(edb.read_bytes()).hexdigest(),
                             "rows":[{"case":case}]}))
    workbook=x.with_suffix(".xlsx");workbook.write_bytes(b"synthetic workbook")
    located=list(_stage_comparison_sources(legacy,(legacy,)))
    assert ("comparison",x) in located
    assert ("comparison",workbook) in located
    edb.write_bytes(b"replaced source model")
    assert list(_stage_comparison_sources(legacy,(legacy,)))==[]


def test_legacy_combined_reader_rejects_mismatched_case(tmp_path):
    export=tmp_path/"export";export.mkdir()
    edb=tmp_path/"source.edb";edb.write_bytes(b"source")
    (export/"OpenSees_Element_Connectivity.json").write_text(json.dumps({
        "source_edb":str(edb)}))
    legacy=export/"OpenSees_Analysis_Results"/"ULS_Floor_3_old";legacy.mkdir(parents=True)
    (legacy/"NBC105_ESM_Calculation_ULS_X+_E0_V111.json").write_text(
        json.dumps({"direction_case":"ULS_X+_E0","limit_state":"ULS","stories":[]}))
    folder=export/"03_ESM"/"COMPARISONS";folder.mkdir(parents=True)
    x=folder/"ETABS_Linked_vs_OpenSees_Direct_ESM_20261123_123457.json"
    x.write_text(json.dumps({"source_edb_sha256":hashlib.sha256(edb.read_bytes()).hexdigest(),
                             "rows":[{"case":"ULS_Y+_E0"}]}))
    assert list(_stage_comparison_sources(legacy,(legacy,)))==[]
