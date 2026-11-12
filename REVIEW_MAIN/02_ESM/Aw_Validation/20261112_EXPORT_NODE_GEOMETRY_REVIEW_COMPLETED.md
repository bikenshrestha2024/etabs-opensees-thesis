# 2026-11-12 | X-direction Aw grouping — review completed from exported node geometry

**Geometry-review status: COMPLETED — two 12 m X walls confirmed from the uploaded OpenSees export.**
**NBC design acceptance: NOT CERTIFIED. Independent original ETABS EDB and response equivalence remain open.**

## User's engineering decision
On 2026-11-12 the researcher explicitly selected **two continuous 12 m reinforced-concrete X walls**, not four independent 6 m grid panels. Each 12 m wall contains two 2.0 m × 2.3 m circulation doors; concrete reconnects over the openings. The researcher confirms wall continuity, full opening overlap in the first storey, thickness 0.6 m and seismic H 95 m. No existing original EDB or Excel input is edited.

## Independently inspected uploaded exported-node evidence
Source evidence: user-supplied `ESM_Review_20261111_192506_593398_UPLOAD.zip` (uploaded in earlier chat), containing:

- `Source_Provenance/OpenSees_Complete_Model_Data_V118.json` (47,502,795 bytes; SHA256 `97def708661a10c165b6e0072b045ca7a0a82e13f021649bdb07c3a522a25f72`)
- `Source_Provenance/OpenSees_Element_Connectivity.json` (1,241,552 bytes; SHA256 `50e5fced4898d65d77825f22fa26764eececb27533be7cda9f1a60f62f8173a0`)
- `Source_Provenance/OpenSees_Analysis_Results/.../NBC105_Input_Provenance_V123.json` (existing audit: historical X=1.9306371 m² pier diagnostic, earlier Excel based on 6m).

Read-only extraction checked 11,072 model nodes and the full 10,400 exported shell set, of which 136 SHEAR WALL shell pieces intersected the first-storey elevation. Source model base z=0.0m and maximum model node z≈95m. Actual first storey extends from z=0 to z=3.8m. All relevant first-storey walls have t=0.600m.

### First-storey X wall lines, exported node coordinates (m)

| Geometric property | X Wall A | X Wall B |
|---|---:|---:|
| Constant Y wall-plane | 6.0 | 12.0 |
| Overall X extent | 6.0–18.0 | 6.0–18.0 |
| Overall structural wall length | **12.0** | **12.0** |
| Horizontal solid intervals at z=0–2.3m | [6,8], [10,14], [16,18] | [6,8], [10,14], [16,18] |
| First door gap | [8,10] | [8,10] |
| Second door gap | [14,16] | [14,16] |
| Net solid width at opening section | 8.0 | 8.0 |
| Minimum horizontal net concrete area | **4.8 m²** | **4.8 m²** |
| Upper segment at z=2.3–3.8m | continuous [6,18] | continuous [6,18] |

The two openings are located at the **same first-storey horizontal elevation** and are bounded by solid concrete intervals. An intermediate 6m architectural grid line does not change the physical full-wall span. Source meshing subdivides each 12m wall into finite elements; mesh-object subdivision is not equivalent to a structural wall separation.

### First-storey Y walls

Three wall planes at constant X=6m, X=12m and X=18m; each has a continuous Y interval [6,12]m, thickness 0.6m and no first-storey opening.

## Governing calculation and alternative results

NBC 105:2025 §5.1.2:

```
Aw = Σ per whole structural wall [Awi * (0.2 + min(Lwi/H,0.9)^2)]
```

Selected X walls: Awi=0.6×(12−2−2)=4.8m², Lwi=12m, H=95m, two wall planes.

**Selected X Aw = 2×4.8×[0.2+(12/95)^2] = 2.073174515 m².**

Unperforated Y walls: Awi=0.6×6=3.6m², Lwi=6m, H=95m, three wall planes.

**Selected Y Aw = 3×3.6×[0.2+(6/95)^2] = 2.203080332 m².**

### Why previous results differ

| Former method | X Aw (m²) | Reason |
|---|---:|---|
| **Selected: two 12m perforated structural walls** | **2.073174515** | 2 groups, net area 4.8 m² each, gross length 12m |
| Former Excel: four 6m panels | 1.958293629 | 4 groups, net area 2.4m² each, grid length 6m |
| OpenSees continuous-pier diagnostic | 1.930637119 | Two X planes each weighted as 2m + 4m + 2m solid intervals, not one connected 12m wall |

Existing OpenSees diagnostic for this exact source geometry:

```
AwX_pier=2 × 0.6 × {
  2 × 2 × [0.2 + (2/95)^2] +
  4 × [0.2 + (4/95)^2]
}=1.930637119 m²
```

This is a **grouping/empirical-formula difference**, not a detected ETABS→OpenSees mesh loss. The source shell material intervals are present and reconnect above the doorway. The diagnostic is retained as a comparison only.

## Interpretation of historic references

- **NBC 105:2025 §5.1.2**: governing Nepal empirical wall area and L/H cap. No specifically illustrated RC doorway grouping in the clause.
- **ICBO 1997 UBC §1628, §1630.2.2 Eq.(30-9)**: minimum first-storey horizontal net area and overall length are separate quantities. Historic UBC precedent; not a Nepal amendment.
- **SEAOC 1997 UBC Design Manual Vol I Example 19**: masonry wall with multiple openings uses net first-storey area and gross 60ft wall length. Demonstrates opening treatment but does not prove RC wall coupling.
- **SEAOC Blue Book 2019 Article 04.03.010**: specifically identifies historic wall-area formula as relevant to *concrete or masonry shear walls*.
- **Balkaya & Kalkan (2004), Engineering Structures 26:2081–2099, DOI `10.1016/j.engstruct.2004.07.005`**: RC wall buildings, wall-opening effects, empirical-versus-FEM period limitations.
- **Goel & Chopra (1998), J. Structural Engineering 124(4):426–433, DOI `10.1061/(ASCE)0733-9445(1998)124:4(426)`**: empirical concrete shear-wall period limitations.
- **SEAOC UBC Manual Vol III, Example 5**: RC walls with coupling beams; modeling/design context, not direct Aw arithmetic.
- All original user-supplied PDFs and snapshots are in the *private* Aw_Validation research package. Do not commit copyrighted PDFs to this public repo. See SOURCE_REGISTER.md.

## Implemented code decision and guards

- `components/inputs/grouped_wall_aw.py`: strict `verify_thesis_two_12m_wall_geometry` checks 2 X/3 Y source planes, actual first-storey material intervals, two X door gaps 2m each, reconnection above 2.3m, 0.6m thickness, H95m; derives full-wall groups and weighted area from source positions; does NOT hardcode 2.073 as output.
- `components/inputs/opensees_nbc_sync.py`: uses reviewed grouped method only if original source EDB exists, model JSON is present and source node/shell geometry passes; preserves original Excel as legacy reference, continuous-pier diagnostic as a separate response, and emits local `REVIEW_MAIN/02_ESM/Aw_Validation` evidence for every new sync.
- `components/inputs/aw_sources.py`: shared modal/ESM source resolver prioritizes verified 12m grouping over the older 6m Excel result for the same project. Missing geometry cannot masquerade as accepted 12m input.
- `components/equivalent_static/calculation_and_gui.py`: one-click node verification and selective prefill when geometry passes. Old workbook is never modified.
- `tests/test_grouped_wall_aw_ubc_seaoc.py`: exact synthetic geometry and regression checks for grouping, opening head, height, three Y walls, and old-pier sensitivity.
- Original EDB, Excel, OpenSees element stiffness and analysis results remain intact.

## Remaining independent acceptance gates

**Completed**: selected structural-wall grouping in *exported shell/node geometry*; door locations/height, wall thickness, building node height; empirical formula computation; explanation of previous Aw discrepancy.

**Open**: read-only direct native ETABS OAPI validation of the EDB identity and material/section/mesh object IDs; reinforcing continuity and capacity of doorway head/spandrels; source-matched ULS/SLS original workbook adoption; comparison of NBC empirical period to Rayleigh/ETABS/OpenSees modes and dynamic analysis requirements; qualified engineer's code-acceptance signoff.

Do **not** label OpenSees–ETABS physical response equivalence or NBC structural design compliance PASS solely because the geometry and Aw now agree.
