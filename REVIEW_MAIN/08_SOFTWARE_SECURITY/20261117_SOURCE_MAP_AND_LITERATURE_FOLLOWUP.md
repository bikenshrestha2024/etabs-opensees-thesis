# 2026-11-17 — Current-head source-map defect, research-to-code matrix, and audit gate

## Scope and repeatability

Base GitHub `main`: `cedd203d9804dbe9b517e9ff8a15e6b32987ec52`. The fully recursive GitHub tree response was `truncated=false` with **3,173 tracked blobs**, **173 root files**, **190 components**, **232 tests**, **900 docs**, **143 REVIEW_MAIN**. These are Git tree metadata, not manual 3,173-file semantic review. This audit uses existing `tools/audit_repository_integrated.py`, `docs/review/ledger/semantic_review_attestations.csv`, and [issue #75](https://github.com/bikenshrestha2024/etabs-opensees-thesis/issues/75); no alternate scanner is introduced. The current CI-produced per-file symbol register and executed tests **must be retrieved from the exact branch commit** before advancing status.

## Confirmed source-level discrepancy: NLTHA source resolution

**ID:** P1-NLTHA-SRC-EMPTY-MAP. **Path:** `components/nonlinear_time_history/soil_c_run_matrix.py`, `create_configs()`.

Prior implementation used `sources = source_map or resolve_sources(matched_dir)`. Explicitly passing an empty `source_map={}` selected the private directory discovery path, disregarding the supplied authoritative mapping. The choice was silent and configuration generation could depend on an unintended local directory. For earthquake pair and SeismoMatch provenance, silent fallback is unacceptable.

**Narrow correction:** use directory resolution only if `source_map is None`; if a caller explicitly passes an empty mapping, raise `ValueError` before making any run output directory or writing 112 configurations. The normal default directory-resolution behavior and valid supplied 16-component mapping are unchanged. Regression: `tests/verify_soil_c_run_matrix.py::RunMatrixTests::test_explicit_empty_source_map_fails_closed_without_scanning_private_files` mocks directory discovery as a failure and verifies the output directory remains absent.

**Limits:** This fixes only the empty-override branch. It does **not** yet validate all supplied map entries' SHA, file presence, event/component exactness, missing `dt` or original matched record preprocessing provenance. The existing tests with synthetic source maps may legitimately use nonexistent paths; do not secretly enforce live waveform presence without first separating a test-only injection contract.

**Exact validation commands (require checkout of branch head):**

```bash
python -m unittest tests.verify_soil_c_run_matrix -v
python -m unittest tests.verify_soil_c_nltha_suite tests.verify_matched_waveform_register -v
python -m py_compile components/nonlinear_time_history/soil_c_run_matrix.py tests/verify_soil_c_run_matrix.py
python tools/audit_repository_integrated.py --repo . --output audit/integrated --fail-on-static-blockers
```

The patch and existence of test code are **not** evidence that those commands passed. Do not mark acceptance without CI/runner output on the exact revision and review of collateral failures.

## New and already uploaded research — relevance and actual implementation boundary

| Evidence | Current independent source | Highest-value project test | Prohibited shortcut |
|---|---|---|---|
| Charney (2008), unintended Rayleigh damping; OpenSees official `rayleigh` command | Uploaded Charney PDF; https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/rayleigh.html | Compare `alphaM`, `betaK`, `betaKInit`, `betaKcomm`, hinge damping force and energy under actual nonlinear model with correct element regions | No arbitrary universal damping coefficients; a successful zero-motion solve alone is not validation |
| Kurniawandy et al. (2026), irregular-plan FVD layouts | Uploaded 2026 article, DOI 10.1080/13467581.2026.2721849 | Equal-capacity, equal-count FVD layouts at asymmetric plan corners/perimeter, drift/torsion/device work | Never adopt its published percentage reductions as results of this 25-storey outrigger |
| Rathje et al. (1998) mean-period frequency content | Uploaded article | Raw/matched record station + component SHA, frequency content, `Tm` and spectrum compatibility and record-duration reconciliation | Frequency summaries cannot replace NBC spectrum matching or XY/YX source evidence |
| Menegotto & Pinto (1973), Kent–Park (1971), Mander (1988), Zendaoui et al. (2016), Neuenhofer & Filippou (1997) | User-uploaded originals; see `LITERATURE/2026-11-17_SECOND_UPLOADS_THESIS_USE_CASES.md` | Test Steel02 vs wall SteelMPF/FSAM material maps, confinement, force-/displacement-based frame convergence | Frame coupon does not reproduce 3D RC shear wall behavior |
| 2026 consistent SFI-MVLEM tangent research | University of Canterbury institutional report: https://ir.canterbury.ac.nz/items/c9d2c5f8-31a8-496b-8916-b4874623bb80 | Separate compiled OpenSees element binding and selected RC wall tangent/element finite response from code provenance | An institutional 2026 proposal is not proof that the new tangent exists in installed OpenSees |
| Sebaq et al., published Nov. 13, 2026, long-duration FVD demands | https://doi.org/10.1080/13467581.2026.2741457 | Cumulative damper energy, residual drift, history completeness, degradation and sustained response; duration-aware sensitivity | Peak drift-only optimization cannot be assumed to cover cumulative damage |
| 2026 irregular high-rise composite FVD placement | https://doi.org/10.1007/s10518-026-02428-6 | Placement-count/capacity control, roof acceleration and torsion comparison, high-rise applicability | Different composite structural system is not a direct material parameter source |
| 2026 side-core TVMD feasibility; 2026 H2 TVMD paper | https://www.jstage.jst.go.jp/article/aijs/91/840/91_270/_article/-char/en ; https://www.sciencedirect.com/science/article/pii/S2352710226002603 | Optional separately modeled inertance+tuning-spring mechanism and multimodal displacement/acceleration objectives | TVMD must not be represented as the baseline power-law FVD |

### Existing engineering blockers: test in order

1. **P0 physical source:** native ETABS object vs analysis-joint six-DOF restraints, first-storey mesh, 32/76/97 configurations, wall base cut force **and moment**, diaphragm, frame offsets, source SHA. Recorded equal total gravity `311367.3136 kN` is not local force equivalence.
2. **P0 numerical root cause:** first failed X-wall element around tag 110280 after gravity, finite mass/tangent/constitutive mapping, ZERO/X/Y/XY clean-domain experiments, last committed step and failure recovery. No changes to actual shell topology without reproduced cause.
3. **P0 device units:** verify `F=C|v|^alpha sign(v)`, units `[C]=kN/(m/s)^alpha` or `kN/(mm/s)^alpha` depending model, actual ETABS link data and nonlinear OpenSees `uniaxialMaterial Viscous`/device mapping with independent force/energy benchmark. Existing `700` cannot be rescaled without seeing physical native model definition.
4. **P1 method and computational accuracy:** matched source record hashes/units/dt/duration, Rayleigh energy and non-proportional damping, benchmark force-based integration, confinement and yielding.
5. **P1 thesis comparison:** only complete, source-verified XY and YX histories for M0–M6, with equal damper capacity/quantity and separately declared device-type variants, can be interpreted as outrigger performance.

## Acceptance (do not auto-promote)

- **G0** inventory tree enumeration **observed** on base SHA; exact checked-out Git index scan not rerun here.
- **G1** fix and regression **committed to review branch; tests not yet evidenced green**.
- **G2** cross-module import, security, output producer/reader, GUI and archives **not fully semantically reviewed**.
- **G3** native 32/76/97 local reactions and frame/wall physics **OPEN**.
- **G4** wall first-step and complete record M0–M6 **OPEN**.
- **G5** literature transfer and ground-motion match **REQUIRES MODEL-SPECIFIC TESTS**.
- **G6** main integration **BLOCKED until exact-commit CI + diff + source attestation review**.

**Privacy:** the supplied Library file and ChatGPT shared-conversation URLs could not be resolved through the interfaces available in this pass, so their contents cannot be claimed independently read. All user PDFs, confidential workbooks, 3D model and raw waveforms remain outside GitHub.
