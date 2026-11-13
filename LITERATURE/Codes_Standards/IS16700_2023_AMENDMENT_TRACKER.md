# IS 16700:2023 first revision — project crosswalk, 2025 amendment gate

**Reviewed:** 2026-11-13. **Authority:** Bureau of Indian Standards (BIS), CED 38. **Classification:** Indian supplementary tall-building standard, **not** Nepal's governing seismic design code.
**Project-use restriction:** IS 16700 is adopted for **initial P-Delta cases (§7.2(d))** and **conventional slab flexural Ig (Table 5) only**. All other checks remain supplementary, subordinate to NBC 105:2025 and cannot change NBC seismic calculations. See [governing-code matrix](../../KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md).

**Uploaded study copy:** *IS 16700:2023 Criteria for Structural Safety of Tall Concrete Buildings* (First Revision), September 2023, 38 PDF pages. The file was **not copied to public GitHub**: the supplied download copy contains an identifying access watermark. Keep original privately and record SHA256 only in the private literature ledger.

## Edition / amendment warning (do not omit)

The **BIS Standard Details catalog for IS 16700:2023 explicitly lists "First Amendment", year 2025**. The user's September 2023 PDF does **not demonstrate** inclusion of that amendment. **AMENDMENT_TEXT_NOT_YET_RECONCILED**: review the authenticated amendment itself; record its clauses, amended pages, issue date, effective applicability, interpretation, and a date-of-retrieval screenshot/checksum. Until then, cite provisions below as "**2023 base PDF, subject to 2025 Amendment No. 1 verification**", never as a fully amended 2026 version.

BIS catalog: https://standards.bis.gov.in/website/standard-details (search for IS 16700:2023). Catalog discovery is confirmed; the amendment's affected clauses have **not** been determined.

## Uploaded 2023 PDF evidence crosswalk — clause text independently consulted

| Page in printed standard (PDF page) | Clause | Source-derived summary (not verbatim) | Model implication / check | Status |
|---|---|---|---|---|
| 1 (3) | 1.1, 1.4–1.5 | Primary scope: RC buildings >50–250 m; may be used <=50 m; expressly includes outrigger and belt-truss systems | Relevant as supplementary research basis for the 25-storey concrete-outrigger building | BASE_TEXT_VERIFIED, AMENDMENT_PENDING |
| 1 (3) | 1.2 | Near-field definition is within 10 km of seismogenic fault; prescriptive approach needs more rigorous review there | Near-field *ground-motion classification* is not the same as *site-to-fault distance*; obtain site-fault distance before applying this clause | BASE_TEXT_VERIFIED, PROJECT_SITE_UNKNOWN |
| 4 (6) | Table 1, note 1 | For table classification, walls outside the core carry at least 25% of lateral actions to count as well-distributed | Core-only configuration may not satisfy an IS prescriptive category; requires load-share calculation, not assumed failure/pass | BASE_TEXT_VERIFIED, APPLICABILITY_REVIEW |
| 5 (7) | 5.4.1, 5.5.1 | Contains separate serviceability/earthquake drift checks and a torsional-to-translational period rule | Do not replace NBC 105:2025 drift or torsion criteria; investigate torsional behavior as supplementary sensitivity | BASE_TEXT_VERIFIED, SUPPLEMENTARY |
| 7 (9) | 7.2(a)–(d) | Include rigid end offsets, diaphragm flexibility, cracked properties, and initial P-Delta case `1.2 DL + 0.5 IL ± 1.5 EL/WL` | Independent +X/-X/+Y/-Y project gate; do not confuse with seismic weight ledger or sustained NLTHA preload | BASE_TEXT_VERIFIED, NATIVE_EVIDENCE_REQUIRED |
| 7 (9) | Table 5 | Slab `Ig`: SLS 0.35, strength 0.25; beam 0.70/0.35; column 0.90/0.70; wall 0.90/0.70; member `Ag=1.0` | Explain *element and limit state* and compare against separately sourced NBC Table 3-1; NEVER silently replace NBC wall 0.50/0.70 cracked ULS/SLS references with IS wall 0.70/0.90 | BASE_TEXT_VERIFIED, ADOPTION_NOT_APPROVED |
| 8 (10) | 7.3.1–7.3.9 | Model mass/stiffness, diaphragm, irregularity, member strength/deformation and second-order effects | Compare source ETABS shell/frame sections and OpenSees stiffness/load paths | BASE_TEXT_VERIFIED, PROJECT_VERIFICATION_PENDING |
| 8 (10) | 7.3.10 | Interstorey drift stability coefficient theta, limit 0.2 | Evaluate with the exact source equation, correct vertical load, story design shear/height/drift and response reduction factor; an empty GUI table is not a completed check | BASE_TEXT_VERIFIED, NUMERICAL_CHECK_PENDING |
| 8 (10) | 7.3.12 | Perforated/coupled wall and coupling-beam stiffness, strength and deformation must be represented | Critical core-wall openings/spandrels/FSAM and end connections must be independently verified | BASE_TEXT_VERIFIED, PROJECT_VALIDATION_PENDING |
| 5 (7) | 5.6.2 | Floor-diaphragm openings and collection of lateral loads require consideration | Existing opening gaps alone do not prove collector/chord transfer capacity | BASE_TEXT_VERIFIED, PROJECT_VALIDATION_PENDING |
| 9–12 (11–14) | 8.1.3 | Podium/backstay subclauses require particular configurations | Apply **only if** project geometry includes those physical systems; do not impose podium backstay rules on a standalone tower | CONDITIONAL_ONLY |

## Code selection decision table

| Question | Adopted rule |
|---|---|
| Which governs seismic hazard, load combinations and acceptance for Nepal? | NBC 105:2025 official DUDBC edition, and its current official amendments as verified. |
| When to use IS 16700? | Supplementary comparison / explicitly documented project tall-building procedure where relevant, with jurisdictional acceptance and verified amendment text. |
| Is IS 16700 Table 5 slab `Ig` automatically an approved factor for a conventional RC floor? | **No.** Verify actual slab structural type, the applicable code and section bending behavior; separately preserve membrane stiffness, thickness, unit weight and masses. |
| Does IS initial P-Delta replace a 1D+1L gravity benchmark or NBC seismic weight? | **No.** They serve different analysis purposes and should be separately tracked in manifests. |
| Does an 8/16 shell-mesh workbook establish actual load transfer? | **No.** Solve independently with same physical model and compare support/group reactions, vertical interface forces, beam actions and deformation. |
| Do citations validate the project nonlinear wall material? | **No.** Need actual reinforcement/axial-load geometry and component calibration against experimental histories, plus full model ZERO/X/Y/XY diagnostics. |

## Specific source hierarchy and update checklist

1. **Primary Nepal requirement:** [NBC 105:2025 official PDF](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf) and [DUDBC building-code index](https://dudbc.gov.np/pages/building-code/).
2. **Supplementary base text:** BIS IS 16700:2023 (first revision, September 2023; user-provided private copy).
3. **Must retrieve:** BIS **Amendment No. 1 (2025)** exact text, verify changed provisions before assigning current-compliance status. Never assert that Table 5/§7.2 are unchanged without evidence.
4. **Implementation reference:** [OpenSeesPy ShellMITC4](https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html), [OpenSees rigidDiaphragm](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html), [CSI ETABS Analysis Reference Manual](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf).
5. **Related project decisions:** [Model reference](../../docs/02_MODEL_NBC_REFERENCE_AND_VALIDATION.md), [source registry](../../docs/00_RESEARCH_REFERENCES.md), [model review](../../REVIEW_MAIN/00_MODEL/20261113_STAGE02_AREA_INTEGRATION_AND_SLAB_MESH_STUDY.md).
6. **Who/when:** Reference curator retrieves authentic amended text and dates; structural reviewer resolves applicability/conflicts and signs a dated calculation; software maintainer updates validation tests **only after** signed engineering decision. Unknown approval remains `NOT_VERIFIED`.

## Public security and evidence policy

The supplied study copy includes an access watermark with contact/network identifiers. **Do not commit the actual file, extracted first/last-page watermarks, private download URL credentials, local personal paths, or derivative screenshots** to public branches, PRs, CI artifacts or citation indexes. Commit only short independent paraphrases and official bibliographic links. No reproduction/redistribution authorization is inferred from being able to read a PDF.
