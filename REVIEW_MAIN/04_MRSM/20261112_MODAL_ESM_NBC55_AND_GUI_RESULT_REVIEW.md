# 2026-11-12 ESM/MRSM saved evidence audit — source identity, NBC §5.5, file selection, GUI status

**Engineering acceptance: NOT ESTABLISHED.** Numerical ULS cases completed; one-state ULS comparison, native ETABS validation and source effective stiffness remain separate gates. This register does **not** modify any project EDB, original Excel, exported analysis data or user ZIPs.

## Evidence sources (private; NEVER upload original data to public repository)
- User-provided `ESM_Review_20261112_151459_984181_UPLOAD.zip`, `ESM_Review_20261112_152133_186491_UPLOAD.zip`, `ESM_Review_20261112_153212_183327_UPLOAD.zip`.
- User-provided `MRSM_Review_20261112_154626_734037_UPLOAD.zip`, `MRSM_Review_20261112_154741_343548_UPLOAD.zip`.
- Within latest ESM package: `OpenSees_Direct/NBC105_Rayleigh_Preliminary_V123.json`, `NBC105_ESM_Calculation_ULS_X+_E0_V111.json`, corresponding Y JSON and all-storey source data.
- Within latest MRSM package: `OpenSees_Direct/MRSM_ULS/MRSM_Results_V132.json`, `OpenSees_Direct/MRSM_Batch_Status_V151.json`, source model in `Source_Provenance/OpenSees_Complete_Model_Data_V118.json`; prior comparison `Comparisons/ETABS_Comparison_V148/Comparison_Source_Exclusions.json`.
- Governing original source: Government of Nepal, DUDBC, *NBC 105:2025 Seismic Design of Buildings in Nepal*, second revision, **printed pp.36–37**, §5.5.1.1/.2 and §5.5.3. https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf

## 1. Verified numerical evidence from original ZIP (independent file inspection)

| Item | X | Y | Status |
|---|---:|---:|---|
| 25-storey Rayleigh Σ Wi di² (kN·m²) | 627.9604838101 | 2638.0972296202 | JSON source read |
| 25-storey Rayleigh Σ Fi di (kN·m) | 166.2742007442 | 339.6951869133 | JSON source read |
| Rayleigh T (s), 2π√[ΣWi di² /(9.81 ΣFi di)] | 3.8985139079 | 5.5904409801 | Numerically consistent, physically unqualified |
| NBC adopted ULS ESM design T1 (s) | 1.9812808850 | 1.9219797767 | min(Rayleigh, 1.25 empirical) |
| ESM W (kN) | 284691.5561853357 | Same source ledger | Source case JSON |
| Source model SHA256 | 97def708661a10c165b6e0072b045ca7a0a82e13f021649bdb07c3a522a25f72 | same | Source_Provenance JSON hash consistent |
| ESM reference base shear (kN) | 25659.0463 | 26450.735 | Source case JSON/log |
| MRSM unscaled V (kN) | 22586.5843613 | 16748.1890576 | Saved modal response |
| MRSM force scale | 1.1360303910 | 1.5793191122 | Saved result; base shear matched reference |
| MRSM scaled V (kN) | 25659.0463 | 26450.735 | Force scaled, not drift scaled |
| Cumulative modal mass participation | 91.24498698% UX | 90.77458703% UY | 40 modes, program criterion numerically passed |
| Maximum ULS design edge drift ratio (worst ±e) | ~0.005088 | ~0.007460 | Saved model, numerical NBC limit 0.025 |
| Top elastic master displacement (m), E0 | 0.10539 | 0.15084 | CQC envelope |
| Top design master displacement (m), E0 | 0.36886 | 0.52795 | ×Rμ=3.5, §5.5.1 |

## 2. Important code and plot conclusions

1. NBC §5.5.1.1 explicitly requires ULS design horizontal displacement = **Rμ × computed ESM/MRSM horizontal displacement**. SLS §5.5.1.2 requires **computed elastic displacement without ductility amplification**. MRSM uses `amp=Rμ` for ULS and 1 for SLS; MRSM force-only `S` is **not** multiplied onto displacement/drift. This accords with the saved code and source report, subject to §7.5/6.5 interpretation, native input qualification and effective stiffness.
2. NBC §5.5.3 inter-storey ratio limits are ULS 0.025 and SLS 0.006 **using effective stiffness §3.4**. Saved numeric ratios do not establish structural acceptance. An ETABS default display is typically the unamplified solver displacement unless its display/service combination explicitly contains a design scale; never assume automatic multiplication. Compare **raw elastic with raw elastic**, and **NBC design with NBC design** after matching Rμ and limit state. Do NOT double-multiply if source already contains amplified displacement.
3. The saved MRSM JSON has both `elastic_drift_ratio` and `design_drift_ratio`. The GUI plot uses the latter, while `MRSM_Results_V134.xlsx` previously did not plainly show the underlying ULS ×Rμ. Added `NBC 5.5 Deflections` worksheet listing every floor/case raw and design master displacement, implied factor, elastic and design edge drift, limit and physical acceptance status.
4. `components/response_spectrum/reports.py::saved_cases` previously did recursive scanning that could include **duplicate MRSM_Results JSON copies from organized evidence**. Source plots showed a repeated rainbow of cases; this was not evidence of repeated independent runs. Reader now prefers canonical `MRSM_ULS/MRSM_Results_V132.json` and `MRSM_SLS/MRSM_Results_V132.json` and excludes copied packages; it deduplicates case/state/model SHA.
5. The screenshot opening `ETABS comparison` at 15:33 precedes the MRSM calculation at 15:40–15:46. Therefore the **older** `Comparison_Source_Exclusions.json` with `ZERO_SOURCE_MATCHED_ROWS` may reflect *time of creation*, not proof that post-analysis MRSM is missing. Re-open and refresh comparisons AFTER solver completion. The source ZIPs include the MRSM results; the independent native ETABS mapping is still missing.
6. `ETABS_Normalized_Input.csv` is a schema template **NOT** a populated ETABS response dataset. `OpenSees_Normalized.csv` and the generated `NBC105_ESM_Storey_Forces` CSVs are also **NOT** native ETABS CSV. `components/validation/etabs_comparison.py` now checks EDB SHA256/path, selected mapping and approval before preselecting `ETABS_API_Normalized.csv`. If the mapping is not verified, it clearly prompts for the one-time Direct ETABS API step; it does not fabricate a comparison.
7. In the ESM dialog, `Workbook adopted T1-X/Y` are **historical original Excel reference periods**, not current OpenSees Rayleigh results. The source photograph showed historical X=2.0385674s even though current NBC design adopted X=1.9812809s; **do not substitute that old X period into current OpenSees ULS/MRSM**. The older input selector opt-in is now disabled by default and labels it research only.
8. MRSM GUI has a per-case ledger and now also visible top-level READY / RUNNING / EXPORTING / EXPORTED / COMPLETED / FAILED / REVIEW REQUIRED status and indeterminate bar. It restores the saved completed-case count when reopened, but labels it numerical completion, not design acceptance.
9. ESM footer relabelled explicit complete ESM evidence ZIP export and verified comparison controls. All outputs remain copies; archive provenance is not native solver acceptance.

## 3. The 32/76/97 wall support question is NOT CLOSED

The observed MRSM run used **76 source-restrained model nodes** (`ETABS_SOURCE_SUPPORTS`), while an independent gravity diagnostic used **32** ETABS nodes with nonzero vertical reactions; **97** is an extended continuous-wall-base experiment. In a finite-element shell mesh, original *point objects* and generated *analysis nodes* are not one-to-one. ETABS local meshing can propagate boundary restraints to points on a meshed wall base. Comparing only the count of originally selected ETABS point objects to the full OpenSees mesh support count therefore does not identify the correct restraint model. A zero ETABS reaction is not proof of a free restraint DOF. Establish **six DOFs per native analysis node** from matching CSI export and test support reaction/edge translation, membrane/shear, rotational restraint, gravity and modes before modifying the MRSM production baseline. Preserve 32/76/97 as separate diagnostics; do not silently change 76 to 32.

## 4. Remaining engineering and software gates

- Physical **NBC Table 3-1 effective stiffness** wall EI/shear and frame stiffness versus currently gross in-plane elastic shells; native ETABS OAPI read-only comparison required.
- Nodal mass, gravity preload, source six-DOF supports and selected site Vs30 must match.
- ULS ESM for this asymmetric ~95m building is **comparison only** under NBC §3.2.1; verify qualifying dynamic method.
- Current evidence only shows **ULS** six MRSM cases; SLS design ratios cannot be claimed as already checked.
- Independent ETABS response must be exported with source SHA and approved mapping; match `MODAL`, `ESM`, `MRSM` case bases and mode shapes. Modal mass 90% and balanced base shear are necessary checks but not sufficient.
- CQC positive envelopes of displacement, drift and shear are **not a single simultaneously signed response state**. Physical torsion, floor-edge drift and case mapping need explicit matching.
- Windows ETABS v23 + OpenSees native full-size validation not executed in this chat. CI tests only check Python software correctness.

## 5. Source code modified (commits on main)

`components/validation/etabs_comparison.py` read-only evidence auto-select; `components/response_spectrum/reports.py` deduplication and §5.5 Excel; `components/response_spectrum/model_analysis.py` visible MRSM operation status; `components/equivalent_static/calculation_and_gui.py` historical workbook reference and export labels. Review these modules rather than changing original source EDB/XLSX.
