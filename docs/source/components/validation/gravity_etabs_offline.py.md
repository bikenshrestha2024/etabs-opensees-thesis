# Offline ETABS full-table joint reaction gravity comparison

Module: `components/validation/gravity_etabs_offline.py`.

This module bypasses the failing ETABS OAPI `GetCaseStatus=1` and
`Results.BaseReact()=1` by consuming the **already analyzed** source
ETABS complete XLSX/CSV table export.

The existing Gravity GUI provides the field **Completed ETABS full table
XLSX / Joint Reactions CSV** and action **Compare saved ETABS tables vs BOTH
OpenSees gravity cases (no ETABS API)**. It searches the latest completed
dual-gravity run under the selected output folder. The operation is performed
on a worker thread; neither ETABS model nor OpenSees solver is rerun.
The report is saved in
`Gravity_Wall_Base_Comparison/<run ID>/ETABS_Full_Table_Offline_Comparison/`:

- `ETABS_Offline_Gravity_Comparison.json`
- `ETABS_Offline_Joint_Reaction_Differences.csv`
- `ETABS_Offline_Gravity_Comparison.xlsx`

**ETABS Joint Reactions table contract:** headers include Story, Label,
Unique Name, Output Case and FZ (kN). Only rows having
`Story=Base` and `Output Case=1. DL + LL` are accepted. For a table
with multiple steps for the same unique point, the tool fails closed
rather than choosing an envelope or first row. ETABS point Unique Name
is matched to `node_map[].etabs_point_name` in
`OpenSees_Element_Connectivity.json` and then to original OpenSees
node tags. ETABS display labels and OpenSees numerical IDs are not
interchangeable. Rows that cannot be mapped remain explicit with null
OpenSees values; they are never assigned zero.

A completed source-only OpenSees gravity result and the continuous fixed-wall
alternative are read independently. The source-only run is the ETABS
validation target; the continuous run remains a restraint sensitivity
check. Only 100% DL+LL gravity is supported. Seismic preload results are
not silently substituted.

A very large ETABS XLSX (the user's uploaded full export is ~531 MB) may
take substantial time/memory even with openpyxl read-only parsing, so
**exporting just the Joint Reactions worksheet as CSV** from Excel is a
supported faster input. The original export workbook remains untouched.

The comparison currently covers Base joint reactions only. Separate
work will be needed to reconcile original ETABS `Base Reactions`,
full-frame joint displacements and member self-weight ledger and to
explain the 8680.475-kN gravity weight difference. No acceptance claim
may be made from successful nodal matching alone.

Tests: `python tests/verify_gravity_etabs_offline.py`.

## Split third-lot result evidence (2026-11-27)

An explicitly selected analysis lot that contains the exact Joint Reactions worksheet can be used in the existing offline gravity picker. A source lot without that worksheet is rejected by the shared selection guard. For this purpose the original third lot or its unmodified Joint Reactions CSV is sufficient; it is not a complete assignment/model/analysis export. Do not register an incomplete lot as a replacement for all native evidence or assert same-EDB provenance from matching case names alone. Keep the original workbook, EDB fingerprint and actual case selection local.

The source review confirms the distinction between 76 exported base point records and the project-confirmed 32 physical foundation supports plus 44 mesh points. Match ETABS Unique Name through the actual conversion node map, not an equal integer or display label. Compare the exact 1.0D+1.0L combination. Zero FZ does not prove free native DOFs; a missing OpenSees result is not zero. Existing report wording that requires 76 matched support reactions needs strategy-specific review; it must not be interpreted as a physical acceptance criterion for the primary 32-support strategy.

Source section-cut forces can be checked against summed reactions only for compatible simultaneous/static groups; never sum independent Max/Min envelopes or RSA modal-combined nodal peaks to infer global base shear. Keep relative and absolute dynamic responses separate. Joint Drift Disp X/Y are total displacements; compare adjacent-level displacements at the same exact case/step and coordinates, not total displacement divided by storey height. Equal ordinary and internal-mesh displacement records in one export do not prove internal constraint topology. Do not silently combine duplicate tables or infer missing mode vectors.
