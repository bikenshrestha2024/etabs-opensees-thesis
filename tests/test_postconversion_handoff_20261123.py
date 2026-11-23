"""Post-conversion current-source ID integrity and on-demand audit regressions.

Source evidence: 2026-11-23 uploaded V125 workbook (2092 source records,
55 unassigned storey-0 beams with empty solver tag list). Fixtures synthetic;
no native ETABS COM or solver pass implied.
"""
import inspect
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from components.model.id_audit import export_id_audit
from components.sections.mapping_audit import collect, save_assignment, summarize_assembly_warnings
from components.sections import mapping_gui


def _fixture(root):
    nodes=[
        dict(etabs_point_name=str(50+i),opensees_node_tag=i,
             coordinates_m=[float(i),0.,0.],etabs_storey_number=0)
        for i in range(1,5)
    ]
    topology=dict(
        source_edb="private-current.EDB",
        node_map=nodes,
        elements=[
            dict(etabs_object="1",dimension="line_2_node",category="BEAM",
                 storey_number=1,assigned_section="Beam 600*800",
                 element_tag=101,node_tags=[1,2],node_names=["51","52"]),
            dict(etabs_object="1",dimension="area_polygon",category="FLOOR",
                 storey_number=1,assigned_property="Slab 150",
                 element_tag=201,node_tags=[1,2,3,4],
                 node_names=["51","52","53","54"]),
            dict(etabs_object="55",dimension="line_2_node",category="BEAM",
                 storey_number=0,assigned_section="UNASSIGNED",
                 element_tag=55,node_tags=[3,4],node_names=["53","54"]),
        ])
    payload={
        "frames":[dict(object="1",nodes=[1,2],category="BEAM",
                       properties={"section":"Beam 600*800","E":1000.})],
        "shells":[dict(object="1",nodes=[1,2,3,4],category="FLOOR",
                       properties={"property":"Slab 150","thickness":0.15})],
        "nodes":{str(i):n["coordinates_m"] for i,n in enumerate(nodes,1)},
    }
    (root/"OpenSees_Element_Connectivity.json").write_text(json.dumps(topology),encoding="utf-8")
    (root/"OpenSees_Complete_Model_Data_V118.json").write_text(json.dumps(payload),encoding="utf-8")
    (root/"OpenSees_Complete_Export_Report_V118.json").write_text(
        json.dumps({"elastic_assembled":True,"assembly_errors":[]}),encoding="utf-8")
    (root/"OpenSees_Complete_Model_Config_V118.json").write_text("{}",encoding="utf-8")
    (root/"OpenSees_Source_Model_Metadata_V118.json").write_text(
        json.dumps({"supports":{}}),encoding="utf-8")
    return root


def test_area_and_frame_ids_never_share_assembled_solver_tags():
    from openpyxl import load_workbook
    with tempfile.TemporaryDirectory() as td:
        folder=_fixture(Path(td))
        export_id_audit(folder,payload=json.loads(
            (folder/"OpenSees_Complete_Model_Data_V118.json").read_text()))
        with (folder/"OpenSees_ID_and_Support_Audit.xlsx").open("rb") as stream:
            book=load_workbook(stream,read_only=True,data_only=True)
            try:
                rows=list(book["Elements"].values)
            finally:
                book.close()
        values={(r[0],r[1]):r[8] for r in rows[1:]}
        assert values[("1","line_2_node")]=="[100001]"
        assert values[("1","area_polygon")]=="[100002]"
        assert values[("55","line_2_node")]=="[]"


def test_current_export_explicitly_distinguishes_source_only_and_solver_elements():
    with tempfile.TemporaryDirectory() as td:
        folder=_fixture(Path(td))
        out=collect(folder)
        bykey={x["key"]:x for x in out["elements"]}
        assert bykey["FRAME:1"]["assembly_status"]=="ASSEMBLED_SOLVER_ELEMENT"
        assert bykey["AREA:1"]["assembly_status"]=="ASSEMBLED_SOLVER_ELEMENT"
        assert bykey["FRAME:55"]["assembly_status"]=="SOURCE_TOPOLOGY_ONLY_NO_SOLVER_ELEMENT"
        assert bykey["FRAME:55"]["target"]=="KEEP_SOURCE_ELASTIC"
        assert bykey["FRAME:55"]["solver_tags"]==[]
        assert len(out["solver_elements"])==2


def test_reload_does_not_regenerate_or_open_massive_excel_audit():
    class State:
        value=None
        def set(self,value):self.value=value
    with tempfile.TemporaryDirectory() as td:
        folder=_fixture(Path(td))
        active=State();status=State();calls=[]
        fake=SimpleNamespace(
            folder=folder,active=active,status=status,
            populate=lambda:calls.append("populate"),
            draw_source=lambda:calls.append("draw"),
            highlight_keys=lambda keys:calls.append(("highlight",keys)),
            highlight_inline_id=lambda:calls.append("auto_highlight"))
        with patch.object(mapping_gui,"export_excel",side_effect=AssertionError(
                "expensive workbook must be user-requested")):
            mapping_gui.MappingGUI.reload(fake)
        assert calls==["populate","draw",("highlight",[])]
        assert "on demand" in (status.value or "").lower()
        assert not (folder/"OpenSees_Property_Element_Load_Audit_V125.xlsx").exists()


def test_load_audit_popup_does_not_export_excel_without_button_click():
    source=inspect.getsource(mapping_gui.show_load_audit)
    assert "\n    export_excel(folder)\n" not in source
    ui=inspect.getsource(mapping_gui.MappingGUI.__init__)
    assert "self.id_value=tk.StringVar(value='')" in ui


def test_research_override_cannot_target_source_only_unassembled_member():
    with tempfile.TemporaryDirectory() as td:
        folder=_fixture(Path(td))
        try:
            save_assignment(folder,["FRAME:55"],"RC_BEAM_600x800_FIBER")
        except ValueError as exc:
            assert "not assembled" in str(exc).lower()
        else:
            raise AssertionError("A source-only unassigned frame cannot be an active solver material mapping")


def test_warning_digest_keeps_raw_id_specific_diagnostics_in_source():
    warnings=[
        "SOURCE_ONLY wall supports: mesh transfer not verified.",
        "ETABS frame unique ID 1308 | OpenSees topology tag 25049 | OpenSees elastic element tags [103751]: assembled with source My/Mz end releases and zero torsional transfer.",
        "ETABS frame unique ID 1309 | OpenSees topology tag 25050 | OpenSees elastic element tags [103752]: assembled with source My/Mz end releases and zero torsional transfer.",
    ]
    digest=summarize_assembly_warnings(warnings)
    assert len(digest)==2
    assert any("2 frame" in line and "1308" in line and "1309" in line for line in digest)
    assert any("mesh transfer" in line for line in digest)
    assert len(warnings)==3


def test_3d_plotly_handoff_has_dimension_even_for_same_numeric_id():
    from components.sections.mapping_gui import plotly_query_for_key
    with tempfile.TemporaryDirectory() as td:
        data=collect(_fixture(Path(td)))
        assert plotly_query_for_key("FRAME:1",data)=={
            "idKind":"object","idValue":"1","category":"frame"}
        assert plotly_query_for_key("AREA:1",data)=={
            "idKind":"object","idValue":"1","category":"area"}
        assert plotly_query_for_key("SOLVER:100002",data)=={
            "idKind":"solver","idValue":"100002","category":"area"}
        assert plotly_query_for_key("SOLVER:100001",data)=={
            "idKind":"solver","idValue":"100001","category":"frame"}
