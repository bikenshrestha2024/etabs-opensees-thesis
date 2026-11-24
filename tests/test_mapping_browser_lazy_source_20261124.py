"""Mapping V126 source-only GUI regression, no Tk window or private model used.

Synthetic 300-object column group with 1,200 solver segments emulates the
V126 browser's eager 2,092-object/14,262-element workload.
[REF docs/source/components/sections/mapping_gui.py.md]
"""
import types
from unittest.mock import patch

from components.sections import mapping_gui


class Field:
    def __init__(self,value=None):self.value=value
    def get(self):return self.value
    def set(self,value):self.value=value


class Tree:
    def __init__(self,fail_after=None):
        self.records={}
        self.children={"":[]}
        self.last=0
        self.current=None
        self.fail_after=fail_after

    def insert(self,parent,index,text="",values=(),open=False):
        self.last+=1
        if self.fail_after is not None and self.last>self.fail_after:
            raise RuntimeError("SYNTHETIC_TREE_RENDER_FAILURE")
        iid=str(self.last)
        self.records[iid]={"text":text,"values":values,"open":open}
        self.children.setdefault(parent,[]).append(iid)
        self.children.setdefault(iid,[])
        return iid

    def get_children(self,parent=""):
        return tuple(self.children.get(parent,[]))

    def delete(self,*iids):
        for iid in iids:
            for child in tuple(self.children.get(iid,[])):
                self.delete(child)
            for children in self.children.values():
                if iid in children:children.remove(iid)
            self.records.pop(iid,None)
            self.children.pop(iid,None)

    def focus(self):
        return self.current


def sample_data(count=300):
    elements=[]
    solver=[]
    for i in range(1,count+1):
        tags=list(range(i*10,i*10+4))
        source=f"FRAME:{i}"
        elements.append(dict(
            key=source,category="COLUMN",property="Col 1100*1100",
            etabs_object=str(i),display_label="C"+str(i),
            topology_tag=10000+i,solver_tags=tags,
            node_tags=[i,i+1],storey=11,target="KEEP_SOURCE_ELASTIC",
            assembly_status="ASSEMBLED_SOLVER_ELEMENT"))
        for tag in tags:
            solver.append(dict(key=source,solver_tag=tag,node_tags=[i,i+1]))
    return dict(elements=elements,solver_elements=solver,
        properties=[dict(group="COLUMN / Col 1100*1100",
                         property="Col 1100*1100",category="COLUMN",
                         count=count,material="M45")],
        selections={"active":False,"assignments":{}},nodes=[])


def fake_gui(data, fail_after=None):
    self=types.SimpleNamespace(
        data=data,tree=Tree(fail_after),
        category=Field("All"),search=Field(""),
        item_keys={},record_items={},status=Field(),
        load_banner=Field())
    return self


def test_lazy_property_groups_and_source_segments_load_only_when_expanded():
    self=fake_gui(sample_data())
    mapping_gui.MappingGUI.populate(self)
    roots=self.tree.get_children()
    assert len(roots)==1
    group=roots[0]
    assert len(self.tree.records)==2, "Initially render only a property + expander"
    assert len(self.item_keys[group])==300
    assert len(self.tree.get_children(group))==1
    self.tree.current=group
    mapping_gui.MappingGUI.expand_tree_node(self)
    objects=self.tree.get_children(group)
    assert len(objects)==300
    assert len(self.tree.records)<800, "1,200 solver rows must not render yet"
    first=objects[0]
    assert self.item_keys[first]==["FRAME:1"]
    assert len(self.tree.get_children(first))==1
    self.tree.current=first
    mapping_gui.MappingGUI.expand_tree_node(self)
    children=self.tree.get_children(first)
    assert len(children)==4
    assert self.item_keys[children[0]]==["SOLVER:10"]
    # Repeated open/close events may not duplicate solver mappings.
    before=len(self.tree.records)
    mapping_gui.MappingGUI.expand_tree_node(self)
    assert len(self.tree.records)==before
    assert len(self.tree.get_children(first))==4


def test_failed_property_population_clears_partial_tree_and_still_draws_geometry():
    data=sample_data()
    self=fake_gui(data,fail_after=1)
    self.folder="synthetic_case"
    self.active=Field()
    calls=[]
    self.populate=lambda: mapping_gui.MappingGUI.populate(self)
    self.draw_source=lambda: calls.append("geometry_draw")
    self.highlight_keys=lambda keys:calls.append(("highlight",keys))
    with patch.object(mapping_gui,"collect",return_value=data):
        mapping_gui.MappingGUI.reload(self)
    assert calls==["geometry_draw",("highlight",[])],calls
    assert not self.tree.get_children(), "Partially inserted group must not look complete"
    assert "incomplete" in self.status.value.lower()
    assert "synthetic_tree_render_failure" in self.load_banner.value.lower()
    assert "300" not in self.status.value, "Never claim all items rendered after failure"


def test_missing_geometry_is_visible_not_default_axis_silence():
    data=sample_data(count=2)
    self=fake_gui(data)
    self.folder="synthetic_case"
    self.active=Field()
    self.populate=lambda:mapping_gui.MappingGUI.populate(self)
    self.draw_source=lambda:(_ for _ in ()).throw(
        ValueError("MISSING_COORDINATES_FOR_SOURCE"))
    self.highlight_keys=lambda keys:None
    with patch.object(mapping_gui,"collect",return_value=data):
        mapping_gui.MappingGUI.reload(self)
    assert "incomplete" in self.status.value.lower()
    assert "missing_coordinates_for_source" in self.load_banner.value.lower()


def test_source_only_object_never_claims_solver_child():
    data=sample_data(count=1)
    row=data["elements"][0]
    row["solver_tags"]=[]
    row["assembly_status"]="SOURCE_TOPOLOGY_ONLY_NO_SOLVER_ELEMENT"
    data["solver_elements"]=[]
    self=fake_gui(data)
    mapping_gui.MappingGUI.populate(self)
    group=self.tree.get_children()[0]
    self.tree.current=group
    mapping_gui.MappingGUI.expand_tree_node(self)
    source=self.tree.get_children(group)[0]
    assert self.item_keys[source]==["FRAME:1"]
    assert self.tree.get_children(source)==()
    assert self.tree.records[source]["values"][-2]=="SOURCE_TOPOLOGY_ONLY_NO_SOLVER_ELEMENT"
