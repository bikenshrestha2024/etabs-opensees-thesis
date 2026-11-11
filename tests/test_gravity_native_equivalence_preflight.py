"""Synthetic, solver-free tests for gravity restraint/offset preflight."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32
from components.validation.gravity_native_equivalence_preflight import (
    assess, export, _offset,
)


def _make(tmp_path, *, include_offset=True):
    p=tmp_path/"source"
    p.mkdir()
    kept=list(PROJECT_PRIMARY_32)
    # Source restraints are NOT derived from ETABS zero-reaction test.
    original={str(n):[1,1,1,1,1,1] for n in kept+[718]}
    (p/"OpenSees_Complete_Model_Data_V118.json").write_text(
        json.dumps({"supports":original}),encoding="utf-8")
    (p/"OpenSees_Source_Model_Metadata_V118.json").write_text(
        json.dumps({"frames":{"100":{"GetEndLengthOffset":[True,0.2,0.2,1.0,0]}
                                if include_offset else {"GetEndLengthOffset":[]}},
                    "errors":[]}),encoding="utf-8")
    (p/"OpenSees_Element_Connectivity.json").write_text(
        json.dumps({"node_map":[{"opensees_node_tag":n,"etabs_point_name":str(n+200)}
                              for n in kept+[718]]}),encoding="utf-8")
    return p


def test_correctly_reports_released_original_source_support(tmp_path):
    p=_make(tmp_path)
    r=assess(p)
    assert r["engineering_acceptance"]=="NOT_VALIDATED"
    assert r["selected_primary_count"]==32
    assert r["released_by_primary32_count"]==1
    assert r["originally_restrained_released_by_primary32"]==[718]
    assert r["native_frame_rigid_end_zone_review_count"]==1
    assert r["offset_rows"][0]["rigid_zone_factor"]==1.0
    assert any("releases originally restrained" in x for x in r["blockers"])


def test_missing_native_end_offset_is_not_interpreted_as_zero(tmp_path):
    p=_make(tmp_path,include_offset=False)
    r=assess(p)
    assert r["native_offset_missing_or_invalid_count"]==1
    assert r["offset_rows"][0]["status"]=="MISSING_OR_FAILED_NATIVE_OFFSET"


@pytest.mark.parametrize("raw",[[False,-0.1,0.0,1.0,0],
                                 [True,0.0,0.0,1.1,0],
                                 [True,0.0,0.0,float("nan"),0],
                                 [True,0.0,0.0,1.0,1]])
def test_invalid_offsets_do_not_pass(raw):
    assert _offset(raw)["status"]!="NATIVE_OFFSET_CAPTURED"


def test_preflight_requires_original_model_data(tmp_path):
    p=_make(tmp_path)
    (p/"OpenSees_Complete_Model_Data_V118.json").unlink()
    with pytest.raises(FileNotFoundError):
        assess(p)


def test_export_is_additive_and_does_not_overwrite(tmp_path):
    p=_make(tmp_path)
    target=tmp_path/"audit"
    export(p,target)
    assert (target/"GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json").is_file()
    assert (target/"SOURCE_SUPPORT_DOF_VS_PRIMARY32.csv").is_file()
    assert (target/"ETABS_END_ZONE_STIFFNESS_REVIEW.csv").is_file()
    with pytest.raises(FileExistsError):
        export(p,target)
    assert json.loads((p/"OpenSees_Complete_Model_Data_V118.json").read_text())["supports"]["718"]==[1]*6


def test_rejects_stale_or_wrong_primary_mapping(tmp_path):
    p=_make(tmp_path)
    wrong=tmp_path/"wrong.json"
    wrong.write_text(json.dumps({"mode":"ETABS_NONZERO_REACTION_DIAGNOSTIC",
                                  "mapping":[{"selected":True,"opensees_node":1}]}))
    with pytest.raises(ValueError,match="does not match"):
        assess(p,primary_audit=wrong)
