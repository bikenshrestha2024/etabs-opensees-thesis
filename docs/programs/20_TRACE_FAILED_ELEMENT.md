# 20 — Trace failed solver element

**Current launcher:** [`20_TRACE_FAILED_ELEMENT.py`](../../20_TRACE_FAILED_ELEMENT.py)  
**Previous launcher:** [`21_TRACE_FAILED_ELEMENT.py`](../../21_TRACE_FAILED_ELEMENT.py) (compatibility alias)

## Goal
Trace a reported solver tag to its source object and its frame segment or mesh cell using the isolated model from the failed run.

## Input checklist
Confirm the current export folder, validated geometry and section mapping, gravity and mass data, analysis units, selected material cards, and output destination as applicable to this subprogram. Do not mix old saved V156 exports with source modules from the new checkout.

## Execution
```powershell
python 20_TRACE_FAILED_ELEMENT.py "<failed run or isolated_model folder>" --tag 110280
```

The trace writes `Failed_Element_110280_Trace.json` by default. When the saved element map is present, the tag must appear in it. The trace uses the ordered tags for a source object to select the matching serialized segment. If the two sources disagree on the segment count or order, the report identifies the mapped object and marks its geometry unavailable. If the map is absent, the trace reports when it inferred a candidate from the serialized tag range.

## Validation and results
Use the map and model data from the same failed run. A trace identifies the recorded solver tag. Establish whether the element initiated the failure using the accepted pre-failure state and independent probe evidence.

[Complete run order](00_PROGRAM_INDEX.md) · [Modeling basis](../../Research_Components/02_MODELLING_BASIS.md)
