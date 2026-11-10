# 01 — ETABS-only tasks

**Import boundary:** native CSI ETABS OAPI and Windows COM belong here or in a future `src/etabs_adapter/`. An OpenSees solver module must not import this adapter.

**Existing canonical code (do not duplicate):** `components/inputs/project_workbooks.py` (project workbooks), `components/validation/etabs_native_quantity_tables.py` (ETABS tables), `components/validation/etabs_eq_pdelta_native_extract.py` (EQX/EQY results), `OpenSees_Project_Inputs_V123.py` (compatibility facade), `tools/ETABS_EQX_EQY_PDELTA_EXPORT.py` (read-only saved evidence). The ETABS conversion portion of `components/model/assembly.py` is *mixed responsibility*, not yet moved.

**Workflow:** read original EDB/assignment tables with source hashes -> audit geometry, offsets, self-weight, mass, load patterns and effective stiffness -> export documented neutral input -> compare native result tables. **Never mutate the original EDB**.

[Beginner instructions](../engineering/topics/ETABS.md) · [program index](../docs/programs/00_PROGRAM_INDEX.md) · [validation gates](../engineering/rules/ENGINEERING_GATES.md)

**Spyder gravity rebuild fix:** [No-argument GUI selector, original ETABS native workbook requirements and 32-support rerun instructions](../docs/review/20261109_GRAVITY_CLEAR_BEAM_ESM_NATIVE_REMEDIATION.md#spyder-2026-11-10--no-argument-rebuild-procedure). Select the NEW source export folder; do not rerun the old gross-beam model.
