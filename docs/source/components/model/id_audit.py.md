# id_audit.py — source documentation

**Python source:** [components/model/id_audit.py](../../../../components/model/id_audit.py)
**Git baseline content SHA:** 8ecacd10fbd4cff624a9ea95b793697039e85ba4
**Subsystem:** ETABS geometry/mass/constraint and model assembly
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the model implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R02 R10 R12. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-15 new source-linked element role columns

`export_id_audit` uses `components.model.display_ids.member_identity` to write additive `Main family`, `Brace role` and `Display prefix` columns to the original `Elements` worksheet and the exact-ID HTML lookup. Existing column indexes 0–9 are unchanged: original ETABS object, original category, story, source property, topology and solver tags remain available. An additional `OpenSees_Brace_Role_Review.csv` lists each source frame with BR-family membership, its current source/proposed role and evidence-review state.

To assign an **explicit source-verified role**, add to the *working copied* `OpenSees_Complete_Model_Config_V118.json`:

```json
{"display_member_roles": {
  "REVIEWED_ETABS_UNIQUE_ID": "CO",
  "ANOTHER_REVIEWED_ETABS_UNIQUE_ID": "BT"
}}
```

These are illustrative keys; do not paste them as real IDs. Only the source unique ID namespace is allowed, **never** OpenSees preview/assembled tags. For CT, first verify the member belongs to the cap-truss assembly at the 25th storey. A chosen role changes labels/lookup only and is not constitutive-model evidence. Unknown IDs, invalid roles and contradictory explicitly typed categories fail before writing an output. Source drawings/ETABS group proof and independent FVD/BRB assignments remain separate gates. Existing source EDB is never touched.
