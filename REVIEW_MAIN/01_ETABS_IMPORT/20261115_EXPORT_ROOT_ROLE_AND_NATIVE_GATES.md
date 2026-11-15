# 2026-11-15 — Source-specific import/export and thesis brace role assessment

## Evidence source (user-supplied, **not publicly uploaded**)
User's 2026-11-15 GUI and Windows Explorer screenshots plus locally inspected `OpenSees_Complete_Export_Report_V118(2).json` and `Available_Inputs_And_Steps_V144(3).json`. Source paths are deliberately omitted. The report is factual input evidence, **not native ETABS validation**.

## Exact observed evidence
- Connected elastic assembly: `elastic_assembled=true`, `assembly_errors=[]`, **`analysis_ready=false` and `nonlinear_ready=false`**.
- Imported 1,312 frame objects represented by **3,862 assembled frame segments**, 725 source area objects represented by **10,400 shell mesh cells**, 25 diaphragm groups, 11,072 assembled nodes. Distinguish unique ETABS object IDs, preview topology tag and actual assembled solver tag.
- Configured analysis preload factors: Live 0.3, Roof Live 0.0; saved reported downward applied load **286,419.758231 kN**, not evidence that an independent 1.0D+1.0L native gravity comparison passed. With all other loads unchanged, changing a verified 48,000 kN unfactored Live assignment from 0.3 to 1.0 would add 33,600 kN; that is only a **conditional arithmetic comparison**.
- Gross beam self-weight policy `GROSS_SECTION_LENGTH`; 750 beams, gross weight **53,984.05488 kN** and a **potential** 8,652.444352 kN end-offset reduction `AUDIT_ONLY`. No automatic source geometry correction.
- Source supports **76** at baseline; 32 primary reaction-bearing support reference and 76/97 sensitivity require explicit separate boundary-condition and signed reaction validation.
- The nonlinear model config has `nonlinear_parameters_reviewed=false`, `nonlinear_materials_file=""`, `nonlinear_wall_fsam_tags={}`. Constitutive, confinement and reinforcement data are unqualified. 120 hinged-brace warnings mention end My/Mz release modeling and pending nonlinear hinge verification.

## Confirmed software/organization findings
1. The UI could advertise an assembled export as if matching stage entries and nonlinear analysis readiness were automatic. User-visible message now reports both independent readiness flags, source-comparison requirement and case identity gates.
2. `OpenSees_Workflow_V144.workflow_status` searched a legacy results root and selected export root but not canonical numbered stage trees. Present case artifacts under `04_MODAL` or `05_MRSM` could be reported as not discovered. The source is corrected; discovery remains candidate-only (not verified).
3. `OpenSees_Workflow_V144` previously wrote its large combined inventory to the export root. The new inventory writer uses unique names under `01_ETABS_EXPORT/00_MANIFEST/INPUT_READINESS/`.
4. ID lookup already displayed labels; it did not expose a `BR` family with distinct verified `CO` conventional core-wall-to-perimeter, `BT` perimeter belt and `CT` 25th-storey cap roles. New optional source-ID config, columns, and brace-review CSV make classifications inspectable. NO automatic role inference from story/geometry.
5. Large export root retains flat legacy files because multiple active readers still use them. New UI checkbox uses **existing SHA-verified copy-only mirror** after export/rebuild; it never moves/deletes/replaces the source and reports an explicit mirror hash conflict instead of falsely declaring export failure. Full flat-path writer/reader migration remains open. Existing `.processing.json` timing sidecars are excluded from copied source evidence.

## Nonlinear and code compliance blockers — NOT CLAIMED COMPLETED
- Shear wall: actual ETABS panel thickness, web/boundary bar grades/counts/ratios, confined/unconfined concrete and axial loads. `ConcreteCM + SteelMPF + FSAM` source-calibrated constitutive data and region-by-region tags; independent cyclic wall benchmark and mesh sensitivity, openings and coupling beams.
- RC beam/column: ETABS real bar schedules, covers/ties and cyclic stress–strain. No illustrative M35/Fe550 profile substitution. Member moment-curvature and cyclic checks.
- Outrigger device/brace: classify source ID -> main family + CO/BT/CT; explicitly distinguish normal bracing BR, FVD link and BRB device assignment. Each M0–M6 scenario source-verified. Device properties and tests or explicit scenario disabled, never synthetic calibration.
- Initial EQ P-Delta: signed X/Y ± with stated gravity factors and model SHA; independently validate carried-state dynamic excitation and no double counting; preserve NBC 105:2025 governance and specifically adopted IS 16700 supplementary initial case.
- Rayleigh modal and added viscous device damping: base modes, alphaM/betaK, 5% reference band where specified and independent device contribution, no unverified double damping.
- Exact gravity and seismic mass: story-by-story ETABS load/mass ledger, original 32 support reactions plus 76/97 sensitivity, member self-weight physical ownership once, ShellMITC4 load transfer, 04/08/16 meshes.
- Record pairs/ULS/SLS: original A/B checksums, dt, complete durations and XY/YX; Acc(g)->m/s² once with 9.80665; SeismoMatch scale logs, NBC §9.3.2 target and limits, gravity preload and full seven M0–M6 configurations.
- First-step X wall `110280` remains unresolved; no completed full NLTHA claim.

## Acceptance
- Software AST/CI and synthetic files: pending exact commit results.
- Actual ETABS EDB and Windows OAPI extraction rerun: **NOT_RUN**.
- Native OpenSees 25-storey modal/gravity/FSAM, P-Delta and paired NLTHA: **NOT_RUN**.
- ETABS/OpenSees parity, physical model acceptance and code compliance: **NOT_VERIFIED**.

Regression scope: `tests/test_export_workflow_roles.py`, `tests/test_id_audit_roles.py`, `tests/test_import01_audit_and_workflow.py`. Preserve all current original source/export files and verified numerical inputs.
