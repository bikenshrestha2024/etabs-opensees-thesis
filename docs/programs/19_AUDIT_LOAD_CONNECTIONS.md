# 19 — Load-path and connectivity audit

**Current launcher:** [`19_AUDIT_LOAD_CONNECTIONS.py`](../../19_AUDIT_LOAD_CONNECTIONS.py)  
**Previous launcher:** [`20_AUDIT_LOAD_CONNECTIONS.py`](../../20_AUDIT_LOAD_CONNECTIONS.py) (compatibility alias)

## Goal
Inspect direct node sharing and missing node references in an assembled export. This audit reads the serialized model and prints JSON without running OpenSees.

## Input checklist
Confirm the current export folder, validated geometry and section mapping, gravity and mass data, analysis units, selected material cards, and output destination as applicable to this subprogram. Do not mix old saved V156 exports with source modules from the new checkout.

## Execution
Pass the folder containing `OpenSees_Complete_Model_Data_V118.json`.

```powershell
python 19_AUDIT_LOAD_CONNECTIONS.py "<assembled export folder>"
```

## Validation and results
The audit reports shared node IDs. Review ties, diaphragm constraints and other force-transfer mechanisms separately before drawing load-path conclusions.

[Complete run order](00_PROGRAM_INDEX.md) · [Modeling basis](../../Research_Components/02_MODELLING_BASIS.md)
