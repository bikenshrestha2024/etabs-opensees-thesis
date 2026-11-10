"""Thin discoverable ETABS-only adapter to existing canonical code.

No model mathematics or native data reconstruction here. Lazy imports avoid
starting ETABS/COM for documentation or standalone OpenSees users.
Native API extraction is strictly read-only unless called by a separate
explicitly authorized ETABS working-copy execution tool.
"""
from __future__ import annotations
from importlib import import_module

_ADAPTERS={
    "native_quantity":(
        "components.validation.etabs_native_quantity_tables",
        "export_native_quantity_tables"),
    "eq_pdelta":(
        "components.validation.etabs_eq_pdelta_native_extract",
        "export_eq_pdelta_native_evidence"),
    "project_workbook":(
        "components.inputs.project_workbooks",
        "source_limit_state"),
}

def existing_adapter(name):
    """Find existing implementation rather than creating a second one."""
    if name not in _ADAPTERS:
        raise ValueError("Unknown ETABS adapter: "+str(name)+
                         "; choose "+", ".join(sorted(_ADAPTERS)))
    module,symbol=_ADAPTERS[name]
    fn=getattr(import_module(module),symbol,None)
    if not callable(fn):
        raise RuntimeError("Existing ETABS adapter not callable: "+module+"."+symbol)
    return fn

def available_existing_adapters():
    """Return symbolic import paths without importing ETABS/COM or the source."""
    return {name:module+"."+symbol for name,(module,symbol) in _ADAPTERS.items()}
