# Aw-X engineering validation gates

**2026-11-12 geometry review: COMPLETED** using the earlier uploaded
`ESM_Review_20261111_192506_593398_UPLOAD.zip` exported
`OpenSees_Complete_Model_Data_V118.json` (SHA256:
`97def708661a10c165b6e0072b045ca7a0a82e13f021649bdb07c3a522a25f72`).
See [completed geometry review](20261112_EXPORT_NODE_GEOMETRY_REVIEW_COMPLETED.md).

The researcher has **selected two 12m X walls** for this thesis. The
following are independently reviewed checks of the exported **shell/node
geometry**, not certification of the original native ETABS model.

## Completed (exported model geometry)
- [x] Two separate parallel X wall planes: Y=6m and Y=12m, each X=6..18m (12m).
- [x] 0.6m wall thickness in exported source wall shells.
- [x] Two 2m door gaps in each X wall: X=8..10m and X=14..16m.
- [x] Both openings occupy the z=0..2.3m horizontal section; continuous wall spans reconnect above z=2.3m.
- [x] Three solid Y walls: X planes 6,12,18m, Y=6..12m, t=0.6m.
- [x] Exported model base z=0m, roof/max-node z≈95m and first-storey upper z=3.8m.
- [x] Recalculate AwX=2.073174515m² and AwY=2.203080332m² using the NBC formula with historical UBC/SEAOC whole-wall interpretation.
- [x] Explain older 4×6m Excel 1.958293629m² and independent-pier 1.930637119m² diagnostics; preserve old calculations as comparisons.
- [x] Add source-derived geometry verification to OpenSees NBC sync, ESM GUI and common Aw resolver, with immutable per-run local review evidence.

## Open (native engineering acceptance)
- [ ] Establish original source EDB file SHA256 against the exact export-time EDB identity, selected ULS/SLS state and any source-verified Excel workbook; *path alone is not a byte-identity guarantee*.
- [ ] Independently confirm ETABS OAPI wall area IDs, polygons, property assignments, wall line continuity and doorway head connectivity.
- [ ] Check reinforcement continuity and structural capacity of coupling/spandrel regions, independently of Aw empirical period.
- [ ] Review native ETABS ↔ OpenSees stiffness, masses, diaphragm behavior and modal/Rayleigh periods, taking account of different supports and ULS/SLS assumptions.
- [ ] Verify that NBC 105 §5.1.2 / §5.1.3 empirical period, analysis eligibility and any base shear scaling are applied appropriately to ~95m irregular RC high-rise.
- [ ] Obtain qualified design-review sign-off before labeling the method CODE_ACCEPTED.

**Final classification:** `GEOMETRY_REVIEW_COMPLETED; NBC_CODE_ACCEPTANCE_OPEN`. It is not valid to label the original Excel 6m calculation as the current project Aw or to claim an ETABS/OpenSees physical equivalence PASS from geometric reconciliation alone.
