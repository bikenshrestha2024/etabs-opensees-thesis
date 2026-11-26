# rigid_end_zones.py: opt-in ETABS frame rigid end zones

**Implementation:** [rigid_end_zones.py](../../../../components/model/rigid_end_zones.py). Called from `prepare_complete_export` in [assembly.py](assembly.py.md) just before `elastic_conversion_settings.compile_settings`.

**Status:** stiffness input for the elastic ETABS comparison model only (`STIFFNESS_INPUT_ONLY_NOT_ENGINEERING_ACCEPTANCE`). Default off.

## Config

`OpenSees_Complete_Model_Config_V118.json`:

```json
"rigid_end_zones": {"enabled": true, "source": "ASSIGNMENT_WORKBOOK", "factor": "SOURCE"}
```

| Key | Values | Meaning |
|---|---|---|
| `enabled` | `true` / `false` | `false` or an absent block changes nothing; the export is byte-identical |
| `source` | `ASSIGNMENT_WORKBOOK` (default), `SOURCE_METADATA` | ETABS table `Frame Assignments - End Length Offsets` (sheet `Frame Assigns - End Len Offsets`: `UniqueName`, `Offset Option`, `Offset I`, `Offset J` in mm, `Rigid Factor`), or the EDB `FrameObj.GetEndLengthOffset` record in `OpenSees_Source_Model_Metadata_V118.json` |
| `factor` | `"SOURCE"` (default) or 0…1 | rigid-zone factor from the same source, or an explicit override (counted in the audit) |
| `workbook_path` | optional string | default `etabs_native_assignment_workbook_path`, which `tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py` writes |

The block needs a non-empty `elastic_etabs_comparison`, because the rigid zones act through that stiffness path. It must not be combined with hand-written `end_offsets_m`.

## Method and why

- Rigid length per end = offset × rigid factor. `inject_end_offsets` writes it as `end_offsets_m` into every `elastic_etabs_comparison` state. `compile_settings` then puts it on the first and last segment of the frame object as `geomTransf PDelta ... -jntOffset` rigid joint offsets.
- On those outer segments A and J are multiplied by the retained (flexible) length ratio, so EA/L and GJ/L equal the full-length values. CSI: "The rigid zones of the end offsets never affect axial and torsional deformations. The full element length is always assumed to be flexible for those deformations" (ETABS help, Assign > Frame > End Length Offsets). Bending and shear act over the clear length.
- Nodes, nodal loads (beam self-weight is applied as consistent nodal loads on the original segment length), nodal masses and self-weight are not touched. Total gravity load and seismic weight are unchanged. The 2026-11-21 MESH_04 runs confirm it: 311,367.3139 kN in every ablation step.
- Not used: explicit rigid links with new nodes (they would add nodes, move load points and need mass bookkeeping) and stiffened end segments (they need an arbitrary stiffness multiplier). `-jntOffset` is the OpenSees-native rigid offset.
- Hinged braces with a nonzero rigid length are rejected (releases plus offsets are not qualified). ETABS gives braces zero offsets.
- Shear-flexible (`ElasticTimoshenkoBeam`) segments with offsets are still rejected by `compile_settings` (OpenSees `ElasticTimoshenkoBeam3d` is not qualified with `-jntOffset` here). The [preset](etabs_comparison_preset.py.md) therefore uses Euler-Bernoulli frames.

## Audit

`OpenSees_Complete_Export_Report_V118.json` → `rigid_end_zones`: source, workbook file name, factor, number of assembled frame objects and of frames with a rigid zone, total rigid length, and the workbook-against-metadata mismatch count. On the user's assignment workbook (SHA-256 8b3a6b33…) and MESH_04 metadata: 1,312 assembled frame objects (the 55 None-section frames are not assembled), 1,200 with rigid zones (750 beams, 450 columns; the 112 braces have zero offsets), 1,700 offset segments, total rigid length 1,081.25 m, 0 workbook-against-metadata mismatches. Verified on the solved model: beam rigid ends sit only at column nodes (0.55 m × 800, 0.625 m × 450 ends), never at wall nodes, and column rigid ends only at the top (0.8 m × 450); member I is reduced once (0.35 beams, 0.7 columns) (see the [run finding](../../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md) §8).

Tests: `tests/test_rigid_end_zones.py`.
