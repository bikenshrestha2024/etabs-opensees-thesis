"""Readiness selection must not prefer an unbound V116 template to a valid V134 draft."""
import json
from pathlib import Path
from types import SimpleNamespace
from components.model.readiness import bind_readiness_draft, select_model_bound_readiness
from components.model.assembly import autoselect_inputs

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "OpenSees_Model_Readiness_Template_V116.json"


class Variable:
    def __init__(self, value=""): self.value = value
    def get(self): return self.value
    def set(self, value): self.value = value


def project(root):
    root.mkdir(exist_ok=True)
    model = root / "OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("# synthetic nonlinear model", encoding="utf-8")
    template = root / "OpenSees_Model_Readiness_V116.json"
    template.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    (root / "OpenSees_Export_Manifest_V118.json").write_text(json.dumps({
        "nonlinear_model_script": model.name,
        "readiness_manifest": template.name,
    }), encoding="utf-8")
    return model,template


def auto(root, old_readiness=""):
    gui=SimpleNamespace(model=Variable(),readiness=Variable(old_readiness),
                        output=Variable(),ls=Variable("ULS"))
    assert autoselect_inputs(gui,root,"nonlinear_model_script")
    return gui


def test_draft_wins_over_unbound_v116_template(tmp_path):
    model,template = project(tmp_path)
    draft = bind_readiness_draft(TEMPLATE,model)
    assert auto(tmp_path).readiness.get() == str(draft)
    assert select_model_bound_readiness(model,[template,draft]) == draft
    assert json.loads(template.read_text())["approved_for_nltha"] is False


def test_no_bound_draft_leaves_readiness_empty_instead_of_template(tmp_path):
    model,template=project(tmp_path)
    gui=auto(tmp_path)
    assert gui.model.get()==str(model)
    assert gui.readiness.get()==""
    assert select_model_bound_readiness(model,[template]) is None


def test_switching_projects_clears_stale_model_binding(tmp_path):
    a=tmp_path/"a";b=tmp_path/"b"
    model_a, _=project(a); model_b, _=project(b)
    draft_a=bind_readiness_draft(TEMPLATE,model_a)
    gui=auto(b,str(draft_a))
    assert gui.model.get()==str(model_b)
    assert gui.readiness.get()==""
    draft_b=bind_readiness_draft(TEMPLATE,model_b)
    assert auto(b,str(draft_a)).readiness.get()==str(draft_b)


def test_draft_with_changed_script_sha_is_not_silently_accepted(tmp_path):
    model,_=project(tmp_path)
    draft=bind_readiness_draft(TEMPLATE,model)
    model.write_text("# model modified",encoding="utf-8")
    assert auto(tmp_path).readiness.get()==""
    assert select_model_bound_readiness(model,[draft]) is None
    assert json.loads(draft.read_text())["model_script_sha256"] != ""


def test_approved_model_specific_manifest_can_be_selected_without_mutation(tmp_path):
    model,template=project(tmp_path)
    from components.model.readiness import record_binding,READINESS_CHECK_KEYS
    import hashlib
    data={"model_script":str(model),"model_script_sha256":hashlib.sha256(model.read_bytes()).hexdigest(),
          "approved_for_nltha":True,"checks":dict.fromkeys(READINESS_CHECK_KEYS,True)}
    record_binding(data,model)
    template.write_text(json.dumps(data),encoding="utf-8")
    original=template.read_bytes()
    assert select_model_bound_readiness(model,[template])==template
    assert auto(tmp_path).readiness.get()==str(template)
    assert template.read_bytes()==original
