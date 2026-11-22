"""Source-grounded NBC 105:2025 Clause 1–10 entrypoint; no solver side effects.

[REF NBC105-2025 Clauses 1–10; docs/nbc105/README.md]
Call exported pure-Python rule functions by their canonical clause. This facade
makes individual clauses available to the production GUI/Excel adapter and CLI;
it cannot approve building models, material design or native solver evidence.
"""
from __future__ import annotations

import dataclasses
import importlib
import inspect
import math

_MODULES={
 1:"clause_01_scope_definitions",
 2:"clause_02_general_principles",
 3:"clause_03_scope_of_analysis",
 4:"clause_04_seismic_hazard",
 5:"clause_05_dynamic_characteristics",
 6:"clause_06_equivalent_static",
 7:"clause_07_modal_response_spectrum",
 8:"clause_08_elastic_time_history",
 9:"clause_09_nonlinear_analysis",
 10:"clause_10_parts_and_components",
}
_STATUS="CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE"

def _load(number):
    if type(number) is not int or number not in _MODULES:
        raise ValueError("NBC 105 clause must be an integer 1..10")
    return importlib.import_module("components.nbc105."+_MODULES[number])

def _operations(number):
    module=_load(number)
    return {name:fn for name in getattr(module,"__all__",())
            if isinstance(name,str) and not name.startswith("_")
            and inspect.isfunction(fn:=getattr(module,name,None))
            and fn.__module__==module.__name__}

def available_operations():
    """Public, explicit rule entrypoints by exact clause.

    [REF NBC105-2025 Clauses 1–10; docs/nbc105/README.md]
    """
    return {number:sorted(_operations(number)) for number in _MODULES}

def _json_primitive(value):
    if dataclasses.is_dataclass(value) and not isinstance(value,type):
        return _json_primitive(dataclasses.asdict(value))
    if isinstance(value,dict):
        return {str(k):_json_primitive(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):
        return [_json_primitive(v) for v in value]
    if value is None or isinstance(value,(str,bool,int)):
        return value
    if isinstance(value,float):
        if not math.isfinite(value):
            raise ValueError("NBC calculation produced a nonfinite result")
        return value
    raise ValueError("NBC calculation returned an unsupported result type")


def _operation_signature(fn):
    """Return an explicit JSON-input contract for one public code rule.

    This exposes named required fields without guessing engineering values.
    It does NOT validate the source standard or the selected structural model.
    """
    signature=inspect.signature(fn)
    fields=[]
    for param in signature.parameters.values():
        if param.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                              inspect.Parameter.KEYWORD_ONLY):
            raise ValueError("NBC function uses unsupported non-keyword JSON inputs")
        required=param.default is inspect.Parameter.empty
        default=None if required else _json_primitive(param.default)
        fields.append({"name":param.name,"required":required,
                       "default":default,
                       "annotation":str(param.annotation) if
                       param.annotation is not inspect.Parameter.empty else "",
                       "description":""})
    return {"parameters":fields,
            "required":[p["name"] for p in fields if p["required"]],
            "optional":[p["name"] for p in fields if not p["required"]],
            "template":{p["name"]:p["default"] for p in fields},
            "note":"Replace null required fields using independently verified project inputs; defaults are source-code defaults, not project verification."}


def operation_input_spec(clause, operation):
    """Describe the exact public Clause 1–10 operation arguments."""
    operations=_operations(clause)
    if operation not in operations:
        raise ValueError("Unsupported NBC clause operation")
    return _operation_signature(operations[operation])


def annex_operation_input_spec(annex, operation):
    """Describe the exact public Annex A/B operation arguments."""
    if annex not in _ANNEX_MODULES:
        raise ValueError("Only Annex A/B are implemented as callable rule modules")
    module=importlib.import_module("components.nbc105."+_ANNEX_MODULES[annex])
    if operation not in available_annex_operations()[annex]:
        raise ValueError("Unsupported NBC annex operation")
    return _operation_signature(getattr(module,operation))


def _execute_named_rule(fn, inputs, *, label):
    """Bind arguments before calling; never disguise an internal TypeError."""
    if not isinstance(inputs,dict) or any(not isinstance(k,str) for k in inputs):
        raise ValueError(label+" inputs must be a JSON object of named parameters")
    signature=inspect.signature(fn)
    try:
        bound=signature.bind(**inputs)
    except TypeError as exc:
        raise ValueError(label+" input error: "+str(exc)) from exc
    missing_null=[name for name,value in bound.arguments.items() if value is None
                  and signature.parameters[name].default is inspect.Parameter.empty]
    if missing_null:
        raise ValueError(label+" requires project values for: "+", ".join(missing_null))
    return fn(**inputs)

def run_operation(clause,operation,inputs):
    """Execute only an explicitly exported Clause 1–10 rule with JSON inputs.

    [REF NBC105-2025 Clauses 1–10; docs/nbc105/README.md]
    The return status never certifies an ETABS/OpenSees model.
    """
    operations=_operations(clause)
    if not isinstance(operation,str) or operation not in operations:
        raise ValueError("Unsupported NBC clause operation")
    value=_execute_named_rule(operations[operation],inputs,
                              label="NBC clause "+str(clause)+" / "+operation)
    return {"standard":"NBC 105:2025","source_clause":str(clause),
            "clause":clause,"operation":operation,"status":_STATUS,
            "result":_json_primitive(value)}

# Reference checks for mandatory Annexes are separate from main clause modules.
# Annex C is a large source zoning dataset; it is NOT implemented/approved here.
_ANNEX_MODULES={
    "A":"annex_a_rc_detailing",
    "B":"annex_b_steel_detailing",
}

def available_annex_operations():
    """List source-based Annex A/B reference calculations, never design approval.

    [REF NBC105-2025 Annex A §§5.1–5.5 and Annex B §§7.1–7.1.4]
    """
    result={}
    for annex,slug in _ANNEX_MODULES.items():
        module=importlib.import_module("components.nbc105."+slug)
        result[annex]=sorted(name for name in getattr(module,"__all__",())
                             if inspect.isfunction(fn:=getattr(module,name,None))
                             and fn.__module__==module.__name__)
    return result

def run_annex_operation(annex,operation,inputs):
    """Evaluate an explicitly exported Annex A/B function without certification.

    [REF NBC105-2025 Annexes A and B; docs/nbc105/README.md]
    """
    if annex not in _ANNEX_MODULES:
        raise ValueError("Only source-referenced Annex A or Annex B operations supported")
    module=importlib.import_module("components.nbc105."+_ANNEX_MODULES[annex])
    allowed=available_annex_operations()[annex]
    if operation not in allowed:
        raise ValueError("Unsupported or private NBC annex operation")
    value=_execute_named_rule(getattr(module,operation),inputs,
                              label="NBC annex "+annex+" / "+operation)
    return {"standard":"NBC 105:2025","annex":annex,"operation":operation,
            "status":_STATUS,"result":_json_primitive(value),
            "warning":"Preliminary rule evaluation; connection/strength and native model acceptance remain open"}
