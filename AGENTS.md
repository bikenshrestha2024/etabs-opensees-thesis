# AGENTS.md — Nonlinear ETABS-to-OpenSeesPy thesis coding contract

## Environment
Windows; Spyder IDE; Python 3.12; conda-forge only. Keep source modules import-compatible and the 01–21 launchers usable. No external upload of sensitive ETABS exports or internal model datasets without permission.

## Primary seismic code and exceptional supplementary sources (user design-basis decision, 2026-11-13)

All seismic loads/combinations, seismic mass, ESM, MRSM, linear time history, nonlinear time history and acceptance checks **must be sourced to NBC 105:2025**. Do not silently import IS 16700 analysis rules. **Two project-adopted IS 16700:2023 values only:** the **COMPULSORY** EQ P-Delta initial cases `1.2 DL+0.5 IL±1.5 EL/WL` from §7.2(d), and the **REQUIRED** conventional RC slab flexural `0.25 Ig` strength / `0.35 Ig` serviceability from Table 5 (not wall or beam/column stiffness). IS may be cited for further checks where NBC is silent, strictly as `SUPPLEMENTARY_NOT_NBC`; the official 2025 BIS amendment still requires reconciliation. Read [the mandatory code-purpose matrix](KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md) before edits to any analysis method or load generator. **NBC 105:2025 §§8.1.1.3 / 9.3.1.3 require P-Delta**, with §8.1.1.2 / §9.3.1.2 requiring §5.2 gravity. Compute static initial EQ EL from NBC seismic coefficient; solve **IS 16700:2023 §7.2(d) signed X±/Y± initial cases** before P-Delta-enabled TH. The P-Delta-disabled zero-initial history is **diagnostic-only and not NBC compliant**. Do not carry held static seismic EL into a full dynamic earthquake without verified no-double-counting/state-transfer evidence. See [mandatory P-Delta review](REVIEW_MAIN/00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md). IS initial cases never replace NBC §3.6 load combinations, §5.2 seismic mass/gravity or time-history motion/spectrum requirements.

## Physical correctness
Model: nonlinear RCC beams, columns and RC core walls with openings, ordinary steel braces, possible BRBs and fluid viscous dampers, seven M0–M6 outrigger configurations, bidirectional motions and ULS/SLS.
Do not invent project reinforcement, axial load, cylinder strengths, damper parameters, seismic record pairing or material-test figures.
Record adopted kN–m–s model units, stress kN/m² and SI time step; 1 MPa = 1000 kN/m² only once. FVD Cd has fractional-exponent dimensions, not universally kN*s/m.
Distinguish nominal, experiment-reproduced and transferred values. Do not relabel smoke tests as calibration or short trials as completed NLTHA.

## Edit requirements
Read docs/00_RESEARCH_REFERENCES.md, docs/00_THESIS_ACCEPTANCE_GATES.md and the individual docs/source guide. Cross-check imports and runtime-generated path references before moving files.
Make the smallest reversible physical-code edit. Include a failing deterministic test, then report executed test evidence and known missing native checks. Never claim unseen tests passed.
Write module/function documentation on units, source DOI/paper section, assumptions, side effects, inputs and outputs only where the source actually supports them.
Catch native solver failure at case boundary, keep original traceback/failed time/stage, identify post-failure contaminated data and use a fresh domain for retries.
Keep ETABS source read-only; write analysis to isolated output folders. Never use stale preserved V156 runtime as if it were matching active V170 code.
Ensure GUI remains responsive and native modal analysis is cancellable at process level, not just Python flag.

## Priority
P0 resolve X-only wall step failure; verify core region reinforcement/confinement, wall openings, trace, FVD/BRB qualification, and case statuses.
P1 update source geometry/section/mass mapping, tests for dt, drift/torsion, energy and full-record outputs.
P2 clean package archive, replace silent exceptions, split oversized UI components, preserve historical results as immutable evidence.

## References
Use source IDs R01–R13 in docs/00_RESEARCH_REFERENCES.md and include original DOI/source in documentation. Do not cite a 2026 paper as if it was already calibrated in an older release.

## NBC 105:2025 research implementation contract (2026-11)

Before changing seismic analysis code read docs/00_NBC105_2025_NONLINEAR_RESEARCH_IMPLEMENTATION.md and the official NBC 105:2025 document (DUDBC). Main governing clauses are 9.3.1 (nonlinear 3D, gravity, P-Delta, torsion and hysteresis), 9.3.2 (motion pairs, C(T)/Omega_u target, lower of two component factors, 0.33–3, XY/YX swap, integration dt bound) and 9.3.3 (response evaluation), with interstory limits in 5.5.3. Clause 9.3.3.1 erroneously cites 5.6, which is accidental eccentricity. The published 9.3.3 response-aggregation text does not specify EXACTLY seven records: require documented professional code interpretation instead of assuming a rule.

Use components/nonlinear_time_history/nbc105_2025_audit.py and components/response_spectrum/nbc_pair_spectrum_audit.py for shared conditions; do not hard-code different limits in a launcher/GUI. Existing candidate_scale_factor calculates a mean spectral-ordinate scaling estimate; this is a diagnostic, not proof of compliant spectral matching. Never auto-approve an FVD, wall specimen or project rebar from a literature card. Preserve source hashes and native failed states, and run GitHub Actions on every relevant code change.

## Soil C primary NLTHA data invariants (2026-11-04)

The study has exactly 8 matched Soil-C horizontal earthquake pairs: 6 research-classified near-field (Gorkha, Landers, Northridge, Kobe, Kocaeli, Chi-Chi) and 2 far-field (Hector Mine, Loma Prieta), all input `Acc(g)`; do not relabel as Soil D. Read the Stage 35 and Stage 36 guides. The matched record's extra spectral multiplier in OpenSees is 1.0; Path acceleration units conversion 9.80665. Use original A/B source hashes to select the event, both XY/YX simultaneous orientations and full history. Do not infer original SeismoMatch scale from PGA ratio, use its session logs to review NBC 9.3.2.2. Enforce Gorkha 322.94s vs original 120s provenance and the one-sample Loma Prieta mismatch; no hidden trimming, zero padding, rematching or unlogged corrections. For eight pairs report NBC §9.3.3 average of complete accepted responses; failed/nonconverged data cannot enter accepted comparison. Current modal `T1/Tn90` verification is required; a selected 20th eigenperiod cannot be assumed to be Tn90. Use only correct project ETABS reinforcement, mass and actual core-wall geometry. Do not label elastic-wall exploratory output as full nonlinear wall verification. When changing UniformExcitation recorder logic, preserve BOTH relative and absolute acceleration fields and unit tests. Every new Python module must have an individual `docs/source/.../*.py.md` guide.


## RTFC task briefing (new AI changes)

Use [docs/rtfc/README.md](docs/rtfc/README.md) for concise **ROLE → TASK → FORMAT → CONSTRAINTS** prompts. Select a numbered prompt for the exact engineering task instead of pasting the entire repository or unrelated project memories. Preserve the hard invariants in this AGENTS file and the tested NBC/Soil C data rules. No RTFC prompt can waive source-validation or native solver checks.

## Active repository engineering review and naming safety

Read [physical engineering code-review register](docs/review/00_ACTIVE_CODE_ENGINEERING_REVIEW.md) and [canonical work order](docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md) before any structural physics or repository organization change. Do not use root filename sorting as a work order: old aliases duplicate several 01–21 prefixes. Run `python tools/audit_active_repository.py --output audit/active_inventory.json --fail-on-missing-canonical` before moving modules; preserve import stability and data provenance. Every line-level review report must distinguish *inspected source lines* from static AST symbol discovery; never claim a whole-repo line-by-line audit without an actual ledger for each file.

## Mandatory 3D E-SFI wall geometry/physics gate

Review [P0 RCC wall geometry/material source audit](docs/review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md) before changing `assembly.py`, `wall_diagnostics.py`, `wall_topology.py`, `research_building_materials.py` or NLTHA analysis intent. Four-node wall quads must have i→j horizontal fiber width and i→l vertical story height under the current mesh adapter; verify actual mesh, local axes and multiple wall opening positions from ETABS. Experimental PEER/nominal M30 FSAM materials remain diagnostic, not a production representation. Do not bypass the `THESIS_NLTHA` block with an approval boolean; implement and verify project-calibrated wall and frame materials and real source reinforcement first. Source SHA and material/build provenance are essential.

## Per-file semantic review ledger (Codex / ChatGPT)

Before claiming a codebase has been reviewed line-by-line, consult [the frozen Git baseline ledger](docs/review/ledger/README.md) and the [CSV review status for each active Python file](docs/review/ledger/REVIEW_LEDGER_BASELINE_20261104.csv). Mark only **actual inspected lines/functions** as reviewed; every other file remains `NOT_REVIEWED`. Automated AST inventories and passing tests do not qualify as semantic inspection. Preserve dated immutable review snapshots across releases; `python tools/validate_review_ledger.py` confirms the baseline Git blob inventory. PR #5 was merged on 2026-11-04 (merge commit 9f72cd54199dbcf3724b095d7f3bc2bbd29a82f9); do not duplicate its full-record comparison fixes. Read docs/review/ledger/CURRENT_HEAD_CHECKPOINT_20261104.md for the latest checkpoint. The baseline CSV is frozen at an older SHA, not a current-head review.

## New destination-repository governance (2026-11-10)
For the independent `etabs-opensees-thesis` repository, also follow [canonical cross-agent rules](engineering/rules/CORE_RULES.md), [engineering validation gates](engineering/rules/ENGINEERING_GATES.md), [module dependency boundaries](engineering/rules/MODULE_BOUNDARIES.md), [scientific provenance](engineering/rules/PROVENANCE.md), and [AI attribution](engineering/rules/AI_ATTRIBUTION.md). These supplement, and do not replace, the existing contract above, the `.agents` Codex skill, or the `.claude` Claude Code skill. Start from [beginner task navigation](engineering/README_START_HERE.md) and [canonical module registry](engineering/registry/CANONICAL_MODULES.csv). Before any new file or commit, search for existing functionality and check open pull requests. The OpenSees-independent solver is a migration goal, not a completed implementation.
