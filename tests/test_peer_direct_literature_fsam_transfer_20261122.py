"""PEER 2015/12 B.3 actual FSAM ratios must replace synthetic D20@200 in the research case.

Numerical source: RW-A15-P10-S78, Appendix B.3 printed pp.90-91;
web FSAM panel 6, boundary panel 7.
No native solver/external user data required.
"""
import json
import tempfile
from pathlib import Path

from components.nonlinear_time_history.material_source_sets import (
    peer_fsam_panel_values, peer_single_source)
from components.nonlinear_time_history.material_draft import prepare


def test_fsam_web_and_boundary_exact_published_parameters():
    panel=peer_fsam_panel_values()
    assert panel["web"]=={"rho_x":0.0074,"rho_y":0.0074,"nu":0.8,"alpha":0.01}
    assert panel["boundary"]=={"rho_x":0.0082,"rho_y":0.0587,"nu":0.8,"alpha":0.01}
    assert "Appendix B.3" in panel["citation"]
    s=peer_single_source()
    rows=[x for x in s["rows"] if x["family"]=="FSAM panel"]
    assert rows and all(x["status"]=="FROM_SOURCE" for x in rows)
    assert all(x["source"].endswith(".pdf") for x in rows)


def test_research_draft_uses_published_web_not_unverified_bar_spacing():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);src=root/"src";src.mkdir()
        sources={
            "OpenSees_Complete_Model_Data_V118.json":{"shells":[
                {"category":"SHEAR WALL","properties":{"property":"X12","thickness":0.6}},
                {"category":"SHEAR WALL","properties":{"property":"Y6","thickness":0.6}}]},
            "OpenSees_Complete_Model_Config_V118.json":{"nonlinear_parameters_reviewed":False},
            "OpenSees_Load_Conversion_Audit.json":{},
            "OpenSees_Source_Model_Metadata_V118.json":{},
        }
        for name,val in sources.items():
            (src/name).write_text(json.dumps(val),encoding="utf-8")
        original={p.name:p.read_bytes() for p in src.iterdir()}
        card=prepare(src,root/"draft",basis="PEER_2015_12_SINGLE_SOURCE")
        assert card["assumed_rho"]=={"X12":0.0074,"Y6":0.0074}
        assert card["reinforcement_assumption"].startswith("Published PEER")
        assert card["source_boundary_fsam"]["rho_y"]==0.0587
        assert card["wall_region_assignment"]=="UNCONFINED_WEB_ONLY"
        assert card["status"].startswith("RESEARCH DRAFT")
        cfg=json.loads((root/"draft"/"OpenSees_Complete_Model_Config_V118.json").read_text())
        assert cfg["nonlinear_parameters_reviewed"] is False
        assert {p.name:p.read_bytes() for p in src.iterdir()}==original


def test_published_rho_is_used_for_research_building_instead_of_wall_bar_layout():
    import inspect
    from components.nonlinear_time_history.research_building_materials import define_building_materials
    source=inspect.getsource(define_building_materials)
    assert "peer_fsam_panel_values" in source
    assert "web" in source
