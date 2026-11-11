# Engineering decision register — first-storey door openings in NBC 105:2025 Aw

**Decision state:** PREFERRED RESEARCH INTERPRETATION; SOURCE MODEL GROUPING NOT YET VERIFIED.
**Model:** Current ULS EDB in main GUI (do not infer equality with SERVICE calculation workbook).
**Date:** 2026-11-11.

## Observed issue
Current OpenSees source geometric method groups disconnected solid shell intervals at each storey height, so X-direction connected wall bays with floor-level door openings are treated as independent short piers when determining `(Lwi/H)^2`. This produced X continuous-pier diagnostic of **1.930637119 m²** in the user's actual export. This value is a useful mesh/continuity diagnostic but **not necessarily the NBC 105 structural-wall effective area**. Y continuous-pier diagnostic **2.203080332 m²** agrees with the user's no-opening Y calculation.

## Governing provisions and documented interpretations
1. **NBC 105:2025 §5.1.2 p.29–30**: `Aw=Σ Awi [0.2+(Lwi/H)^2]` with max `Lwi/H=0.9`. `Awi` is effective first-storey wall cross-section and `Lwi` is structural wall length parallel to excitation. NBC does not expressly state a door-opening grouping rule.
   Official DUDBC: https://dudbc.gov.np/pages/24231978/
2. **UBC 1997 §1628**: `Ae` is minimum wall area in any first-storey horizontal section; `De` is wall length in applied force direction. **§1630.2.2 Equation (30-9)** uses `Ac=ΣAe [0.2+(De/hn)^2]`, `De/hn<=0.9`. Source: https://www.najah.edu/media/cms_page_media/482/UBC_Volume2.pdf
3. **SEAOC 1997 UBC Seismic Design Manual, Vol. I Example 19 p.63**: in a **masonry** front-wall example, `De=60 ft`, `Ae=(60-4*10)*7.63/12=12.7 ft²`, i.e. area net of openings and length gross. This is strong historic *application* precedent but not an official NBC interpretation nor an RC coupling test. Source: https://www.framece.com/uploads/3/9/0/1/3901564/ubc97_-_sdm_v1.pdf
4. Relevant Indian analogue IS 1893 (Part 1):2016 §7.6.2 is informative but not controlling; IS 13920 and ACI 318 wall opening/coupling requirements are **separate from empirical period Aw**. ASCE 7 modern approximate periods must not be interchanged without checking their governing scope.

## User example — explicitly assuming all seven wall groupings and critical first-storey geometry
- Four 6.0 m X-direction wall groups, each 0.6 m thick with a 2.0 m wide and 2.3 m high floor-level **door for circulation**, overhead wall/spandrel.
- Minimum horizontal net cross-section per X wall `Awi=(6-2)*0.6=2.4 m²`, gross connected wall span `Lwi=6 m`, building height `H=95 m`.
- `AwX=4*(2.4)*(0.2+(6/95)^2)=1.9582936288 m²`.
- Three solid Y walls, each 6.0 m x 0.6 m, yield `AwY=3*(3.6)*(0.2+(6/95)^2)=2.2030803324 m²`.
- Existing user's original Excel Aw-X/Y numbers match these *hypothetical dimensions* exactly, not independently the currently selected source EDB. Existing SERVICE workbook B4 source mismatch with ULS EDB must remain blocked.
- Do **not** add wall/spandrel above the opening again as a second `Awi` contribution.

## Decision
Use the **minimum net horizontal first-storey area + full structural wall span**, as in UBC/SEAOC historical practice, for explicitly reviewed connected perforated wall groups when considering the NBC §5.1.2 empirical period. Do **not** replace source-original Excel calculations or delete the continuous-pier diagnostic. The independent continuous-pier approach remains a sensitivity indicator, not an automatic adoption basis. A rigidly coupled RC wall cannot be deemed equivalent to a perforated wall by the simple Aw formula alone.

## Code changes & safety gates
- `components/inputs/grouped_wall_aw.py`: source-slice minimum area and explicit overall wall span; rejects overlapping/unmapped source wall groups; includes standalone 4 X / 3 Y illustrative reference.
- `components/inputs/opensees_nbc_sync.py`: records source-matched group candidate and old pier diagnostic independently, with both available in JSON/Excel. Requires optional local `NBC105_Wall_Grouping_Review.json` whose **source EDB SHA256, model SHA256, H, ULS/SLS** match. If absent, no physical assumption is made and original behavior remains.
- `components/inputs/aw_sources.py`: candidate retains `REVIEW_REQUIRED` status; it is not a physical or code PASS.
- Tests verify door 2.3m / X net area / Y solid, limit 0.9, source hashing and uniqueness. Synthetic tests **do not** constitute native ETABS/OpenSees equivalence.

## Items still required before engineer sign-off
1. Read actual EDB first-storey wall coordinates, all four door locations, thicknesses and spandrel/coupling-beam edges; validate the manually identified structural wall groups.
2. Verify continuous lateral force load path and actual coupled-pier mechanics, wall openings and drift/stiffness, project reinforcement and supported modeling methodology.
3. Verify height `H=95m` based on NBC base/roof and basement definition.
4. Obtain a source-matched ULS workbook or independently documented manually reviewed NBC area; do not infer equality from a mismatched SERVICE workbook.
5. Check whether empirical wall period governs or is only one limit/approximation compared with Rayleigh, modal and MRSM outputs. ESM eligibility for a ~95m building remains restricted.
6. Reviewer must approve wall grouping and code interpretation separately from solver convergence.

**Acceptance:** No native structural equivalence or NBC design acceptance is claimed by these commits.
