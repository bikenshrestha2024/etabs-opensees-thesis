# Rebuilt ETABS-elastic conversion: remaining 768.045 kN foundation reaction residual

**Investigation date:** 2026-11-22. **Status:** UNRESOLVED; native-source offset coverage now explicitly audited in the converter. No numerical correction or native rerun is claimed by this change.

## User-confirmed interpretation and load-state firewall

- **Exactly 32 physical foundation supports**, with 44 additional base-mapped **shear-wall mesh** points. The 76 ETABS mapped point IDs are **not 76 independent foundation supports**. Preserve interpolation/edge transfer through the wall system. A 76/97 directly fixed OpenSees run is a sensitivity model, not the primary foundation model.
- The reference gravity case is **ETABS `1. DL + LL` / OpenSees `GRAVITY_1.0D_1.0L` = 100% applicable dead + 100% applicable live**. Its observed total is 311367.313880 kN for the historically recorded EDB. **NBC 105:2025 §5.2/Table 5-1 seismic weight (other live .30, storage .60 where applicable, roof .00 per actual classification) belongs to a different analysis purpose**, not this gravity benchmark.
- Do not mix source EDB, model configuration SHA, converted frame/area table, output stiffness basis, or saved reaction vector from distinct export runs.

## Documented actual correction and observed repeat results

The source-attested November 20/21 test in [20261120_GRAVITY_REACTION_REBUILD.md](20261120_GRAVITY_REACTION_REBUILD.md), corroborated by [20261118_32_SUPPORT_GRAVITY_CONVERSION.md](20261118_32_SUPPORT_GRAVITY_CONVERSION.md), rebuilt the original clear-length-weight export with ETABS native frame and shell property/object modifiers. Native shell `Wall 600` factors included membrane `f11/f22/f12=0.50`, bending `m11/m22/m12=0.10`, and transverse shear `v13/v23=1.00`. Three designated source sections used ETABS shear areas with OpenSees `ElasticTimoshenkoBeam` in the reviewed elastic comparison. The regular gravity runner solved ten increments and the independent replay reproduced per-joint values within ~0.01 kN. The original ETABS working-copy rerun independently reproduced the ETABS joint values to <0.000001 kN.

| Quantity | LEGACY_GROSS_SHELL saved run | Rebuilt ETABS_ELASTIC_COMPARISON | Note |
|---|---:|---:|---|
| Global ETABS/OpenSees FZ | 311367.314 / 311367.314 kN | 311367.314 / 311367.314 kN | Total equilibrium is NOT pointwise parity |
| Maximum absolute support `ΔRz` | 3041.266 kN | **768.045 kN** | Main source-matched archived full-run benchmark |
| Sum of 32 absolute support `ΔRz` | 37297.027 kN | **10072.106 kN** | Nearly 73% reduction |
| ETABS joints 263,264, signed ETABS minus OpenSees, each | -3041.266 kN | +113.395 kN | Critical locations shifted |
| Remaining high-error ETABS joints | 263,264 | **261,262,7,8** | Nearly symmetric corner pattern |

The November 18 *in-memory exploratory* frame-geometry stiffness probe achieved a smaller max **756.511 kN**, sum abs **9820.706 kN**, but that is **not** the independent regular-run `768.045` source-provenance-verified benchmark. Do not mix their case IDs or state that an exploratory probe passed engineering acceptance.

One isolated source-matched check split Dead and Live for ETABS joint 8: signed point residual **+649.156 kN Dead** and **+118.918 kN Live** (source document conventions). Their sum differs from the ten-step combined run by about 0.03 kN. Most of the remaining point error at that joint is therefore associated with the *dead-load response*, not accidental replacement by seismic `0.3LL`. This does not by itself identify whether wall, slab or frame load/stiffness transfer is responsible.

## New direct uploaded-file evidence: native frame rigid end-zone coverage

This audit inspected the **actual JSON** `OpenSees_Source_Model_Metadata_V118.json` and `OpenSees_Element_Connectivity.json` inside the user's **MESH_04(3).zip** source export (and checked agreement with MESH_08/16 metadata). For all 1367 source frame objects, `GetEndLengthOffset` was present; **1200** have nonzero offset lengths with **rigid_fraction=1.0**:

| Native source object category / section | Objects with nonzero rigid end lengths |
|---|---:|
| BEAM / `Beam 600*800` | **750** |
| COLUMN / `Col 1100*1100` | **300** |
| COLUMN / `Col 1250*1250` | **150** |
| Other / no effective rigid offset | 167 |
| **Total effective rigid-offset source objects** | **1200** |

These **same three sections** are the `shear_flexible_sections` in the repository's [reviewed ULS JSON](20261121_native_gravity_uls.json). But that JSON has **no `end_offsets_m` mapping**. The actual active conversion path `components/model/elastic_conversion_settings.py::compile_settings` supplies `-jntOffset` **only** for entries explicitly in `end_offsets_m`. It also rejects `ElasticTimoshenkoBeam` with nonzero `-jntOffset` because that combined formulation is unqualified. The user's 2026-11-22 14:29 gravity run explicitly logged `LEGACY_GROSS_SHELL`; it is **not** the improved 768-kN stiffness run and cannot be used to validate the improved solver.

**Conclusion supported by code and uploaded metadata:** the published reviewed settings **do not model the recorded rigid-zone offsets** of 1200 frame objects; this is a concrete *remaining stiffness-model equivalence gap*. **NOT YET PROVED:** that it produces all or a certain fraction of the 768 kN residual, because the current ZIPs are **MESH export/formula studies with unsolved gravity** and the saved 768-kN full-run artifact/EDB SHA was not included in this turn.

**Official CSI basis:**
- [ETABS frame end length offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm): source rigid-zone factor applies to bending/shear end zones; axial/torsional flexibility is separate.
- [ETABS wall auto-mesh edge restraint propagation](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Wall_Auto_Mesh_Options.htm).
- [ETABS automatic shell edge constraints](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Auto_Edge_Constraints.htm).

## Source-driven offset-coverage audit now exposed (not a physical fix)

- `components/model/elastic_conversion_settings.py::audit_native_end_offset_coverage`: compares each assembled unique source frame object's native `GetEndLengthOffset` with the **exact** reviewed `end_offsets_m` if present, records missing/source-conflicted/verified inputs and the overlap with shear-flexible sections; preserves source IDs only in private model-bound results.
- `compile_settings` adds `native_end_offset_coverage` into each per-ULS/SLS conversion plan.
- `components/model/assembly.py` writes the audit to the rebuilt model report and logs `[ETABS SOURCE RIGID END-ZONE COVERAGE]` during a configured elastic run. If native coverage is incomplete it warns explicitly; it does **not** fabricate offsets, change the solver stiffness, change load factors, change foundation supports, or falsely call the remaining residual accepted.
- `tests/test_elastic_end_offset_source_coverage.py`: synthetic cases test missing 1200-style source assignments, exact/mismatched reviewed offset values, the existing Timoshenko+offset incompatibility gate and missing metadata. The CI unit test is a **source/contract check, not a native ETABS gravity acceptance**.

## Most discriminating native experiments — execute in this order

1. **Freeze exact benchmark:** original source EDB SHA, ETABS 23.2.0`1. DL + LL` selected step, corresponding OpenSees model/config SHA, 32 physical support tags, identical load-source ledger and a solved gravity result digest. Verify the rebuilt run says `ETABS_ELASTIC_COMPARISON`, not `LEGACY_GROSS_SHELL`. Preserve 44 mesh points as *connected shell nodes* and never reclassify them as physical foundation supports.
2. **Quantify offset omission in the *actual rebuilt model*** using the new audit's `native_active_rigid_zone_objects`, `native_offsets_unmodeled_count`, `native_rigid_zone_on_selected_shear_flexible_objects`, `source_metadata_missing_count`, plus the exact native object/end-length/rigid-factor pairs. These counts from uploaded mesh export must only be promoted to this baseline when EDB/export SHA identities match.
3. **Prove joint offset + shear-flexible element representation** in a small isolated column/beam/column joint subassembly. Match ETABS and OpenSees `P, V2, V3, T, M2, M3` and displacement/rotations at **the same support-face/cut plane**, including gravity, P-Delta and rigid offsets. Compare source section `As2,As3`, the altered bending/shear span, axial/torsional full-span compliance and loads imposed along member lengths. Do not remove Timoshenko shear area arbitrarily or apply the current forbidden combination without qualification.
4. **Recover native wall-base and frame end forces separately.** Existing native physical-element/edge analysis in the November 20 record showed **8024.059 kN** difference between native wall-corner reactions and wall-element resultant. A reconstruction of 544 `@LC` edge relations predicted **8024.088 kN** with <0.015 kN max withheld-node error. This is evidence of **force attribution/edge interpolation**, not proof of an allowable artificial load or support redistribution. Compare consistent wall physical cuts and six-DOF foundation resultants; maintain separate original 32 support reaction and 44 mesh transfer ledgers.
5. **Separate source Dead and Live** and then *source-object group* for the critical ETABS 261/262/7/8 corners, mapping all source member IDs and split beam-force workbooks. Check beam start/end station location (object end vs support face), ETABS frame rigid zones, centroid/insertion point, shell local axes and constraint/MPC reactions. Do not blame `0.3LL` on a confirmed full `1D+1L` case.
6. **Mesh sensitivity under the identical 100% DL + 100% LL benchmark**: rebuilt MESH_04/08/16 must actually be solved before inferring any physical convergence. The 2026-11-22 ZIP `MESH_BUILD_STATUS.json` files explicitly say `FORMULA_WORKBOOK_CREATED_NOT_GRAVITY_VERIFIED`; their configured assembly `Live=0.3` does not represent a solved 1D+1L benchmark. Keep those experiments separate from the full gravity case until fresh solved identities exist.
7. **Acceptance:** 32 physical foundation `Rz` residuals (max, sum abs, RMS, signed and percent), global 6-component resultant, ETABS native wall-base physical cuts, 1D+1L source-pattern ledger, matching force stations, native and OpenSees displacement/rotation, validated shell-edge topology and model provenance. Only physically supported settings may alter production stiffness. CI green is not an ETABS/OpenSees numerical PASS.

### Open blocker

The **768.045 kN** residual remains unresolved. This patch adds actionable source-to-conversion discrepancy evidence and a fail-visible warning, **not** a tuned numerical solution. See [issue #140](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/140).
