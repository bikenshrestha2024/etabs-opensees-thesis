# ETABS 23 → OpenSeesPy conversion: engineering acceptance and source-integrity audit

**Review date:** 2026-11-22 (Asia/Kathmandu). **Audit scope:** current production modules in `components/model`, gravity source/solver interfaces and source-backed November 18–22 comparison evidence. **Status:** CONVERSION_RUNNABLE; **NATIVE_ETABS_OPENSEES_EQUIVALENCE_NOT_ESTABLISHED**. This is a code and prior-evidence review; no ETABS OAPI session, new 25-storey OpenSees run, native EDB or complete force workbook was executed here.

## Mandatory project basis

- The user-confirmed actual physical foundation consists of **32 support joints**; the other **44 points among the 76 base-mapped source IDs are shear-wall mesh points**, not 44 independent physical foundations. Preserve 44 mesh points' stiffness/connectivity and ETABS auto-edge/MPC force transfer. Do not substitute 76 or 97 directly grounded nodes for the 32 physical support reference.
- Primary exact gravity comparison = **100% dead + 100% live** (`GRAVITY_1.0D_1.0L`) against ETABS `1. DL + LL`. The observed matched full gravity total of `311367.313880 kN` proves global FZ equilibrium **only**.
- Seismic weight/mass is **a different purpose** defined by NBC 105:2025 §5.2/Table 5-1, classified dead=1, storage live=0.6, other live=0.3, roof live=0 where applicable. Neither `0.3LL` seismic weighting nor NLTHA preload is a substitute for the full 1D+1L gravity benchmark.
- Source-aligned current geometry has **two X-direction 12 m core walls with openings** and three Y-direction 6 m solid walls, with source-derived thickness/sections. The V10.7 NBC calculator is not interchangeable with older spreadsheets. Verify source EDB and all exact workbook SHA256 values per case.

## Inspected implementation path

| Stage | Active implementation | Source-level observation / acceptance |
|---|---|---|
| Native ETABS source metadata | `components/model/assembly.py::extract_source_metadata` | Reads frame `GetReleases/GetLocalAxes/GetInsertionPoint/GetEndLengthOffset`, native section props and combined object/section modifiers; collection errors appear in metadata. **Actual native EDB identity not independently verified here.** |
| Geometry/polygons | `components/model/assembly.py::_mesh_areas` | Rebuilds only four-node parallelogram wall/slab panels into a shared `ShellMITC4` quad mesh. Not native ETABS analytical mesh equivalence; opening geometry and shell/beam interfaces need native evidence. |
| Source joint identity | `components/model/source_node_identity.py` and `_mesh_areas` | **New source-integrity fix:** prior XYZ dict comprehension overwrote a prior source node tag silently on coincident source coordinates. Conversion now fails closed instead of picking an arbitrary tag; read-only exported-source diagnostic identifies duplicates/incomplete records. No solver stiffness or support topology altered. |
| Frame subdivision | `components/model/assembly.py` frame loop | Scans interior *geometrically coincident* nodes and splits physical frame objects; preserves parent object/segment ledger. ETABS frame auto-mesh and real connection/edge constraints still require actual analytical-mesh evidence; geometric intersection alone does not prove a mechanical tie. |
| Section and stiffness | `components/model/elastic_conversion_settings.py`, `components/model/linear_shell_stiffness.py` | Native frame/object bending/shear factors and wall in-plane/plate factors are partly replicated. Uniform membrane/plate factors supported; `ShellMITC4` plate vs transverse shear cannot independently reproduce ETABS `m=0.1` vs `v=1.0` using the current `ElasticMembranePlateSection` proxy. |
| Frame end zones | `components/model/elastic_conversion_settings.py::_offsets` | Real ETABS `GetEndLengthOffset` values are captured but `docs/validation/20261121_native_gravity_uls.json` does **not** supply `end_offsets_m`. Active shear-flexible `ElasticTimoshenkoBeam` + nonzero joint offsets is explicitly rejected pending qualification. |
| Loads/weight | `components/model/beam_weight_convention.py`, `components/model/assembly.py`, `components/model/load_case_purpose.py` | Clear-beam self-weight verified in prior ETABS object quantity audit; distributed load vectors preserved separately. Full 1D+1L and NBC seismic-mass factors are distinct. Global load sums do not validate local slab-to-frame/wall transfers. |
| Supports/reaction recovery | `components/gravity/etabs_reaction_support_filter.py`; `components/validation/gravity_native_equivalence_preflight.py` | Fixed 32 expected physical foundation tags; 44 native-restrained *mesh points* appear in saved object-layer export. The source analytical-edge constraints, object vs element JointReact attribution and common foundation cuts remain unverified. Updated preflight labels the role rather than calling 44 new foundations. |
| Nonlinear walls, braces and devices | `components/model/assembly.py`, `components/nonlinear_time_history` | Nominal wall material/reinforcement and X-wall first-step nonfinite failure remain open, so the elastic conversion does not establish validated M0–M6 NLTHA. |

## Reproduced source-record findings (not rerun in this review)

The **real ETABS-elastic rebuild** produced the following independently repeated 32-support *full gravity* comparison in the November 20/21 recorded investigations:

| Saved case | Max absolute joint vertical residual | Sum absolute residuals (32 joints) | ETABS–OpenSees result |
|---|---:|---:|---|
| Legacy gross-wall `LEGACY_GROSS_SHELL` | 3041.266 kN | 37297.027 kN | Not accepted |
| Source-converted `ETABS_ELASTIC_COMPARISON` | **768.045 kN** | **10072.106 kN** | **Not accepted** |
| Exploratory in-memory geometric stiffness probe | 756.511 kN | 9820.706 kN | Research-only, not accepted |

The **768-kN case** is the production-rebuilt conversion baseline; do not report 3041 kN for that model or promote the 756 kN probe into a production-verified result. Remaining critical physical support locations: ETABS 261/262/7/8. At ETABS joint 8 the split source-case residual was +649.156 kN Dead and +118.918 kN Live (ETABS-minus-OpenSees per recorded convention). The **dead-load transfer path accounts for most of this one point's difference**.

In **separate MESH_04/08/16 uploaded source metadata**, 1200 of 1367 source frame objects have nonzero native rigid-zone end-offset lengths with factor 1.0: 750 Beam 600×800, 300 Col 1100×1100 and 150 Col 1250×1250. This does not independently establish that the archived 768-kN run's EDB/export fingerprint is identical. The source offset-coverage audit reports omissions instead of automatically changing stiffness; see [specific offset investigation](../../docs/validation/20261122_REBUILT_ELASTIC_768KN_RESIDUAL_AUDIT.md).

Native ETABS `@LC` line/edge interpolation and force-recovery records also explain part of the reported original wall-base reaction attribution: prior source reconstruction of 544 edge relations predicted an ~8024.059 kN wall-corner versus native element-force difference within ~0.015 kN at withheld base nodes. **This is evidence of ETABS edge-force transfer, not permission to add reactions or substitute 44 fixed foundations.**

## Newly identified software error and bounded correction

The previous `_mesh_areas` implementation initialized source point lookup by `{rounded_xyz: node_tag for node_tag,xyz in source_nodes.items()}`. **Different source tags at identical XYZ were silently collapsed** by last-writer-wins. If those tags represent independent joints, releases, wall edges or MPC endpoints, a generated shell grid can attach to the wrong DOF. This is a definite *unsafe implementation mechanism*, not verified to have occurred in the current thesis export.

New `unique_coordinate_lookup` validates finite three-component coordinates and stops with explicit conflicting tag/coordinate evidence rather than making an invented connection. `audit_node_map_identity` reports collision groups, reused tags and unavailable coordinates in the existing gravity conversion preflight. The model remains numerically unchanged for uniquely tagged coordinates. No `equalDOF` was invented. New deterministic regression tests exercise the actual mesher, source map reporting and saved-export preflight. If native coincident tags are intentionally linked, a **source-verified joint relationship adapter** will be required; the converter must not silently fuse or independently tie them.

## Open native equivalence gates (must not be declared PASS)

1. **G0 same-source identity:** EDB sha256, assignment/analysis tables/beam force part hashes, reviewed frame/area metadata, config SHA, solver version and saved 32-support result digest. No stale workbook or legacy shell state.
2. **G1 physical support topology:** 32 actual foundations, 44 wall mesh points and full native ETABS analytical shell edge/MPC constraints, with common six-DOF foundation reaction recovery.
3. **G2 elastic frame/section stiffness:** native `A,As2,As3,J,I22,I33` section/object factors, source local axes/releases, ETABS finite rigid-end-zone flexibilities vs target frame element and consistent load application. Current shear-flexible+offset representation not accepted.
4. **G3 shell and diaphragm:** native wall/floor auto mesh and opening connectivity; membrane, plate, transverse shear, master-slave floor constraints and shell-to-frame vertical load path. `ShellMITC4` section approximation must be benchmarked on native patches.
5. **G4 load-source source force comparison:** full D and L separated (including original 750 beam force objects and all split Excel parts), beam support-face moments/shears, slab resultant/vertical deformation, wall-base section cuts, foundation wrench, individual joint reactions and displacement/rotation.
6. **G5 dynamics and NLTHA:** modal periods/modal mass/stiffness states in ETABS vs OpenSees; correct seismic weight as NBC Table 5-1; code P-Delta initial cases; actual RCC wall rebar/confinement and calibrated material; full first-step nonlinear stability and 224 full-duration runs when appropriate.

## Executable checks and present scope

```text
python -m unittest -v tests.test_source_node_identity_conversion
python -m pytest -q tests/test_elastic_end_offset_source_coverage.py tests/test_elastic_conversion_settings.py
python -m components.validation.gravity_native_equivalence_preflight <SAVED_EXPORT_DIR> <NEW_EMPTY_AUDIT_DIR>
```

The third command is a **read-only saved-export preflight** (separate new audit directory) requiring local private model export files and optional `--primary-audit`. Do **not** publish its raw ZIP if it includes confidential paths/geometry or source point IDs. No native ETABS/OpenSees solve was executed in this PR; synthetic tests cannot prove G0–G5.

**Bottom line:** the converter is an **incomplete source-sensitive structural translation**, and proper design/engineering equivalence is **not established** until the native gates above are passed. See [reaction blocker #140](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/140).

## Engineering reference basis

- [CSI ETABS end length offsets](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm) — rigid zone factor changes bending and shear without altering axial/torsional flexibility.
- [CSI ETABS wall auto mesh options](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Wall_Auto_Mesh_Options.htm) — generated edge restraints/constraints conditional on wall corner assignment.
- [CSI ETABS automatic shell edge constraints](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Auto_Edge_Constraints.htm) — interpolation/edge force transfer and nonmatching analytical mesh implications.
- [OpenSees ShellMITC4](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/ShellMITC4.html), [OpenSees ElasticTimoshenkoBeam](https://openseespydoc.readthedocs.io/en/latest/src/ElasticTimoshenkoBeam.html).
