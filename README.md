> **Thesis knowledge base (what / when / why / how / where / which / who):** [Open the organized knowledge base](KNOWLEDGE_BASE/README.md) · [15 source-linked workflow cards](KNOWLEDGE_BASE/01_WORKFLOWS/WORKFLOW_CARDS.csv) · [folder ownership](KNOWLEDGE_BASE/02_REPOSITORY_STRUCTURE/README.md) · [UI speed and accuracy](KNOWLEDGE_BASE/03_UI_PERFORMANCE/README.md). Canonical launchers/source paths are preserved; no engineer signoff or NLTHA acceptance is inferred.\n\n**Start: [`01_WORKFLOW_START.py`](01_WORKFLOW_START.py)** · [`01.py` compatibility alias](01.py) · [Ordered programs](launchers/README.md) · [All Excel workbooks](excel/README.md) · [Publication decisions](docs/review/EXCEL_AND_LAUNCHER_PUBLICATION_DECISIONS.md)

> **Task-separated navigation (Phase 2):** [ETABS](01_ETABS/README.md) · [OpenSees](02_OPENSEES/README.md) · [Integration](03_INTEGRATION/README.md) · [Python](04_PYTHON/README.md) · [AI/Token saving](05_AI_TOKEN_SAVING/README.md) · [Research](06_RESEARCH/README.md) · [Thesis review](07_REVIEW_MAIN/README.md). [Python ownership and duplicate baseline](engineering/registry/INVENTORY_INTERPRETATION.md) · [Standalone benchmark scope](02_OPENSEES/README.md). The existing numerical launchers are **unchanged**; do not interpret a static inspection as ETABS/OpenSees solver validation.

> **ETABS–OpenSees Thesis — New beginner task navigation:** [Start with ETABS, OpenSees, integration, Python, AI token-saving and research](engineering/README_START_HERE.md). See [governance rules](engineering/rules/CORE_RULES.md), [module owners](engineering/registry/CANONICAL_MODULES.csv) and [migration status](engineering/migration/ORGANIZATION_PHASE_1.md). This organizational overlay preserves existing launchers and solver modules; ETABS-free standalone OpenSees remains a future, gated milestone.

> **2026-11-12 current thesis action plan:** [P0–P2 delivery workboard](docs/review/20261112_THESIS_DELIVERY_WORKBOARD.md) · [nonlinear readiness dashboard](docs/programs/02_NONLINEAR_READINESS_EVIDENCE_DASHBOARD.md) · [literature by use](LITERATURE/README.md). The readiness GUI detects the standard builder for inspection only; material references do not automatically qualify the project for NLTHA. No accepted full-model nonlinear result is claimed.

# ETABS to OpenSeesPy - NBC 105:2025 thesis research

**[00 — Ordered launchers](00_READ_FIRST_RUN_ORDER.md)** · **[Per-program manuals](docs/programs/00_PROGRAM_INDEX.md)** · **[Historical rename map](docs/00_WORK_ORDER_RENAME_MAP.md)** · **[Baseline handoff](START_HERE_V167.md)**

Use the [current launcher index](docs/programs/00_PROGRAM_INDEX.md) for all canonical entry points, including input synchronization, device benchmarks, motion audits and the evidence dashboard. Launcher numbers are stable navigation IDs; the [00-09 engineering dependency map](docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md) defines progression. Legacy aliases remain supported. Experimental sources and historical outputs keep their provenance names.

**Open blocker:** The full-building nonlinear time history still has an unresolved first-step transient failure; no complete validated NLTHA or certified optimum is claimed. The rename itself has not been validated by a native solver run.

[Research modeling basis](Research_Components/02_MODELLING_BASIS.md) · [Organization policy](docs/00_REPOSITORY_ORGANIZATION.md)


**V169 nonlinear diagnostic enhancement:** [21 — NLTHA triage](docs/programs/21_NLTHA_TRIAGE.md) generates isolated ZERO/X/Y/XY probes, validates accelerogram quality and records explicit full-record evidence gates. Existing first-step failure is not resolved.

## Research source documentation

- [Active component source guides](docs/source/00_SOURCE_GUIDE_INDEX.md)
- [Scientific reference and citation register](docs/00_RESEARCH_REFERENCES.md)
- [Thesis NLTHA acceptance gates](docs/00_THESIS_ACCEPTANCE_GATES.md)
- [Contributor / ChatGPT / Codex instructions](AGENTS.md)

This documentation does not certify native solver convergence or project-specific material calibration.

## Stage 01–06 NLTHA implementation (Nov 2026)

The exploratory runner now includes physical wall geometry preflight (stage 01), opt-in source-approved frame reinforcement mapping (02), declared wall opening occupancy checks (03), accepted-step FVD/BRB recorder demand channels (04), chronological full-duration evidence gates (05), and a fail-closed M0–M6 research comparison executable (06). See docs/programs/22_WALL_FAILURE_AUDIT.md through 27_M0_M6_OUTRIGGER_COMPARISON.md. These are engineering validation capabilities **not** a claim that the first-step X wall solver failure is resolved or that all seismic records and variants converged.


[Six-stage NLTHA implementation and validation guide](docs/00_NLTHA_SIX_STAGE_EXECUTION_GUIDE.md) covers executed code changes, source inputs and unsolved physical validation tasks.

## Historical version organization

Superseded root versioned reports, manifests and logs are stored under [archive/previous_versions](archive/previous_versions/README.md), grouped by filename family. Only the latest version in each family stays at root, except two older Python compatibility facades still consumed by the GUI. The archive manifest documents those exceptions and exact original hashes.


The [expanded visual material workbench](docs/programs/06_MATERIAL_DEVICE_VALIDATION_EXPANDED.md) retains V149 Concrete01/Steel02/FVD/BRB plots and adds Concrete02/ConcreteCM/SteelMPF/E-SFI panels plus full research catalog and calibration tools.

## Evidence-based nonlinear model readiness

The main ETABS workflow **OpenSees nonlinear readiness / calibration status** button opens the [model-bound readiness dashboard](docs/programs/02_NONLINEAR_READINESS_EVIDENCE_DASHBOARD.md) instead of a static nine-item warning. Evidence presence, reviewer sign-off and numerical validation are different categories; no automatic analysis approval is granted.


**2026-11 research update:** [Verified NBC 105:2025 NLTHA clauses, OpenSees implementation and recent research evidence](docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md). The new optional strict metadata precheck does not approve real model behavior or a completed earthquake analysis.


[Stage 32: NBC 105:2025 paired accelerogram spectrum scaling audit](docs/programs/32_NBC105_PAIR_SPECTRUM_AUDIT.md) screens actual records, computes separate X/Y spectral candidate factors, and selects the smaller when valid; this is research screening only.


**Bidirectional earthquake setup:** [NBC 105:2025 XY/YX, vertical-action scope and exact OpenSees acceleration scaling](docs/programs/33_NBC105_XY_YX_VERTICAL_AND_SCALE_GUIDE.md). Horizontal XY/YX inputs remain 3D structural NLTHA; §4.3 vertical triggers require separate documented review.


**Matched SeismoMatch waveform import:** already matched Acc(g) records use `scale=1.0` in OpenSees, with Path unit conversion `9.80665`. The source-header and source-hash audit prevents a second spectrum multiplier. This is NOT independent confirmation of original SeismoMatch component scale factors: see [input provenance guide](docs/source/components/nonlinear_time_history/seismomatch_audit.py.md).


[2026-11-04 SeismoMatch numeric source double-verification](docs/00_SEISMOMATCH_MATCHED_RECORDS_AUDIT_20261104.md): six original Library matched X records checked against thesis PGAs, one unresolved Gorkha mismatch, scale1.0 import and missing original component scaling logs documented.


## All eight SeismoMatch earthquake pairs verified at input-file level

The latest [16-component, eight-pair SeismoMatch record audit](docs/ground_motions/seismomatch_20261104/README.md) supersedes the preliminary six-X-component document. It includes matched sample intervals, PGAs, source SHA256 fingerprints, conditional 5%-damped response-spectrum discrepancy statistics, source processing anomalies, and NBC 105:2025 clause checks. See the [16-file register](docs/ground_motions/seismomatch_20261104/matched_component_register.csv) and [offline reproducible source verifier](tools/verify_matched_waveforms.py).

**No original or matched earthquake waveforms are committed.** The original SeismoMatch initial component scaling-factor logs remain unavailable. Matched files already in `Acc(g)` are imported with `scale=1.0` and a unit-conversion Path factor of `9.80665`, not a second spectral scale.


[Complete eight-pair SeismoMatch source verification runbook](docs/ground_motions/seismomatch_20261104/RUNBOOK.md) now covers both original PEER AT2 and matched SeismoMatch source fingerprints, safe parsing, explicit pair synchronization, output schema, OpenSees scaling and NBC 105 evidence gates.


### Two NBC105:2025 target spectra (RC shear-wall dual system)

Do not treat conditional Soil-C-only SeismoMatch PSA residuals as Soil-D validation. The target spectra are now separately generated under [Stage 34](docs/programs/34_NBC105_RC_DUAL_SOIL_C_D_TARGETS.md) from Eq 4.1(2) and the RC dual-system Table 5-2 (R_mu=3.5, Omega_u=1.4, Omega_s=1.2). Soil C and D must be reviewed as distinct analysis cases with separately assigned actual site category, Z/I and matched record set. The code intentionally refuses unreviewed extrapolation beyond 6 s.


## Soil C primary full NLTHA research workflow (2026-11-04)

**Start with the [Stage 35 complete NBC 105:2025 Soil C source and analysis runbook](docs/programs/35_SOIL_C_PRIMARY_NLTHA_RUNBOOK.md)**. All eight actual matched A/B earthquake pairs in Soil C are tracked by original uploaded SHA256 in [source register](docs/ground_motions/seismomatch_20261104/matched_component_register.csv); matches are **already spectral-matched Acc(g)**. Extra OpenSees spectrum scale is **1.0**, acceleration unit Path factor **9.80665** for kN-m-s. Run **both simultaneous XY and YX orientations** per pair, with full 3D model and a separate gravity/preload state. Six near-field and two far-field classifications follow study grouping and still need seismological source-distance evidence.

Use [Stage 35 preflight](35_SOIL_C_NLTHA_PREFLIGHT.py) to audit all 16 source hashes and modal input limits. Use [Stage 36 run-matrix generator](36_SOIL_C_NLTHA_RUN_MATRIX.py) to **plan**, not execute, 112 research configs (M0–M6 × ULS/SLS × eight earthquakes), 224 intended XY/YX transient analyses. [Stage 36 instructions](docs/programs/36_SOIL_C_M0_M6_RUN_MATRIX.md) and [absolute vs relative acceleration recorder documentation](docs/source/components/nonlinear_time_history/ground_acceleration.py.md) describe corresponding code and output schemas.

**Blocked/needs explicit review:** Gorkha export 322.94s versus 120s original; Loma Prieta one-sample A/B end difference; 0.05–6s matching interval versus verified current modal `sqrt(R_mu)*T1`; missing SeismoMatch original scaling factors (0.33..3 and paired lower rule), missing site Vs30, nonlinear RC core/opening/steel/device validation and unresolved X-direction first-step core-wall failure. All raw earthquake waveforms are intentionally kept out of this public repository.


**NLTHA JSON evidence schema (reference document, not launcher 37):** [All Soil C motion, OpenSees recorder, source review and M0–M6 aggregation JSON fields](docs/programs/37_SOIL_C_NLTHA_JSON_SCHEMA.md). This documents actual units, code clauses, reviewer/source-hash evidence and the difference between source preflight, numerical screen and design acceptance.


### RTFC AI engineering workflow

For new Codex, ChatGPT and GitHub coding tasks, use the [numbered RTFC (ROLE–TASK–FORMAT–CONSTRAINTS) prompt library](docs/rtfc/README.md). The [engineering change issue form](.github/ISSUE_TEMPLATE/engineering_rtfc.yml), [pull request checklist](.github/pull_request_template.md) and [AGENTS.md](AGENTS.md) keep engineering assumptions, source data, NBC clauses, tests and deliverables consistent. The templates organize review but never certify a nonlinear analysis.


## Engineering review and safe work-order navigation (2026-11)

Start with the [thesis engineering evidence and workflow review](docs/review/03_THESIS_REVIEW_2026_11_04.md) for the distinction between modal coverage, numerical screening and validated nonlinear response.

For the asymmetric high-rise RCC-core/damped-outrigger thesis, use [the active-source engineering review](docs/review/00_ACTIVE_CODE_ENGINEERING_REVIEW.md) and [canonical 00–09 verification order](docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md) instead of sorting the duplicate numbered legacy launchers. A [static source compilation and inventory utility](tools/audit_active_repository.py) inventories active code, symbol lines, SHA, syntax status, missing source guides and numbered alias collisions. It **does not** claim native solver convergence or a line-by-line semantic review of all archived files.


### P0 RCC core wall / nonlinear material source review

The [first-step wall orientation, opening geometry and material qualification review](docs/review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md) now tests E-SFI bottom-edge width versus vertical edge height in both assembled geometry and the model preflight. Production-labelled `THESIS_NLTHA` is explicitly **blocked** while the existing PEER-web/M30 research templates remain the active concrete/FSAM/Fe500 constitutive implementation, or while the user has no verified wall opening schedule. This protects against treating assumed materials and passing source geometry as calibrated project physics. The earlier X-only first-step wall failure remains unresolved; diagnostic probes and numerical experiments are still available.


### Software-error remediation

See [the current fix-and-open-issues register](docs/review/02_SOFTWARE_ERROR_REMEDIATION.md). Both active NLTHA response-history paths now reject nonfinite accepted recorder values before writing outputs, and time-step comparisons require matching source hashes and true finer accepted steps. Project-specific E-SFI wall instability and experimental reinforcement/material calibration remain P0 open issues, not CI-passing software bugs.



## 2026-11 ETABS EQX/EQY P-Delta case verification

The user's native ETABS v23 screenshot shows **EQX+ P Delta Initial** as Nonlinear Static, zero-initial-state, P-Delta, with 1.2 × (Self Weight, Floor Finish, Partition, Wall), 0.5 × Live and +1.5 × EQX. Its **EQX+ P-Delta** dependent Linear Static case uses the preceding nonlinear case's stiffness, **excludes its loads**, and applies EQX × 1.0. Native Y definitions, negative initial branches and response steps require separate extraction.

Start with [the detailed source-bound verification runbook](docs/review/ETABS_EQX_EQY_PDELTA_NATIVE_VALIDATION_RUNBOOK_20261109.md). The new read-only Spyder tool [`tools/ETABS_EQX_EQY_PDELTA_EXPORT.py`](tools/ETABS_EQX_EQY_PDELTA_EXPORT.py) captures saved native case names, all available base-reaction steps and story tables without running analysis or changing the EDB. An upload-ready ZIP contains source hashes and missing-table status. The [four-case input template](examples/EQ_PDelta_4Case_Input_TEMPLATE.json) intentionally leaves unverified results blank. The offline matrix compares signed raw base shear, recovered story shear, roof/master displacements and drift only with compatible source IDs, P-Delta tangent, eccentricity, case definitions and steps.

**Not yet verified:** corrected 32-support gravity reactions, independent full native EQX/EQY results, OpenSees equivalent tangent-state reuse, wall section-cut story shear, matched ULS/SLS stiffness and 5% eccentricity. Existing ESM story shear is an integrated assigned-force *input*, not verified internal section shear. No EQX/EQY results have been fabricated or seismic factors silently changed.
