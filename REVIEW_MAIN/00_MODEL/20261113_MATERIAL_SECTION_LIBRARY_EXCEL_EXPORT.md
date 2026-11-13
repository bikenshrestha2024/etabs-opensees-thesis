# 02 Model — Material and Section Library Excel export

**Status:** implemented as a read-only, timestamped snapshot of the currently selected export and current repository definitions. **Not** evidence of calibrated nonlinear behavior or NBC compliance.

## Who / what / where

User opens **2. Model → OpenSees material + section library → Export / open complete Excel library**. The GUI uses exactly the same source-table functions as the Excel exporter, eliminating a disconnected or silently hard-coded second spreadsheet dataset. The workbook is written locally under the selected model export:

```
<selected_export>/02_MODEL/MATERIAL_SECTION_LIBRARY/
  OpenSees_Material_Section_Library_YYYYMMDD_HHMMSS.xlsx
```

**Four actual GUI tables** are exported as separate filterable sheets, together with a provenance/readme sheet:

| Excel sheet | Content / source | Critical interpretation |
|---|---|---|
| `Section formulations` | Mapping audit `library()` — beam, columns, wall, SHS, FVD, BRB | Formulation registry, NOT proof material objects were built in a solver |
| `Parameter values and citations` | `parameter_sources()` → active `Define_Section_V109.py` source definitions, PEER material card and device cards | Parameter values, units, parameter-level references; M35/Fe550 and published specimens remain **uncalibrated for the project** |
| `Current source parameters` | `source_parameter_inventory(folder)` → current export `OpenSees_Complete_Model_Data_V118.json` | Native ETABS material elastic section properties (E, G, A, Iy, Iz, J, etc), **not nonlinear concrete/steel reinforcement** |
| `Validation and limits` | `validation_inventory()` | Open research and validation failures, including initial Kobe transient failure and pending FVD/BRB calibration |
| `00_README_PROVENANCE` | Export metadata, UTC creation timestamp and SHA256 of current model data/config | Detect changed inputs: do not treat old workbook as live if file fingerprints differ |

## How to use the export

1. Select the correct ETABS EDB/export folder and build the intended 02 Model configuration as usual; preview the library data.
2. Export the Excel workbook from the material library button. On Windows it opens automatically. Other environments will show the saved file path.
3. Use filters on the `status` column to identify **current source elastic**, **illustrative editable template**, **literature benchmark only**, **missing project evidence**, and other flags. Do not remove qualification text to imply calibration.
4. Compare current source properties with the latest source-hash-identified ETABS output, then separately compare the RC reinforcement and material tests with the nonlinear section builder.
5. Refresh the library or export again **after saving model or material-definition changes**. It creates a new snapshot, not an overwrite or a change to the OpenSees solver. Only `Define_Section` values that were actually saved to disk appear in these tables; uncommitted edits in an open fiber dialog are not yet source parameters.

## Engineering basis and known limits

- The selected ETABS `.EDB` is **never accessed or modified** by the library Excel function.
- The source property `E` is in **kN/m²**. Editable section geometry is **mm** and concrete/steel stresses are **MPa**. The Excel export performs **no silent unit conversion**; OpenSees input scripts must convert explicitly.
- The illustrated 1100×1100 / 1250×1250 columns show **16 perimeter longitudinal bars** (5 positions/side with corners shared, 0 interior bars); 600×800 beam has **12 perimeter bars** (4 positions/side). This is a **geometric template**, not independently verified ETABS reinforcement. Real beam top/bottom reinforcement can differ and must not be inferred from this perimeter schematic.
- The concrete template **M35/Fe550** does not establish the project's source **M45** concrete material, confinement, cyclic response or reinforcement. Correlate with materials, drawings and `ConcreteCM`, `SteelMPF` and `FSAM` cyclic benchmark evidence.
- Initial P-Delta and slab bending IS16700 project sources do not override governing NBC 105:2025 seismic design; the spreadsheet is an evidence and provenance library, not a code-acceptance tool.
- FVD `Cd` units depend on nonlinearity exponent `alpha`: `kN*(s/m)^alpha` (when force and velocity are kN and m/s). Preserve original units in published examples and mark manufacturer/device inputs `REQUIRED`.
- There is no workbook **import-to-OpenSees** button. Updating Excel alone has no effect on solver materials; this is intentional to prevent arbitrary unverified parameters being activated.
- Missing `openpyxl` is reported with a conda-forge installation instruction; existing path collisions never overwrite a prior file.
- This was reviewed by code and deterministic regression test; **native Windows Tkinter/ETABS interaction remains to be verified on the user's system**.

## References

- OpenSees [Concrete01](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Concrete01.html) and [Steel02](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Steel02.html)
- OpenSees [ViscousDamper](https://opensees.berkeley.edu/wiki/index.php/ViscousDamper_Material)
- [PEER Report 2015/12](https://peer.berkeley.edu/publications/2015-12), shear-flexure RC wall material benchmark, Appendix B.3
- [NBC 105:2025 official publication](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf)

**Code files:** `components/sections/library_excel.py`, `components/ui/results.py`; deterministic test `tests/test_model_material_section_library_excel.py`. This feature does not change the converter, source material mappings or analysis output.
