# NBC 105:2025 — source coverage and engineering acceptance register

**Source of truth:** Uploaded NBC 105:2025 Second Revision, printed Clauses 1–10, pp.1–52, Annex A pp.53–80, Annex B pp.81–99 and Annex C p.100 onward. The index was drafted from the printed contents pp.xiv–xx and source section headings. Source index: [source_coverage_register.json](source_coverage_register.json).

## Critical status distinction

1. **Section heading present:** The auditor identifies an NBC subsection or table reference. It **does not** demonstrate that every normative provision within that subsection was enumerated.
2. **Requirement text reviewed:** A structural engineer independently checks each numbered equation, specification, exemption, table entry, footnote, figure and mandatory detailing requirement against the source PDF (including pages with equations embedded as images). This task remains **incomplete** outside the previously reviewed rule samples.
3. **Numerical function tested:** Independently hand-derived values and boundary, invalid-input, units and limits tests pass. Prior source table regressions cover Tables 3-1, 4-1, 5-1, 5-2, 6-1 and 10-1/2/3; these are not exhaustive of all normative clauses.
4. **Production integration verified:** All ETABS/OpenSees/Excel/UI call sites use the canonical clause implementation, have baseline/output parity and tests that fail if a duplicate calculation is reintroduced. The identified active ESM, MRSM, linear/nonlinear history and drift paths have been routed, but the **entire codebase has not been exhaustively audited**.
5. **Native engineering verified:** The exact 95 m asymmetric EDB and matched OpenSees/XARA model are run with logged mass, constraints, stiffness, P-Delta, modal data, Rayleigh force/displacement, RC/steel detailing and all motion case results. This evidence is not supplied or validated on the current public repository.
6. **Professional design acceptance:** An appropriately qualified structural engineer verifies, signs and records all design checks, selected system applicability, dual-system 25% requirement where applicable, component/connection detailing and deviations. This cannot be conferred by a chat response or a green GitHub Action.

## Sentence-level register (added 2026-11-21)

The [normative register](NORMATIVE_REGISTER_GUIDE.md) now enumerates 1417 normative units (Clauses 1-10, Annexes A-C) with one disposition each: 353 IMPLEMENTED_AND_TESTED, 7 IMPLEMENTED_UNTESTED, 307 MANUAL_PROJECT_CHECK, 180 PROJECT_NOT_APPLICABLE, 559 DEFINITION_ONLY, 11 EXTERNAL_DATA_REQUIRED, 0 UNVERIFIED_GAP, 0 unreviewed. Its gate (`python -m components.nbc105 --audit`) reports REGISTER_REVIEWED_EXTERNAL_GATES_OPEN and never certifies. The standard is **not certified**. External gates that remain open: independent human sign-off, native ETABS/OpenSees evidence, project wall and connection designs (Annex A RC detailing, Annex C Table C-1 transcription).

## Mandatory gap groups

| Group | Mandatory remaining review |
|---|---|
| 1–2 | Definitions, scope, life safety, damage limitation, performance evidence, simplicity, foundation/SSI, capacity design and stability |
| 3 | Every LSM/WSM load combination incl. vertical and non-parallel, cracked stiffness and actual ETABS case loading |
| 4 | Vs30 / soil-class verification, site-specific hazard, Annex C Z lookup, Table 4-4 footnote and spectrum point-by-point parity |
| 5 | Source-bound Rayleigh COM displacement with torsion excluded, exact wall geometry and openings, dual-system structural qualification, all irregularity/drift checks |
| 6 | Complete ULS/SLS floor-force distribution, eccentric application, base reactions, P-Delta case semantics, ETABS/Excel parity |
| 7 | Ritz/eigen mass above 90% each horizontal direction, true CQC grouped-mode logic, high-frequency missing mass, unscaled drift and displacement preservation |
| 8 | 3D linear time histories, consistent gravity and nonlinear-free assumptions, records and duration, group response aggregation |
| 9 | N2 target plus-sign/minus-sign pushover, realistic hysteretic RC wall/steel/damper models, complete support ground motion integration, converged 224 full-duration NLTHA cases |
| 10 | Table 10-1 dynamic component amplification, Tables 10-2/10-3, positive anchorages, shutoff, hanging safety cables, panels/ceilings and equipment inventory |
| Annex A | RC beams, columns, beam-column joints, confined boundaries, coupled shear walls and real first-storey openings, seismic shear and flexural capacity, reinforcement anchorage and splice schedules |
| Annex B | Steel/braced-frame systems, seismic links, link rotations, web stiffeners, end connections and material qualification for actual outrigger/belt members |
| Annex C | **All rows** of official municipality-specific Table C-1, correct municipality/ward matching, zoning factor and source edition |

## Current numerical model evidence

The previously supplied V10.7 acceptance report recorded `PERIOD_RS_MATCH_PASS__NOT_FULL_CODE_COMPLIANCE` and `AMPLIFIED_EMPIRICAL_ONLY__NO_ANALYTICAL_PERIOD_CHECK`, with no independently validated native ETABS/OpenSees equivalence. The supported conclusion is a *reported RS base-shear numerical match*—not a code-compliant Rayleigh period, complete structural design or nonlinear acceptance.

In particular, the user’s 12 m gross X-direction wall envelope is a geometric interpretation; actual RC wall openings, coupling action, boundary elements, reinforcement and shear/flexure demand require **Annex A §§5.1–5.9** design evidence, not merely gross and net area arithmetic.

## How to run

```powershell
python -m components.nbc105 --audit
python -m pytest tests/test_nbc105_full_source_coverage_gate.py -q
python -m components.nbc105.acceptance "V107_ACCEPTANCE.json"
```

The first command deliberately exits 2 and reports all open source/engineering gates. A green software CI does **not** change this answer. Keep sensitive source EDB, accelerograms, reinforcement schedules and result spreadsheets local; commit only redacted test provenance, code and abstract metrics.

## Definition of 'exhaustive acceptance'

Only after **every normative sentence** of Clauses 1–10 and Annexes A/B/C has a verified source/evidence row, relevant canonical production code/units have passed independent parity tests, and the native complete model and member/detailing calculations have been verified and signed off, can a reviewer consider a full engineering approval. This current register does not make that claim.

## Local Annex reference calculations

Independent Annex A and Annex B Python modules have now been wired to the same local dispatcher, CLI and NBC settings GUI as Clauses 1–10 without merging their authority into a different clause. They evaluate specifically source-derived RC shear-wall minima/boundary triggers/coupling-beam diagonal requirements and steel eccentric-brace I-section seismic-link rotational limits. They **do not** certify full Annex detailing, steel outriggers/FVD compatibility, full wall design or any structural member capacity. Annex C full zoning dataset remains open. See `tests/test_nbc105_annex_dispatch.py` and `tests/test_nbc105_annex_ab_source_checks.py`.

## New focused source detail evidence

Annex A §5.6 now includes explicit opening replacement-reinforcement and critical-shear-plane checklist logic; this particularly matters for the project’s 12 m gross X-wall envelopes with two voids. Annex B §7.1.1 now requires an **explicit I-section seismic-link designation** before the §7.1.4 rotation limit can be calculated, preventing false application to SHS outriggers/FVD links. Source-based checks still require independent ETABS demand/capacity and actual reinforcement or connection drawings before approval.
