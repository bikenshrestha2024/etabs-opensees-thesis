# tools/etabs_beam_slab_load_path.py: source guide

**What:** a read-only reader for an ETABS database-table export (assignment workbook) and one or more `Element Forces - Beams` workbooks. It reports, per storey and load case, the vertical load carried on the beam clear spans (V2 at the J face minus V2 at the I face) against the beam self weight and uniform frame loads on the clear span, and the beam end shears delivered to joints inside a plan box (normally the core) against simple-span statics. It also reports the floor area whose corners lie in the box when each corner of a four-node floor object takes a quarter of its load, and, optionally, ETABS storey masses times g against an OpenSees storey ledger.

**When:** after exporting ETABS tables for a gravity comparison, to see how ETABS moves slab load into beams and joints before attributing support-reaction differences to the OpenSees load path.

**Why:** with floors set to `No Auto Mesh`, ETABS connects each floor shell to the frame only at its corners. A constant V2 along a beam under Live load shows that no slab load reaches the span. That changes the load path compared with a meshed OpenSees slab, but not the rigid-support statics split. The tool separates the statics share from the beam-flexure transfer, which depends on stiffness. Finding: [GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md](../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md).

**How:** streaming `openpyxl` readers reused from `components.validation.etabs_assignment_gravity_audit._rows` (title, header, units rows) and `components.validation.etabs_split_beam_forces._stream_rows` (header search). Rows of the requested cases (default `Dead`, `Live`) are kept and overlapping rows from split files must agree (abs 1e-6, rel 1e-9), otherwise the tool fails. A file whose data rows reach 1,048,573 is flagged `reached_excel_row_limit`; the beams-per-storey-case counts show what each file holds. Self weight is γ·A·weight-modifier on the clear span only (ETABS reports clear-length beam weight); uniform frame loads on the rigid zones go straight to the joints. Only full-length uniform gravity frame loads are supported. The ledger option computes W = dead + 0.3·live + 0.6·storage from a `Gravity_Storey_Load_Breakdown` JSON; those factors are the caller's assumption. Masses are converted with the project g (`components.nbc105.constants.GRAVITY_M_S2`, 9.81) and with the ETABS internal g, which is derived from the export as UnitWeight/UnitMass of `Mat Prop - Basic Mech Props` (9.80665 m/s² for this model), so m × g_source recovers the ETABS weights.

**Where:** source `tools/etabs_beam_slab_load_path.py`; tests `tests/test_etabs_beam_slab_load_path.py`. CLI:

```
python tools/etabs_beam_slab_load_path.py --assignment Assignment_Export.xlsx \
  --beam-forces Beam_Forces_1.xlsx Beam_Forces_2.xlsx Beam_Forces_3.xlsx --core-box 6 18 6 12 \
  [--cases Dead Live] [--storey-breakdown Gravity_Storey_Load_Breakdown_V131.json --live-factor 0.3] \
  [--export-dir <existing export case root> --case-id NAME --state AS_CONFIGURED]
```

With `--export-dir` the tool creates `<export>/02_GRAVITY/RUNS/<state>/<case>/<run id>/` following the [output-folder standard](../../OUTPUT_FOLDER_STANDARD.md): the JSON summary and the per-beam CSV go to `05_COMPARISONS`, input SHA256 values to `00_INPUT_SOURCE`. The manifest keeps `solver_status = CREATED` and `structural_acceptance = NOT_VERIFIED`.

**Which:** it reads `.xlsx` files only, opens no EDB, imports no solver and changes no load, mass or stiffness. Status is always `DIAGNOSTIC_NOT_ENGINEERING_ACCEPTANCE`.

**Limits:** the slab corner split is rigid-support statics; real slab corner forces depend on slab bending and differential settlement, which the export does not contain. Brace and wall-shell forces are not read. Beam forces are at the rigid-zone faces; the sign convention assumed is ETABS V2 (reaction at I = −V2_I, at J = +V2_J), checked by the span-load balance. OpenSees beam end actions are not read; compare them only after a gravity run that writes them.

**Who:** the software maintainer owns the tool; the thesis author owns any engineering reading of its output.
