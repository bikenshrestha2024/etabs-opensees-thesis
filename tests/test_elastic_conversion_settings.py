import pytest

from components.model.elastic_conversion_settings import compile_settings


def _frame(start=0., end=3.):
    return dict(object="7", category="BEAM", start=start, end=end, length=end-start,
                basis=((1.,0.,0.),(0.,1.,0.),(0.,0.,1.)), properties={
                    "section":"B", "A":.3, "J":.01, "Iy":.02, "Iz":.03,
                    "E":25e6, "G":10e6, "As2":.23, "As3":.25})


def test_absolute_factors_then_object_priority_and_end_zone():
    config={"ULS":{"frame_sections":{"B":{"A":.5,"I22":.4}},
                   "frame_objects":{"7":{"I22":.6}},
                   "end_offsets_m":{"7":{"i":.5,"j":.3,"rigid_fraction":.5}}}}
    first, last=_frame(), _frame(3.,6.)
    result=compile_settings(config,[first,last],[],{})
    i,j=result["ULS"]["frame_segments"]
    assert i["joint_offsets_m"]==pytest.approx([.25,0,0,0,0,0])
    assert j["joint_offsets_m"]==pytest.approx([0,0,0,-.15,0,0])
    assert i["properties"]["A"]==pytest.approx(.3*.5*2.75/3)
    assert i["properties"]["Iy"]==pytest.approx(.02*.6)
    assert i["properties"]["Iz"]==pytest.approx(.03*.35)
    assert first["properties"]["A"]==.3


def test_invalid_offset_and_unknown_id_are_rejected():
    with pytest.raises(ValueError,match="outer segment"):
        compile_settings({"ULS":{"end_offsets_m":{"7":{"i":3.1,"j":0,"rigid_fraction":1}}}},
                         [_frame(),_frame(3.,6.)],[],{})
    with pytest.raises(ValueError,match="999"):
        compile_settings({"ULS":{"frame_objects":{"999":{"I22":.5}}}},[_frame()],[],{})


def test_native_section_and_object_multiply_and_shear_is_opt_in():
    raw={"A":1,"As2":1,"As3":1,"J":1,"I22":1,"I33":1,"mass":1,"weight":1}
    source={"etabs_property_modifiers":{"records":[{
        "kind":"frame","object":"7","section":"B",
        "section_modifiers":{**raw,"I22":.5},"object_modifiers":{**raw,"I22":.75}}]}}
    config={"ULS":{"use_native_frame_modifiers":True,"shear_flexible_sections":["B"]}}
    plan=compile_settings(config,[_frame()],[],source)["ULS"]["frame_segments"][0]
    assert plan["properties"]["Iy"]==pytest.approx(.02*.5*.75)
    assert plan["properties"]["As2"]==.23


def test_shell_objects_have_independent_effective_stiffness_and_source_thickness():
    p={"property":"W", "E":25e6, "nu":.2, "thickness":.6}
    shells=[dict(object=obj, category="SHEAR WALL", properties=p) for obj in ("1","2")]
    config={"ULS":{
        "shell_sections":{"W":dict.fromkeys(("f11","f22","f12"),.5)},
        "shell_objects":{"2":dict.fromkeys(("f11","f22","f12"),.8)}}}
    plan=compile_settings(config,[],shells,{})["ULS"]["shell_objects"]
    assert plan["1"]["E_membrane_kN_m2"]==12.5e6
    assert plan["2"]["E_membrane_kN_m2"]==20e6
    assert plan["1"]["physical_thickness_m"]==plan["2"]["physical_thickness_m"]==.6
    assert p["E"]==25e6
def test_read_comparison_settings_rejects_timing_and_empty_states(tmp_path):
    from components.model.elastic_conversion_settings import read_comparison_settings
    import pytest

    sidecar = tmp_path/'elastic_conversion_settings.py.processing.json'
    sidecar.write_text('{"stage":"conversion"}',encoding='utf-8')
    with pytest.raises(ValueError,match='sidecars'):
        read_comparison_settings(sidecar)
    settings=tmp_path/'elastic.json'
    settings.write_text('{"ULS":{}}',encoding='utf-8')
    with pytest.raises(ValueError,match='empty'):
        read_comparison_settings(settings)
    settings.write_text('{"ULS":{"use_native_frame_modifiers":true}}',encoding='utf-8')
    assert read_comparison_settings(settings) == {'ULS':{'use_native_frame_modifiers':True}}


def test_layered_wall_candidate_is_explicit_and_native_only():
    p={"property":"W","E":25e6,"nu":.2,"thickness":.6}
    wall=dict(object="1",category="SHEAR WALL",properties=p)
    values=dict(f11=.5,f22=.5,f12=.5,m11=.1,m22=.1,m12=.1,
                v13=1.,v23=1.,mass=1.,weight=1.)
    metadata={"etabs_property_modifiers":{"records":[{
        "kind":"area","object":"1","section":"W",
        "section_modifiers":values,"object_modifiers":dict.fromkeys(values,1.)}]}}
    options={"use_native_shell_modifiers":True,"layered_shell_sections":{"W":1.}}
    plan=compile_settings({"ULS":options},[],[wall],metadata)["ULS"]["shell_objects"]["1"]
    assert plan["status"]=="ELASTIC_COMPONENT_CANDIDATE_NOT_ETABS_EQUIVALENCE"
    assert plan["physical_thickness_m"]==.6
    assert not plan["transverse_shear_exact"]
    assert plan["layer_factors"]==pytest.approx([.1125,1.275,.1125])
    for bad in ({**options,"use_native_shell_modifiers":False},
                {**options,"layered_shell_sections":{"W":True}},
                {**options,"shell_objects":{"1":{"f11":.8}}},
                {**options,"shell_sections":{"W":{"f11":.8}}}):
        with pytest.raises(ValueError):
            compile_settings({"ULS":bad},[],[wall],metadata)
    with pytest.raises(ValueError,match="wall-only"):
        compile_settings({"ULS":options},[],[{**wall,"category":"FLOOR"}],metadata)
    with pytest.raises(ValueError,match="Incomplete native"):
        compile_settings({"ULS":options},[],[wall],{})


def test_force_based_rigid_zone_uses_source_offsets_and_keeps_shear_area():
    from components.model.elastic_conversion_settings import elastic_offset_force_beam
    vals=dict(A=1.,J=1.,I22=.35,I33=.35,As2=1.,As3=1.,mass=1.,weight=1.)
    native={"frames":{"7":{"GetEndLengthOffset":[True,.5,.3,1.,0]}},
            "etabs_property_modifiers":{"records":[dict(kind="frame",object="7",section="B",
                section_modifiers=vals,object_modifiers=dict.fromkeys(vals,1.))]}}
    options=dict(use_native_frame_modifiers=True,shear_flexible_sections=["B"],
                 force_based_rigid_zone_sections=["B"])
    f=_frame()
    plan=compile_settings({"ULS":options},[f],[],native)["ULS"]
    row=plan["frame_segments"][0]
    assert row["frame_formulation"]=="ELASTIC_FORCE_BASED_RIGID_ZONE_CANDIDATE"
    assert row["joint_offsets_m"]==pytest.approx([.5,0,0,-.3,0,0])
    assert row["properties"]["A"]==pytest.approx(.3*2.2/3)
    assert row["properties"]["As2"]==.23
    assert plan["native_end_offset_coverage"]["native_offsets_configured_exact_count"]==1
    assert "end_offsets_m" not in options
    class Ops:
        def __init__(self): self.calls=[]
        def section(self,*a): self.calls.append(a)
        def beamIntegration(self,*a): self.calls.append(a)
        def element(self,*a): self.calls.append(a)
    ops=Ops(); q=row["properties"]
    elastic_offset_force_beam(ops,1,[1,2],25e6,10e6,q,1)
    assert ops.calls[0][-2:]==pytest.approx([.23/q["A"],.25/q["A"]])
    assert ops.calls[1]==("Lobatto",2000001,2000001,3)
    assert ops.calls[2][:6]==("forceBeamColumn",1,1,2,1,2000001)
    for bad in ({**options,"use_native_frame_modifiers":False},
                {**options,"shear_flexible_sections":[]},
                {**options,"end_offsets_m":{"7":{"i":0.,"j":.3,"rigid_fraction":1.}}}):
        with pytest.raises(ValueError):
            compile_settings({"ULS":bad},[f],[],native)
    with pytest.raises(ValueError,match="missing native end offset"):
        compile_settings({"ULS":options},[f],[],{**native,"frames":{}})
