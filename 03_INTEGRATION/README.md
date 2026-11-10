# 03 — ETABS ↔ OpenSees integration

This is an **adapter and comparison layer**, not a second numerical solver.

Existing authoritative paths: `components/model/assembly.py` (source-to-model conversion), `components/gravity/` (32-primary versus 76/97-mesh support checks), `components/equivalent_static/` (original workbook-based Aw/T1 and ESM), `components/validation/` (saved native CSI/ETABS evidence), `tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py` (guarded source regeneration).

The native model, workbook, model configuration and output must all match by source identity before comparing gravity, modal, ESM, RSA, PDelta or NLTHA. A prior gross beam-weight mismatch of approximately 8,652.444 kN is not deemed fixed until the **new** corrected model is solved and compared to original ETABS supports.

[Source and physics gates](../engineering/topics/INTEGRATION.md) · [exact source acceptance](../engineering/rules/ENGINEERING_GATES.md)
