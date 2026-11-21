# Wall grouping for the effective wall area Aw (NBC 105:2025 §5.1.2)

Date 2026-11-21. Index: [NBC 105:2025 clause register](README.md). Declarations: [PROJECT_DECLARATIONS.md](PROJECT_DECLARATIONS.md) item 2. This note describes what the repository code does and which references the repository already records. It quotes no reference. Every Aw value produced by this code carries `code_accepted: false`; nothing here is engineering acceptance and no native ETABS or OpenSees run is implied.

## 1. What NBC 105:2025 itself defines

§5.1.2 (printed pp. 29-30) gives the shear-wall coefficient kt = 0.075 / sqrt(Aw), with Aw = sum over i = 1..Nw of Awi {0.2 + (Lwi/H)^2}, where:
- Awi is the first-storey effective wall cross-section area of wall i;
- Lwi is the first-storey wall length of wall i in the considered direction, with Lwi/H <= 0.9;
- Nw is the number of walls in the considered direction (X and Y are evaluated separately);
- H is the height from the base to the roof (see [declaration 1](PROJECT_DECLARATIONS.md): no basement).

The clause does not define how walls are grouped around openings, that is, which parts of a perforated wall form one wall i and how its Awi and Lwi are measured. That is an engineering interpretation, recorded here as a project decision, not a code rule. The clause 5 matrix rows 7, 8, 9 and 15 cover this: the value is supplied by the caller (see the [clause 5 matrix](clause_05_dynamic_characteristics_matrix.md)).

## 2. What the code does

Shared factor: `effective_wall_area_m2` in `components/nbc105/clause_05_dynamic_characteristics.py` computes the sum of Awi (0.2 + (Lwi/H)^2) with Lwi/H clamped at 0.9 (tested by `test_aw_clamps_lwi_over_h_at_0_9`).

`components/inputs/grouped_wall_aw.py` ([guide](../source/components/inputs/grouped_wall_aw.py.md)):
- `grouped_wall_aw(profile, height_m, groups)`: each group is an explicitly mapped whole structural wall `{id, axis, plane_m, thickness_m, start_m, end_m}`. For every first-storey horizontal slice of the exported shell geometry it merges the solid shell intervals that lie on the group's axis, plane and thickness, clipped to the group's span, and multiplies the solid width by the thickness to get a net area. It takes the minimum net area over the first-storey slices as the group's Awi, and uses the gross group span (end - start, openings included) as Lwi: contribution = (minimum net area) x (0.2 + min(gross length / H, 0.9)^2). Contributions are summed per axis. It rejects duplicate or blank ids, axes other than X/Y, non-positive spans, overlapping groups, wall material in any slice that is not assigned to exactly one group, and groups with no concrete in a slice. It never infers groups.
- `source_matched_grouping(...)`: reads an optional local `NBC105_Wall_Grouping_Review.json` from the export folder and uses it only if the original EDB SHA-256, the assembled model SHA-256, the limit state and the height all match; otherwise it raises or returns nothing. Nothing is generated automatically.
- `verify_thesis_two_12m_wall_geometry(profile, height_m)`: a project-specific check of the exported first-storey geometry (H = 95 m, first storey 3.8 m, two X wall planes of 12 m each with two 2 m floor-level door gaps up to 2.3 m and continuous wall above, three solid 6 m Y wall planes, thickness 0.6 m). If every slice passes, it calls `grouped_wall_aw` with the two connected 12 m X walls and the three Y walls and labels the result `EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY`; any mismatch raises an error instead of falling back. It validates the exported geometry only, not the original ETABS model or reinforcement.
- `wall_aw_example(...)` and `selected_two_12m_wall_reference()`: illustrative arithmetic only, never used as source evidence.

`components/inputs/aw_sources.py` (`resolve_aw`) chooses the Aw shown in the modal and ESM windows, in this order:
1. the reviewed grouped value, only when the exported first-storey geometry passes the check above;
2. otherwise the ETABS-linked original Excel value (`ORIGINAL_EXCEL_METHOD_ETABS_LINKED`, the workbook override), accepted only when the workbook's source EDB is the same path or byte-identical to the export's EDB and the limit state and wall thickness checks pass;
3. otherwise the OpenSees geometry candidate, whose continuous-pier diagnostic treats each solid interval as its own wall and is kept as a separate diagnostic.

If the reviewed check fails, no hard-coded Aw (such as 2.073 m^2) is inserted.

Gross versus net, in one line: the area Awi is net of openings (minimum over the first-storey slices) and the length Lwi is the gross span of the connected wall. The 0.9 limit applies to Lwi/H.

## 3. Worked example, using the code's own formula

One wall with Awi = 6 m^2, Lwi = 3 m, H = 95 m:
- Lwi/H = 3 / 95 = 0.031579 (below 0.9, no clamp);
- (Lwi/H)^2 = 0.00099723;
- factor = 0.2 + 0.00099723 = 0.20099723;
- Aw contribution = 6 x 0.20099723 = 1.20598338 m^2.

`effective_wall_area_m2([(6.0, 3.0)], 95.0)` returns 1.2059833795013852 m^2, equal to the hand value (checked 2026-11-21 by running the function).

The repository's illustrative project figures follow the same arithmetic: AwX = 2 x [(12 - 2 - 2) x 0.6] x [0.2 + (12/95)^2] = 2 x 4.8 x 0.215956 = 2.073175 m^2 and AwY = 3 x [6 x 0.6] x [0.2 + (6/95)^2] = 3 x 3.6 x 0.203989 = 2.203080 m^2 (`selected_two_12m_wall_reference()` returns 2.073174515 and 2.203080332). These come from stated geometry, not from a verified ETABS model.

## 4. References the repository already records

The agent has not seen the UBC or SEAOC documents themselves. Only the following is recorded in the repository, in the files named; section numbers are as those files state them.

| Reference as recorded | Where recorded |
|---|---|
| 1997 Uniform Building Code, §1628 (definitions) and §1630.2.2 Eq. (30-9); the files say these are in Volume 2 and that Volume 1 must not be miscited | `components/inputs/grouped_wall_aw.py` (docstring), [source guide](../source/components/inputs/grouped_wall_aw.py.md), `REVIEW_MAIN/02_ESM/AWX_20261111_UBC_SEAOC_DOOR_OPENINGS_DECISION.md`, `REVIEW_MAIN/02_ESM/Aw_Validation/SOURCE_REGISTER.md` (R06) |
| SEAOC Seismic Design Manual Vol. I (1997 UBC), Example 19, printed p. 63 (PDF p. 66 of the user's upload); recorded as a masonry wall example | `REVIEW_MAIN/02_ESM/Aw_Validation/SOURCE_REGISTER.md` (R01), the decision register above, the source guide |
| SEAOC Blue Book 2019, Article 04.03.010 Period Determination (PDF p. 125) | `SOURCE_REGISTER.md` (R02), `20261112_EXPORT_NODE_GEOMETRY_REVIEW_COMPLETED.md` |
| SEAOC Seismic Design Manual Vol. III, RC wall Example 4 (printed p. 209) and coupled wall Example 5 (printed p. 237+); recorded as modeling context, not Aw arithmetic | `SOURCE_REGISTER.md` (R03) |
| SEAOC Blue Book (1999) and other uploaded RC period research | `REVIEW_MAIN/02_ESM/Aw_Validation/20261112_ADDITIONAL_RC_SOURCES_REVIEW.md` |

Other repository locations that mention them: `components/inputs/opensees_nbc_sync.py`, `components/inputs/aw_sources.py`, `components/equivalent_static/calculation_and_gui.py`, `tests/test_grouped_wall_aw_ubc_seaoc.py`, `REVIEW_MAIN/02_ESM/Aw_Validation/README.md` and `REVIEW_GATES.md`.

LITERATURE folder: it holds no UBC or SEAOC PDF and no `MASTER_LITERATURE_INDEX.csv` row for them. They appear only as URL entries (status UNMATCHED) in `LITERATURE/Codes_Standards/CODE_REFERENCES.md`, `LITERATURE/OpenSees_Methods/CODE_REFERENCES.md` and `LITERATURE/CODE_CITATION_OCCURRENCES.csv`. `SOURCE_REGISTER.md` states that the source PDFs were supplied privately and are not in the public repository; their SHA-256 values are in a separate research ZIP that is not in the repository.

## 5. User's validation

USER_DECLARED 2026-11-21: the wall grouping was validated by the user against UBC and SEAOC references. The repository's records above are the closest it holds to those references. `REFERENCE DETAILS PENDING FROM USER`: the edition, section or example the user validated against, and the validation itself, are not in the repository. The repository's own files describe the UBC and SEAOC material as historical interpretive precedent, not a Nepalese adoption, and say the SEAOC Example 19 is masonry. The agent did not verify the validation.
