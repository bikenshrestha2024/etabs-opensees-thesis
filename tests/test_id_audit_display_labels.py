"""Display labels are additive, preserving ETABS IDs and actual solver tags."""
import json
from openpyxl import load_workbook
from components.model.id_audit import export_id_audit


def test_labels_in_excel_and_html(tmp_path):
    topology={
        "node_map":[
            {"etabs_point_name":"BASE-A","opensees_node_tag":4,
             "etabs_storey_number":0,"coordinates_m":[0,0,0]},
            {"etabs_point_name":"L1-A","opensees_node_tag":104,
             "etabs_storey_number":1,"coordinates_m":[0,0,3.6]}],
        "elements":[
            {"etabs_object":"251","dimension":"line_2_node","category":"BEAM",
             "storey_number":1,"assigned_section":"Beam 600*800",
             "element_tag":1001,"node_names":["BASE-A","L1-A"],"node_tags":[4,104]}]}
    (tmp_path/"OpenSees_Element_Connectivity.json").write_text(json.dumps(topology))
    export_id_audit(tmp_path)
    wb=load_workbook(tmp_path/"OpenSees_ID_and_Support_Audit.xlsx",read_only=True)
    nodes=list(wb["Nodes"].values)
    elements=list(wb["Elements"].values)
    assert nodes[1][-1]=="N1"
    assert nodes[2][-1]=="N101"
    assert elements[1][0]=="251"
    assert elements[1][5]==1001
    assert elements[1][-1]=="B101"
    html=(tmp_path/"OpenSees_ID_Lookup.html").read_text()
    assert "B101" in html and "251" in html
