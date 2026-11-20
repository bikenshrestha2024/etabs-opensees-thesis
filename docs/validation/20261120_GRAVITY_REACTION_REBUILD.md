# November 20 gravity reaction rebuild

The archived 32-restraint run used verified clear-length beam self-weight and gross elastic wall stiffness. The beam weight correction reconciled global gravity. The stiffness diagnosis was still a separate experiment when that export was built. The new rebuild accepts native ETABS stiffness settings for an explicitly selected elastic comparison.

## Recorded results

ETABS case `1. DL + LL` and OpenSees profile `GRAVITY_1.0D_1.0L` both gave 311,367.313880 kN total upward reaction to the shown precision. The same 32 support coordinates, selected from the source analysis workbook, and the same applied OpenSees load were used. The reviewed candidate was solved with the regular gravity runner in ten increments. The ETABS reference is the saved direct extraction from the source EDB's analyzed working copy.

| Quantity | Archived clear-beam model | Reviewed elastic model |
|---|---:|---:|
| ETABS 263 / OpenSees 36, ETABS − OpenSees (kN) | −3,041.266 | +113.395 |
| ETABS 264 / OpenSees 41, ETABS − OpenSees (kN) | −3,041.266 | +113.395 |
| Largest absolute difference at any support (kN) | 3,041.266 | 768.045 |
| Sum of absolute differences for the 32 matches (kN) | 37,297.027 | 10,072.106 |

The earlier controlled [wall-membrane-only probe](20261118_32_SUPPORT_GRAVITY_CONVERSION.md) reduced the maximum error to 825.043 kN. Native `Wall 600` in-plane modifiers are 0.50. Its plate bending modifiers are 0.10 and its transverse shear modifiers are 1.00. The gross-wall branch omitted the in-plane reduction and concentrated gravity at 263 and 264. The reviewed model applies native frame and shell object and property modifiers. It also uses ETABS shear areas on the three designated frame sections. [CSI shell stiffness modifiers](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Shell_Stiffness_Modifiers.htm)

The largest remaining differences are at 261, 262, 7 and 8, which form a nearly symmetric set. Separate one-increment dead- and live-load runs produced 263,367.314 kN and 48,000.000 kN total reactions respectively. At point 8 the signed residuals are +649.156 kN for dead and +118.918 kN for live. The largest pointwise departure of the sum of the separate OpenSees results from the ten-step combined run is 0.033 kN, which is immaterial to the 768 kN residual. The dead-load distribution therefore accounts for most of the remaining discrepancy at these corners. This comparison alone cannot assign the difference to a particular load pattern, shell edge, or frame joint.

## Restraints and native force recovery

The 76-restraint run transferred 104,463.014 kN to the 44 extra fixed OpenSees nodes whose corresponding ETABS points report zero FZ. The 97-restraint run adds another 21 direct fixities. The 32-restraint case is a diagnostic approximation to the 32 reaction-bearing native locations. The identified 44 ETABS points remain part of the native restraint and shell edge-constraint topology. Zero reported FZ alone is insufficient to classify their kinematic roles. [CSI automatic shell edge constraints](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Auto_Edge_Constraints.htm)

The 8,024.059 kN difference between native wall-corner support reactions and the integrated native wall-element results has a separate explanation. A previous analysis using the native physical-element nodal forces and the geometry of 544 `@LC` edge relations fitted the edge transfers using above-base nodes. It predicted 8,024.088 kN at the withheld base nodes, with a maximum point error of 0.015 kN in that reconstruction. This identifies a force recovery mechanism in the ETABS outputs. The reconstructed transfers are evidence for the next mesh comparison and are never applied as artificial OpenSees loads.

## Reproduce the reviewed rebuild

Use **Rebuild with ETABS elastic settings** in the updated gravity GUI. Select the reviewed assignment workbook, the JSON below, and a new output location. The CLI tool `tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py` accepts the same JSON via `--elastic-comparison-settings` together with `--source-dir`, `--assignment-workbook` and `--dest-dir`.

```json
{
  "ULS": {
    "use_native_frame_modifiers": true,
    "use_native_shell_modifiers": true,
    "allow_shell_shear_approximation": true,
    "shear_flexible_sections": ["Beam 600*800", "Col 1100*1100", "Col 1250*1250"]
  }
}
```

Run the rebuilt gravity model with the 32-point diagnostic, the original ETABS analysis workbook and full gravity. Check the direct comparison for the support strategy, the `ETABS_ELASTIC_COMPARISON` stiffness basis and the model configuration SHA-256. The rebuild evidence carries the numbers of source shell objects, shear-flexible frame segments, and shells using the transverse shear approximation. The configured stiffness applies to the selected elastic state. A separate configuration is required to reproduce a different ETABS stiffness state.

## Remaining validation

The current OpenSees elastic shell section couples its transverse shear modifier to plate bending. The comparison JSON opts into that approximation. Earlier independently resolved shear and plate-bending probes produced a similar residual. The reviewed configuration retains centerline stiffness geometry and uses the verified clear beam length for weight. The previously tested eight-subdivision variant had a larger maximum error. These findings support a native analytical-mesh comparison with explicit edge transfers, matched insertion and end-zone settings, separate dead-load patterns, base wall section cuts, and beam support-face forces. Pointwise foundation reaction equivalence remains open. [OpenSees elastic shell section source](https://github.com/OpenSees/OpenSees/blob/master/SRC/material/section/ElasticMembranePlateSection.cpp) · [CSI end offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm)
