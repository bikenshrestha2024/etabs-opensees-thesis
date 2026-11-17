# S1–S7 thesis acceptance — source-linked register (17 November 2026)

**Basis:** official GitHub default branch at start of this review: `89301aa1eee33222717c614487810c13a4cccba3`; its untruncated Git tree listed **3,178 tracked blobs**. Prior exact-head automated inventory counted **579 active Python files** and approximately **4,416 generated function/method review units**, which are **review candidates, not semantic approvals**. Current source-level inspection/CI evidence: nine attested functions in `docs/review/ledger/semantic_review_attestations.csv`; no complete independent function-by-function review is demonstrated. Each source-file change must update affected exact Git blob attestations or the audit blocks.

**Purpose:** one navigational acceptance index, not a competing scanner or second result ledger. Use existing `tools/audit_repository_integrated.py`, `docs/review/ledger/`, and `REVIEW_MAIN/`; do not move, delete, or overwrite historical user/solver evidence. All quantities and statements below are attributed to the indicated source. CI passing is never equivalent to native model verification.

## Acceptance table — no automatic promotion

| Gate | Acceptance requirement | Current verified status | Independent evidence | Outstanding decisive evidence |
|---|---|---|---|---|
| S1 inventory | All tracked Git paths/blobs enumerated, `truncated=false`, versioned | **PASS metadata only** at specified base commit | Git recursive tree and existing integrated inventory | Refresh count/blob list after each merge, plus archive/duplicate provenance |
| S2 complete semantic review | Every active source function and module side effect has SHA, actual inspected line span, argument/return and error behavior, call-site graph, test and reviewer | **OPEN**; nine narrow source-inspected/tested attestations, **not** nine end-to-end full-module reviews | `docs/review/ledger/semantic_review_attestations.csv` | Finish all ~4,416 generated units, resolve dynamic imports/GUI callbacks and interface boundaries, independently attest findings |
| S3 software regression | Reproduce defect before changing implementation, pass affected tests and original unaffected tests on exact commit | **PASS targeted source tests only**; no Windows/native conclusion | PRs #102–#108, associated red/green CI logs; `.github/workflows/integrated-repository-audit.yml` | Full native Windows/ETABS/OpenSees integration, GUI plots/exports/reload, and remaining output migration |
| S4 ETABS–OpenSees physical equivalence | Identical source EDB, loads/masses, material stiffness, element connectivity, 6-DOF supports/constraints, wall-base force+moment integration, comparable displacements/member forces | **NOT VERIFIED** | `REVIEW_MAIN/01_GRAVITY/20261117_INDEPENDENT_REACTION_PARTITION_32_76_97.md` | Independent native ETABS analytical-joint source + native OpenSees runs with full support-force-and-moment transfer and shared physical cuts |
| S5 nonlinear wall convergence | Gravity-preloaded wall element passes verified ZERO/X/Y/XY single-step/full history tests with converged forces, finite stress/strain/tangent and timestep/algorithm sensitivity; materials independently qualified | **UNRESOLVED** | `docs/00_THESIS_ACCEPTANCE_GATES.md` and `REVIEW_MAIN/06_NONLINEAR_TH/` first-step evidence | Trace original wall element 110280 / 112778 back to AREA:354 / AREA:482, validate orientation/constitutive/local DOF and first failing accepted/attempted state; fix **reproduced** cause, rerun coupon/panel/connected-bay |
| S6 complete M0–M6 NLTHA | 7 variants × 8 motion pairs × 2 limit states × XY/YX = **224 full independent orientations**, exact record/model SHA, complete dt/time/energy/response checks | **NOT VERIFIED**; run-matrix configurations are NOT native solver completions | `components/nonlinear_time_history/soil_c_run_matrix.py`, `variant_comparison.py`, `full_record_gate.py` | 224 native outputs plus failure manifest, independent device/material validation, complete acceptance evaluation |
| S7 thesis conclusions | Independent NBC 105:2025 code clause review, site classification and record matching, experimental performance limits, engineering judgement and signed case-review decisions | **NOT VERIFIED** | `docs/00_THESIS_ACCEPTANCE_GATES.md`, `LITERATURE/` registers | Approved ground conditions, physical source parameters and independent peer review |

No single `PASS` in S1/S3 can automatically set S2/S4/S5/S6/S7. A positive text field in a JSON case summary is not physical validation.

## S4 — numbered engineering closure protocol (native Windows model)

1. Freeze the exact current **ETABS v23 EDB** and fresh OAPI/analysis-joint export with SHA-256; identify source load cases, 1.0D+1.0L combination, gravity state, rigid diaphragm and all boundary conditions. Do not require a stale Excel workbook for new model conversion.
2. Export the analytical joint mesh (not only ETABS drawing-object IDs): coordinates, global-to-local axes, all six restraint DOFs, MPC master/slave links, shell edges, nodes and wall opening connectivity, 1,367 frame-end offset references and all source loads.
3. Re-run the original 76-source-restraint interpretation as a **source parity candidate**, then the 32-restraint release and 97-point continuous-base models as separately labeled **boundary sensitivities**. Do not infer source equivalence just from a smaller 32-node point-react mismatch.
4. Compare complete nodal and physical-cuts **FX,FY,FZ,MX,MY,MZ** about the same origin, independent member end forces at physical faces, lateral/gravity displacements, masses and self-weight. Different accounting of point reactions versus ETABS analysis-joint transfer is not solved by force balancing.
5. Run unit loading benchmarks for ShellMITC4 slab-to-beam-to-column/wall transfer at 4×4, 8×8 and 16×16 meshes, including connected first storey and diaphragm; record force conservation and mesh sensitivity.
6. **Acceptance decision:** only after declared tolerances for each comparable quantity and expected mesh convergence are applied to **actual native runs**; engineering review must sign off changed assumptions and residual discrepancies.

**Measured workbook conflict, not root-cause proof:** ETABS 1.0D+1.0L total FZ `311,367.313600 kN` and OS sum `311,367.313880 kN` match globally, while the OS76 44 additional wall-connected nodes attract `104,463.013534 kN` (33.55%). The ETABS point-object ledger reports zero FZ there; no complete ETABS analytical-joint/MPC/cut-force evidence exists to establish why. This remains a blocking engineering discrepancy.

## S5 — independent nonlinear wall convergence experiments

- **W0 source proof:** original exported tags, node XYZ, Shell/FSAM/E-SFI orientation, element area and right-hand local axes; original constitutive values, source unit system, integration scheme, gravity preload and lateral/mass settings.
- **W1 one-element/coupon:** evaluate ConcreteCM, SteelMPF and actual wall material spring/smeared model stress/strain/tangent over prescribed finite strain and cyclic branches; record solver package/version, stress and tangent sign; keep M30/Fe500 parameter origin traceable.
- **W2 panel and connected bay:** with exact geometry, applied gravity and boundary DOF/coupling, reproduce small wall panel and one connected bay; compare force equilibrium, mesh refinement and pure zero-history.
- **W3 first-step event:** clean domain before ZERO/X/Y/XY, capture `t=0`, attempted `t=0.005`, last accepted state, all failed attempts, return codes, force/strain/tangent first nonfinite origin. Postfailure element nonfinite responses alone are **localization**, not a proven initiating material law.
- **W4 robust convergence:** compare numerical integration algorithms, tolerances and substepping with the *same physics*. Do not weaken material, bypass the wall or accept a partial duration as a fix. Qualify initial/committed tangent and Rayleigh damping energy as separate hypotheses.
- **W5 success evidence:** accepted full record with all finite numerical channels and independent panel/material validation; reproducible alternate solver and timestep sensitivity; documented failure cleanup; only then promote S5 beyond exploratory numerical screening.

## S6 — exact NLTHA release contract

For each `variant in M0..M6`, `limit_state in ULS/SLS`, `pair_id in eight selected records`, and `orientation in XY/YX`:
- Input manifest must carry immutable `model_sha256`, both ordered raw component SHA-256 values, their **orientation-invariant pair identity**, match/scaling provenance, units, `dt`, full record duration, correct excitation mapping, gravity/P-delta initial state and analysis settings.
- Run must capture all accepted timestamps, finite displacement/drift/acceleration/force/stress/device work; full duration and nonzero post-start steps; number of attempted/retried steps, solver residual, reasons for failure, and time-step convergence partner.
- Comparison must preserve input pair identity across XY/YX, across variants, and across coarse/fine reruns; separate ULS and SLS and distinguish full-duration numeric screening from *physical* model acceptance. No missing case may be ignored; source hash validation must use actual files, not only strings.
- Release outputs must include seven-variant performance and P0/M0 baseline comparisons **only for complete qualified histories**, an explicit failed-case register and governing response aggregation interpretation independently checked against NBC 105:2025.

## S3 additional source issue — nonlinear timestep metrics

`components/nonlinear_time_history/full_record_gate.py::compare_time_step_results` converted peak-response metrics with `float(...)` without rejecting Python boolean coercions, negative peak magnitudes or consistently wrapping missing/bad values. It also accepted boolean timestep sizes and relative-difference tolerances. This can falsely pass an acceptance tolerance or turn a malformed history into plausible demand data.

**RED evidence:** GitHub Actions [run 44090040187](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44090040187), test-only head `4f42586027faf816edca9aec4a8708d163e5207e`, `tests.verify_full_record_gate` failed with **5 failures and 1 error** for malformed metrics and bool evidence; syntax and source discovery passed.

**Fix:** reject booleans, negative peak-demand magnitudes, malformed metrics and boolean timestep/tolerance inputs. Test `test_timestep_rejects_boolean_and_negative_peak_demands` and `test_timestep_rejects_boolean_step_size_and_tolerance` must pass, plus affected source ledger blob-SHA reattestation. The first green regression run on source commit `290d96f455318871bcb05cdf55df233ed58fcd77` ran 226 focused tests successfully but **static audit blocked because the inspected source blob hash changed**. On the next branch commit, `docs/review/ledger/semantic_review_attestations.csv` was synchronised to the exact new blob. Only accept merge after the whole branch passes the integrated audit and other required checks; record the exact green run separately.

## Governance and folder rules

1. This source-of-truth register belongs under `REVIEW_MAIN/08_SOFTWARE_SECURITY`; gravity evidence remains `REVIEW_MAIN/01_GRAVITY`; wall/NLTHA evidence belongs in `REVIEW_MAIN/06_NONLINEAR_TH`. Existing `docs/review/ledger` owns symbol attestation, `tools/audit_repository_integrated.py` owns the automated candidate register. Do not create competing scanners.
2. Preserve `[ROOT]/01..07` working launchers, all active producer/consumer schemas, and archived version snapshots. Never move users' `.edb`, original material PDFs, private earthquake histories, raw EDB-derived workbooks, certificates or credentials into public GitHub.
3. Every correction requires reproducible failing input, root-cause explanation, smallest safe patch, regression, exactly pinned commit workflow, verified revert path and recorded unresolved questions.
4. Exact Git blob SHA-1 of reviewed source is **not** raw model or waveform SHA-256. A change to the reviewed source invalidates that attestation until a new source-level review and test reattestation occur.
5. Source metadata inventory and synthetic Python unit tests are not equivalent to native ETABS, native OpenSees, Windows UI, experimental qualification, or NBC compliance.
